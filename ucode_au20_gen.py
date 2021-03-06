# GENERATED CODE, DO NOT EDIT BY HAND

from aurora import *
from uxn_isa import *

UCODE_ROM = [
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_ADD),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_ADD),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_AND),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_AND),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_A_U8,
    UI_POP_BS,
    Ui(mem_op=MEM_ST_BL_AT_A, mem_sp=MEM_SP_DEV) | Ui(last=True),
    UI_POP_A_U8,
    UI_POP_BS | UI_ALU_A_PLUS_1,
    Ui(mem_op=MEM_ST_BH_AT_A, mem_sp=MEM_SP_DEV) | UI_ALU_TO_A,
    Ui(mem_op=MEM_ST_BL_AT_A, mem_sp=MEM_SP_DEV) | Ui(last=True),
    UI_POP_A_U8,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_DEV),
    UI_MEM_TO_BL,
    UI_PUSH_BS | Ui(last=True),
    UI_POP_A_U8,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_DEV),
    UI_MEM_TO_BH | UI_ALU_A_PLUS_1,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_DEV),
    UI_MEM_TO_BL,
    UI_PUSH_BS | Ui(last=True),
    UI_RPUSH_PC_W,
    Ui(pc_op=PC_WARP_UVEC) | Ui(last=True),
    UI_RPUSH_PC_W,
    Ui(pc_op=PC_WARP_UVEC) | Ui(last=True),
    UI_POP_AS,
    UI_PUSH_AS,
    UI_PUSH_AS | Ui(last=True),
    UI_POP_AS,
    UI_PUSH_AS,
    UI_PUSH_AS | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_EOR),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_EOR),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_EQU),
    UI_PUSH_ALU_L | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_EQU),
    UI_PUSH_ALU_L | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_GTH),
    UI_PUSH_ALU_L | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_GTH),
    UI_PUSH_ALU_L | Ui(last=True),
    UI_POP_AS,
    UI_ALU_A_PLUS_1,
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_AS,
    UI_ALU_A_PLUS_1,
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_A_S8,
    UI_POP_BS | UI_ALU_PC_PLUS_A,
    Ui(pc_op=PC_WARP_ALU_IF_BL_NONZERO) | Ui(last=True),
    UI_POP_AS,
    UI_POP_B_U8 | Ui(alu_op=ALU_OP_PASS_OP0, alu_sel0=ALU_SEL0_A, alu_sel1=ALU_SEL1_X),
    Ui(pc_op=PC_WARP_ALU_IF_BL_NONZERO) | Ui(last=True),
    UI_POP_A_S8,
    UI_ALU_PC_PLUS_A,
    Ui(pc_op=PC_WARP_ALU) | Ui(last=True),
    UI_POP_AS,
    Ui(alu_op=ALU_OP_PASS_OP0, alu_sel0=ALU_SEL0_A, alu_sel1=ALU_SEL1_X),
    Ui(pc_op=PC_WARP_ALU) | Ui(last=True),
    UI_POP_A_S8,
    UI_RPUSH_PC_W,
    UI_ALU_PC_PLUS_A,
    Ui(pc_op=PC_WARP_ALU) | Ui(last=True),
    UI_POP_AS,
    UI_RPUSH_PC_W,
    Ui(alu_op=ALU_OP_PASS_OP0, alu_sel0=ALU_SEL0_A, alu_sel1=ALU_SEL1_X),
    Ui(pc_op=PC_WARP_ALU) | Ui(last=True),
    UI_POP_AW,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_RAM),
    UI_MEM_TO_BL,
    UI_PUSH_BS | Ui(last=True),
    UI_POP_AW,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_RAM),
    UI_MEM_TO_BH | UI_ALU_A_PLUS_1,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_RAM),
    UI_MEM_TO_BL,
    UI_PUSH_BS | Ui(last=True),
    UI_POP_A_S8,
    UI_ALU_PC_PLUS_A,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_RAM),
    UI_MEM_TO_BL,
    UI_PUSH_BS | Ui(last=True),
    UI_POP_A_S8,
    UI_ALU_PC_PLUS_A,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_RAM),
    UI_MEM_TO_BH | UI_ALU_A_PLUS_1,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_RAM),
    UI_MEM_TO_BL,
    UI_PUSH_BS | Ui(last=True),
    UI_POP_A_U8,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_RAM),
    UI_MEM_TO_BL,
    UI_PUSH_BS | Ui(last=True),
    UI_POP_A_U8,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_RAM),
    UI_MEM_TO_BH | UI_ALU_A_PLUS_1,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_RAM),
    UI_MEM_TO_BL,
    UI_PUSH_BS | Ui(last=True),
    Ui(mem_op=MEM_LD_AT_PC, mem_sp=MEM_SP_RAM) | Ui(pc_op=PC_INCR),
    UI_MEM_TO_A_U8,
    UI_PUSH_AS | Ui(last=True),
    Ui(mem_op=MEM_LD_AT_PC, mem_sp=MEM_SP_RAM) | Ui(pc_op=PC_INCR),
    UI_MEM_TO_AH,
    Ui(mem_op=MEM_LD_AT_PC, mem_sp=MEM_SP_RAM) | Ui(pc_op=PC_INCR),
    UI_MEM_TO_AL,
    UI_PUSH_AS | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_LTH),
    UI_PUSH_ALU_L | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_LTH),
    UI_PUSH_ALU_L | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_MUL),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_MUL),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_NEQ),
    UI_PUSH_ALU_L | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_NEQ),
    UI_PUSH_ALU_L | Ui(last=True),
    UI_POP_AS,
    UI_POP_S,
    UI_PUSH_AS | Ui(last=True),
    UI_POP_AS,
    UI_POP_S,
    UI_PUSH_AS | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_ORA),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_ORA),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_AS,
    UI_POP_BS,
    UI_PUSH_BS,
    UI_PUSH_AS,
    UI_PUSH_BS | Ui(last=True),
    UI_POP_AS,
    UI_POP_BS,
    UI_PUSH_BS,
    UI_PUSH_AS,
    UI_PUSH_BS | Ui(last=True),
    UI_POP_S | Ui(last=True),
    UI_POP_S | Ui(last=True),
    UI_POP_AS,
    UI_POP_BS,
    UI_POP_CS,
    UI_PUSH_BS,
    UI_PUSH_AS,
    UI_PUSH_CS | Ui(last=True),
    UI_POP_AS,
    UI_POP_BS,
    UI_POP_CS,
    UI_PUSH_BS,
    UI_PUSH_AS,
    UI_PUSH_CS | Ui(last=True),
    UI_POP_B_U8,
    UI_POP_AS,
    UI_ALU(ALU_OP_SFT),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_B_U8,
    UI_POP_AS,
    UI_ALU(ALU_OP_SFT),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_AW,
    UI_POP_BS,
    Ui(mem_op=MEM_ST_BL_AT_A, mem_sp=MEM_SP_RAM) | Ui(last=True),
    UI_POP_AW,
    UI_POP_BS | UI_ALU_A_PLUS_1,
    Ui(mem_op=MEM_ST_BH_AT_A, mem_sp=MEM_SP_RAM) | UI_ALU_TO_A,
    Ui(mem_op=MEM_ST_BL_AT_A, mem_sp=MEM_SP_RAM) | Ui(last=True),
    UI_POP_AS,
    UI_RPUSH_AS | Ui(last=True),
    UI_POP_AS,
    UI_RPUSH_AS | Ui(last=True),
    UI_POP_A_S8,
    UI_POP_BS | UI_ALU_PC_PLUS_A,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_ST_BL_AT_A, mem_sp=MEM_SP_RAM) | Ui(last=True),
    UI_POP_A_S8,
    UI_POP_BS | UI_ALU_PC_PLUS_A,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_ST_BH_AT_A, mem_sp=MEM_SP_RAM) | UI_ALU_A_PLUS_1,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_ST_BL_AT_A, mem_sp=MEM_SP_RAM) | Ui(last=True),
    UI_POP_A_U8,
    UI_POP_BS,
    Ui(mem_op=MEM_ST_BL_AT_A, mem_sp=MEM_SP_RAM) | Ui(last=True),
    UI_POP_A_U8,
    UI_POP_BS | UI_ALU_A_PLUS_1,
    Ui(mem_op=MEM_ST_BH_AT_A, mem_sp=MEM_SP_RAM) | UI_ALU_TO_A,
    Ui(mem_op=MEM_ST_BL_AT_A, mem_sp=MEM_SP_RAM) | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_SUB),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_BS,
    UI_POP_AS,
    UI_ALU(ALU_OP_SUB),
    UI_PUSH_ALU_S | Ui(last=True),
    UI_POP_AS,
    UI_POP_BS,
    UI_PUSH_AS,
    UI_PUSH_BS | Ui(last=True),
    UI_POP_AS,
    UI_POP_BS,
    UI_PUSH_AS,
    UI_PUSH_BS | Ui(last=True),
    Ui(alu_op=ALU_OP_PASS_OP0, alu_sel0=ALU_SEL0_0, alu_sel1=ALU_SEL1_X),
    UI_ALU_TO_A,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_DEV),
    UI_MEM_TO_BH | UI_ALU_A_PLUS_1,
    UI_ALU_TO_A,
    Ui(mem_op=MEM_LD_AT_A, mem_sp=MEM_SP_DEV),
    UI_MEM_TO_BL,
    Ui(alu_op=ALU_OP_ADD, alu_sel0=ALU_SEL0_0, alu_sel1=ALU_SEL1_B),
    Ui(pc_op=PC_WARP_ALU) | Ui(last=True),
    UI_RPUSH_PC_W,
    Ui(pc_op=PC_WARP_UVEC) | Ui(last=True),
]
# 264 uins total

