#!/usr/bin/env python3

from aurora import *
from ucode_au20 import UCODE_LUT, UCODE_ROM
from ucode_tools import iterate_uprogs

from uxn_isa import opcode_to_mnemonic, OMODE_S

rows = []

for opcode, uprog in iterate_uprogs(UCODE_LUT, UCODE_ROM):
    if (opcode & 0x9f) == 0x00:
        # where BRK would be in the LUT, we have LIT (FIXME?)
        opcode ^= 0x80

    if opcode == OP_ZZ_STKTRAP:
        title = ".STKTRAP"
    elif opcode == OP_ZZ_UNIMPL:
        title = ".UNIMPL"
    else:
        mnemonic = opcode_to_mnemonic(opcode)
        title = f"{opcode:02X}h&ensp;{mnemonic}"

    heading = [title, "ALU", "Mem", "PC", "Reg", "Stack", "Stall"]
    rows.append(heading)

    for uaddr, uins in uprog:
        row = [f"{uaddr:03X}h"]

        # ALU
        if uins.alu_op != ALU_OP_X:
            op = alu_op_str[uins.alu_op]
            sel0 = alu_sel0_str[uins.alu_sel0]
            sel1 = alu_sel1_str[uins.alu_sel1]
            row.append(f"{op}({sel0}, {sel1})")
        else:
            row.append("")

        # MEM
        if uins.mem_op != MEM_NOP:
            row.append(mem_sp_str[uins.mem_sp] + ":" + mem_op_str[uins.mem_op])
        else:
            row.append("")

        # PC
        if uins.pc_op != PC_NOP:
            row.append(pc_op_str[uins.pc_op])
        else:
            row.append("")

        # Reg
        rl = []
        if uins.reg_al_wr: rl.append("AL")
        if uins.reg_bl_wr: rl.append("BL")
        if uins.reg_cl_wr: rl.append("CL")

        if rl:
            rl += ["<=", "low(" + reg_in_sel_str[uins.reg_in_sel] + ")"]

        rh = []
        if uins.reg_ah_wr: rh.append("AH")
        if uins.reg_bh_wr: rh.append("BH")
        if uins.reg_ch_wr: rh.append("CH")

        if rh:
            what = {
                REG_H_MIRROR:   "low(" + reg_in_sel_str[uins.reg_in_sel] + ")",
                REG_H_ZERO:     "00",
                REG_H_SIGN:     "sign(" + reg_in_sel_str[uins.reg_in_sel] + ")",
                REG_H_ALU_H:    "ALU_H",
                REG_H_H:        "high(" + reg_in_sel_str[uins.reg_in_sel] + ")" + (
                    " = 0" if uins.reg_in_sel == REG_IN_WST and uins.stk_sz == STK_SZ_S and (opcode & OMODE_S) == 0 else ""),
            }
            rh += ["<=", what[uins.reg_h_mode]]

        rw = []
        if rh: rw.append(" ".join(rh))
        if rl: rw.append(" ".join(rl))
        # row.append("&ensp;&bull;&ensp;".join(rw))
        row.append("<br>".join(rw))

        # Stack
        if uins.stk_op == STK_PUSH:
            in_ = stk_in_str[uins.stk_in_sel]
            sz_str = {
                STK_SZ_8L: ".8 lo(" + in_ + ")",
                STK_SZ_8H: ".8 hi(" + in_ + ")",
                STK_SZ_16: ".16 " + in_,
                STK_SZ_S: ".s " + in_,
            }
            row.append(stk_sel_str[uins.stk_sel] + " push" + sz_str[uins.stk_sz])
        elif uins.stk_op == STK_POP:
            sz_str = {
                STK_SZ_8L: ".8",
                STK_SZ_8H: ".8",
                STK_SZ_16: ".16",
                STK_SZ_S: ".s",
            }

            row.append(stk_sel_str[uins.stk_sel] + " pop" + sz_str[uins.stk_sz])
        else:
            assert uins.stk_op == STK_NOP
            row.append("")

        if uins.reg_in_sel == REG_IN_MEM:
            row.append("memory-load")
        else:
            row.append("")

        rows.append(row)

    rows.append([])

with open("ucode_au20.html", "wt") as f:
    f.write("<style>body, table { font-family: monospace } td, th { border-bottom: 1px solid #ccc; padding: 2px 1em; text-align: left } "
            "th { border-top: 2px solid #ccc; font-size: 12pt;  } "
            "th:not(:first-child) { color: #999 }</style>\n")
    f.write("<h2>Aurora-20 microcode listing</h2>\n")
    f.write('<table cellspacing="0">\n')
    for row in rows:
        f.write("<tr>")
        for cell in row:
            if len(row[0]) > 4:     # terrible terrible
                f.write('<th>' + cell + "</th>")
            else:
                f.write('<td>' + cell + "</td>")
        # if not row:
        #     f.write("<td colspan=\"8\">&nbsp;</td>")
        f.write("</tr>\n")
