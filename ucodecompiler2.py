#!/usr/bin/env python3

import io
import sys

import hy

import aurora


S = hy.models.Symbol
AUTO = S("auto")


out = io.StringIO()


def make_uins(**kwargs):
    kwargs_str = {key: str(value) for key, value in kwargs.items()}

    kwargs_resolved = {key: getattr(aurora, value) for key, value in kwargs_str.items()}
    aurora.Ui(**kwargs_resolved)     # ensure that it's valid

    return "Ui(" + ", ".join(f'{key}={value_pyexpr}' for key, value_pyexpr in kwargs_str.items()) + ")"


def process_opcode(mnemonic, *uprog_model, s_mode=0):
    # print("OPCODE:", mnemonic, uprog_model)

    def make(s):
        uprog = []

        def emit(x):
            uprog.append(x)

        for uins in uprog_model:
            if isinstance(uins, list):
                emit(" | ".join(uins))
            else:
                assert isinstance(uins, str)        # string or hy.models.Symbol

                uins_mnemonic = str(uins)

                if uins_mnemonic.startswith("UI_") or uins_mnemonic.startswith("Ui("):
                    emit(uins_mnemonic)
                else:
                    raise Exception(f"Unhandled: {uins}")

        return uprog

    if mnemonic.endswith("2"):
        mnemonic = mnemonic[:-1]
        s_mode = 1

    if s_mode in {0, AUTO}:
        uprog = make(s=False)

        out.write(f"    (OP_{mnemonic} & 0x1f): [\n")
        for uins in uprog:
            out.write(f"        {uins},\n")
        out.write(f"    ],\n")

    if s_mode in {1, AUTO}:
        uprog = make(s=True)

        out.write(f"    (OP_{mnemonic} & 0x1f) | OMODE_S: [\n")
        for uins in uprog:
            out.write(f"        {uins},\n")
        out.write(f"    ],\n")

    if s_mode not in {0, 1, AUTO}:
        raise Exception("what do you think you are doing?")


out.write("""# GENERATED CODE, DO NOT EDIT BY HAND

from aurora import *
from uxn_isa import *

UCODE = {\n""")

with open(sys.argv[1], "rt") as f:
    hycode = hy.read_many(f, filename=sys.argv[1])

    localz = {}
    localz["opcode"] = process_opcode
    localz["uins"] = make_uins

    for sym in dir(aurora):
        if sym.startswith("UI_"):
            # just inject them as strings in final form. this could be done in a more structured/typesafe way
            localz[sym.removeprefix("UI_").lower()] = sym

    hy.eval(hycode, locals=localz)

out.write("}\n")

with open(sys.argv[2], "wt") as f:
    out.seek(0)
    f.write(out.read())