UCODE_LUT = {
    OP_ADD:                     (  0,  4),
    OP_ADD | OMODE_S:           (  4,  4),
    OP_AND:                     (  8,  4),
    OP_AND | OMODE_S:           ( 12,  4),
    OP_DEO:                     ( 16,  3),
    OP_DEO | OMODE_S:           ( 19,  4),
    OP_DEI:                     ( 23,  4),
    OP_DEI | OMODE_S:           ( 27,  7),
    OP_DIV:                     ( 34,  2),
    OP_DIV | OMODE_S:           ( 36,  2),
    OP_DUP:                     ( 38,  3),
    OP_DUP | OMODE_S:           ( 41,  3),
    OP_EOR:                     ( 44,  4),
    OP_EOR | OMODE_S:           ( 48,  4),
    OP_EQU:                     ( 52,  4),
    OP_EQU | OMODE_S:           ( 56,  4),
    OP_GTH:                     ( 60,  4),
    OP_GTH | OMODE_S:           ( 64,  4),
    OP_INC:                     ( 68,  3),
    OP_INC | OMODE_S:           ( 71,  3),
    OP_JCN:                     ( 74,  3),
    OP_JCN | OMODE_S:           ( 77,  3),
    OP_JMP:                     ( 80,  3),
    OP_JMP | OMODE_S:           ( 83,  3),
    OP_JSR:                     ( 86,  4),
    OP_JSR | OMODE_S:           ( 90,  4),
    OP_LDA:                     ( 94,  4),
    OP_LDA | OMODE_S:           ( 98,  7),
    OP_LDR:                     (105,  6),
    OP_LDR | OMODE_S:           (111,  9),
    OP_LDZ:                     (120,  4),
    OP_LDZ | OMODE_S:           (124,  7),
    OP_LIT & 31:                (131,  3),
    OP_LIT & 31 | OMODE_S:      (134,  5),
    OP_LTH:                     (139,  4),
    OP_LTH | OMODE_S:           (143,  4),
    OP_MUL:                     (147,  4),
    OP_MUL | OMODE_S:           (151,  4),
    OP_NEQ:                     (155,  4),
    OP_NEQ | OMODE_S:           (159,  4),
    OP_NIP:                     (163,  3),
    OP_NIP | OMODE_S:           (166,  3),
    OP_ORA:                     (169,  4),
    OP_ORA | OMODE_S:           (173,  4),
    OP_OVR:                     (177,  5),
    OP_OVR | OMODE_S:           (182,  5),
    OP_POP:                     (187,  1),
    OP_POP | OMODE_S:           (188,  1),
    OP_ROT:                     (189,  6),
    OP_ROT | OMODE_S:           (195,  6),
    OP_SFT:                     (201,  4),
    OP_SFT | OMODE_S:           (205,  4),
    OP_STA:                     (209,  3),
    OP_STA | OMODE_S:           (212,  4),
    OP_STH:                     (216,  2),
    OP_STH | OMODE_S:           (218,  2),
    OP_STR:                     (220,  4),
    OP_STR | OMODE_S:           (224,  6),
    OP_STZ:                     (230,  3),
    OP_STZ | OMODE_S:           (233,  4),
    OP_SUB:                     (237,  4),
    OP_SUB | OMODE_S:           (241,  4),
    OP_SWP:                     (245,  4),
    OP_SWP | OMODE_S:           (249,  4),
    OP_ZZ_STKTRAP:              (253,  9),
    OP_ZZ_UNIMPL:               (262,  2),
}
