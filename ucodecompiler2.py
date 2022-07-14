#!/usr/bin/env python3

import functools
import io
from pathlib import Path
import sys
from typing import List, Optional

import hy

import aurora
from ucode_tools import iterate_uprogs


S = hy.models.Symbol
AUTO = S("auto")


ucode_rom = []
ucode_lut = {}


def make_uins(**kwargs):
    kwargs_str = {key: str(value) if isinstance(value, hy.models.Symbol) else value for key, value in kwargs.items()}

    kwargs_resolved = {key: getattr(aurora, value) if isinstance(value, str) else value for key, value in kwargs_str.items()}
    aurora.Ui(**kwargs_resolved)     # ensure that it's valid

    return "Ui(" + ", ".join(f'{key}={value_pyexpr}' for key, value_pyexpr in kwargs_str.items()) + ")"


def process_opcode(ucode_rom, ucode_lut, mnemonic, *uprog_model, opcode_expr=None, s_mode=0):
    # print("OPCODE:", mnemonic, uprog_model)

    def make(s):
        uprog = []

        def emit(x):
            uprog.append(x)

        for i, uins in enumerate(uprog_model):
            # terminate u-program
            if i == len(uprog_model) - 1:
                if not isinstance(uins, list):
                    uins = [uins]
                
                uins.append("Ui(last=True)")

            # convert to string
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

    def define_uprog(masked_opcode_str, uprog):
        start = len(ucode_rom)
        ucode_rom.extend(uprog)
        ucode_lut[masked_opcode_str] = (start, len(uprog))


    if mnemonic.endswith("2"):
        mnemonic = mnemonic[:-1]
        s_mode = 1

    if s_mode in {0, AUTO}:
        uprog = make(s=False)

        if opcode_expr:
            define_uprog(hy.disassemble(opcode_expr, codegen=True).strip(), uprog)
        else:
            define_uprog(f"OP_{mnemonic}", uprog)

    if s_mode in {1, AUTO}:
        uprog = make(s=True)

        if opcode_expr:
            define_uprog(hy.disassemble(opcode_expr, codegen=True).strip(), uprog)
        else:
            define_uprog(f"OP_{mnemonic} | OMODE_S", uprog)

    if s_mode not in {0, 1, AUTO}:
        raise Exception("what do you think you are doing?")


with open(sys.argv[1], "rt") as f:
    hycode = hy.read_many(f, filename=sys.argv[1])

    localz = {}
    localz["opcode"] = functools.partial(process_opcode, ucode_rom, ucode_lut)
    localz["uins"] = make_uins

    for sym in dir(aurora):
        if sym.startswith("UI_"):
            # just inject them as strings in final form. this could be done in a more structured/typesafe way
            localz[sym.removeprefix("UI_").lower()] = sym

    hy.eval(hycode, locals=localz)

"""
ucode generated; now compress it

- iterate over uprogs
- (it is each uprog's own responsibility to be properly terminated)
- insert into suffix tree & make LUT point to head
"""

from dataclasses import dataclass, field

@dataclass
class SuffixTreeNode:
    suffix: Optional["SuffixTreeNode"]
    prefixes: List["SuffixTreeNode"] = field(default_factory=dict)

    def get_or_insert_prefix(self, uins: aurora.AuroraUins) -> "SuffixTreeNode":
        if uins not in self.prefixes:
            self.prefixes[uins] = SuffixTreeNode(suffix=self)

        return self.prefixes[uins]


root = SuffixTreeNode(suffix=None)

new_lut = {}

for opcode, uprog in iterate_uprogs(ucode_lut, ucode_rom):
    head = root

    for uaddr, uins in reversed(list(uprog)):
        head = head.get_or_insert_prefix(uins)

    new_lut[opcode] = head


def visualize(root):
    import graphviz

    dot = graphviz.Digraph('ucode',
                        graph_attr={'rankdir': 'LR', 'ranksep': '0', 'nodesep': '0.05'},
                        node_attr={'fontname': 'Cascadia Code', 'shape': 'plaintext'}
                        )
    sub = graphviz.Digraph(graph_attr={"rank": "same"})
    term = graphviz.Digraph(graph_attr={"rank": "same"})

    id_next = [0]

    def make_id():
        id = str(id_next[0])
        id_next[0] += 1
        return id

    def makeit(head, uins):
        id = make_id()

        title = uins.replace(" | Ui(last=True)", "")\
            .replace("UI_", "")\
            .replace("Ui(", "")\
            .replace(")", "")\
            .replace(",", "|")

        if id != "0":
            dest = term if head.suffix is root else dot
            dest.node(id, title, shape="record" if title else "point")

        for uins, prefix in head.prefixes.items():
            newid = makeit(prefix, uins)
            if id != "0":
                dot.edge(newid, id)

        for lut_key, opcode_head in new_lut.items():
            if opcode_head is head:
                newid = make_id()

                sub.node(newid, lut_key, rank="min", shape="cds", color="white", style="filled", fillcolor="lightgrey")
                dot.edge(newid, id)

        return id

    makeit(root, "")

    dot.subgraph(sub)
    dot.subgraph(term)

    # https://dreampuf.github.io/GraphvizOnline/
    with open(Path(sys.argv[1]).with_suffix(".dot"), "wt") as dotf:
        dotf.write(dot.source)


visualize(root)


with open(sys.argv[2], "wt") as out:
    out.write("""# GENERATED CODE, DO NOT EDIT BY HAND

from aurora import *
from uxn_isa import *

UCODE_ROM = [\n""")

    for uins in ucode_rom:
        out.write(f"    {uins},\n")

    out.write("]\n")
    out.write(f"# {len(ucode_rom)} uins total\n\n")

    out.write("UCODE_LUT = {\n")

    for k, (start, length) in ucode_lut.items():
        out.write(f"    {k + ':':28s}({start:3}, {length:2}),\n")

    out.write("}\n")
