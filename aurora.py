from dataclasses import dataclass

# Aurora microarchitecture
#
# Terminology:
# - microcode (ucode) -- entire body of microcode
# - microprogram (uprog) -- microcode for a single instruction
# - micro-instruction (uins)
#
# - micro-operation (uop) -- not used here

ALU_OP_X = -1
ALU_OP_PASS_OP0 = 0     # probably useless, can do MUL 1, EOR 0 or something clever
ALU_OP_ADD = 1
ALU_OP_SUB = 2
ALU_OP_MUL = 3
ALU_OP_EOR = 4
ALU_OP_SFT = 5
ALU_OP_EQU = 6          # perhaps some symmetry among these can be exploited
ALU_OP_NEQ = 7          # (perhaps that doesn't necessitate any change in the encoding though)
ALU_OP_GTH = 8
ALU_OP_LTH = 9
ALU_OP_AND = 11
ALU_OP_ORA = 12

ALU_SEL0_X = -1         # don't care
ALU_SEL0_A = 0          # register A

ALU_SEL1_X = -1         # don't care
ALU_SEL1_1 = 0          # constant 1
ALU_SEL1_B = 1          # reg B
ALU_SEL1_PC = 2         # program counter (for relative jumps)

# often we miss:
#  - load at stack top (W) -> LDA
#  - load at stack top (U8) -> LDZ
#  - load at alu -> LDR & all 2-byte loads
MEM_NOP = 0
MEM_LD_AT_A = 1
MEM_LD_AT_PC = 2
MEM_ST_BL_AT_A = 3
MEM_ST_BH_AT_A = 4

MEM_SP_X = -1
MEM_SP_RAM = 0
MEM_SP_DEV = 1

REG_IN_X = -1
REG_IN_WST = 0
REG_IN_MEM = 1
REG_IN_ALU = 2
REG_IN_RST = 3          # UNUSED!

# TODO: this stopped making sense with 16-bit stacks
REG_H_X = -1
REG_H_MIRROR = 0        # copy low byte to high byte; USELESS IF ONLY NEEDED FOR MEM which is just 8 bits wide
REG_H_ZERO = 1          # set high byte to all 0
REG_H_SIGN = 2          # sign extend low byte into high byte
REG_H_ALU_H = 3         # REDUNADNT with REG_H_H
REG_H_H = 4

PC_NOP = 0
PC_INCR = 1
PC_WARP_ALU = 2
PC_WARP_ALU_IF_BL_NONZERO = 3
PC_WARP_DVEC_S = 4

STK_NOP = 0
STK_PUSH = 1
STK_POP = 2

# could reduce footprint further by merging Stk mux of A/B/C with someone else's mux of A/B/C (if there is such one)
STK_IN_X = -1
STK_IN_ALU_RES = 0
STK_IN_REG_A = 2
STK_IN_REG_B = 4
STK_IN_REG_C = 6
STK_IN_PC = 8         # These can be probably removed if we force JSR to go through ALU

STK_SZ_X = -1
STK_SZ_8L = 0
STK_SZ_8H = 1
STK_SZ_16 = 2
STK_SZ_S = 3


@dataclass
class AuroraUins:
    alu_op: int = ALU_OP_X
    alu_sel0: int = ALU_SEL0_X
    alu_sel1: int = ALU_SEL1_X

    pc_op: int = PC_NOP

    # reg A
    reg_al_wr: bool = False
    reg_ah_wr: bool = False

    # reg B
    reg_bl_wr: bool = False
    reg_bh_wr: bool = False

    # reg C
    reg_cl_wr: bool = False
    reg_ch_wr: bool = False

    # reg common
    reg_in_sel: int = REG_IN_X
    reg_h_mode: int = REG_H_X
    # Note: could separate A/B/C selection from H/L write enable to save 1 bit

    # working stack (WST)
    wst_op: int = STK_NOP
    wst_in_sel: int = STK_IN_X
    wst_sz: int = STK_SZ_X

    # return stack (RST);
    # TODO: merge with WST & add 1-bit Stack Select
    rst_op: int = STK_NOP
    rst_in_sel: int = STK_IN_X
    rst_sz: int = STK_SZ_X

    # memory
    mem_op: int = MEM_NOP
    mem_sp: int = MEM_SP_X

    # Note: some fields could be made to overlap if they're never used at the same time

    def __or__(self, other):
        def select(left, right, neutral):
            if left == neutral or left == right:
                return right
            elif right == neutral:
                return left
            else:
                raise Exception(f"Combination not permitted: {left} | {right}")

        return AuroraUins(
            alu_op=select(self.alu_op, other.alu_op, ALU_OP_X),
            alu_sel0=select(self.alu_sel0, other.alu_sel0, ALU_SEL0_X),
            alu_sel1=select(self.alu_sel1, other.alu_sel1, ALU_SEL1_X),

            pc_op=select(self.pc_op, other.pc_op, PC_NOP),

            reg_al_wr=self.reg_al_wr or other.reg_al_wr,
            reg_ah_wr=self.reg_ah_wr or other.reg_ah_wr,
            reg_bl_wr=self.reg_bl_wr or other.reg_bl_wr,
            reg_bh_wr=self.reg_bh_wr or other.reg_bh_wr,
            reg_cl_wr=self.reg_cl_wr or other.reg_cl_wr,
            reg_ch_wr=self.reg_ch_wr or other.reg_ch_wr,

            reg_in_sel=select(self.reg_in_sel, other.reg_in_sel, REG_IN_X),
            reg_h_mode=select(self.reg_h_mode, other.reg_h_mode, REG_H_X),

            wst_op=select(self.wst_op, other.wst_op, STK_NOP),
            wst_in_sel=select(self.wst_in_sel, other.wst_in_sel, STK_IN_X),
            wst_sz=select(self.wst_sz, other.wst_sz, STK_SZ_X),

            rst_op=select(self.rst_op, other.rst_op, STK_NOP),
            rst_in_sel=select(self.rst_in_sel, other.rst_in_sel, STK_IN_X),
            rst_sz=select(self.rst_sz, other.rst_sz, STK_SZ_X),

            mem_op=select(self.mem_op, other.mem_op, MEM_NOP),
            mem_sp=select(self.mem_sp, other.mem_sp, MEM_SP_X),
        )

Ui = AuroraUins

# provide some microprogram primitives
# TODO: migrate all to lisp macros

UI_ALU_TO_A =   Ui(reg_al_wr=True, reg_ah_wr=True, reg_in_sel=REG_IN_ALU, reg_h_mode=REG_H_ALU_H)

UI_MEM_TO_A_U8 =  Ui(reg_al_wr=True, reg_ah_wr=True, reg_in_sel=REG_IN_MEM, reg_h_mode=REG_H_ZERO)
UI_MEM_TO_AL =  Ui(reg_al_wr=True, reg_in_sel=REG_IN_MEM)
UI_MEM_TO_AH =  Ui(reg_ah_wr=True, reg_in_sel=REG_IN_MEM, reg_h_mode=REG_H_MIRROR)
UI_MEM_TO_BL =  Ui(reg_bl_wr=True, reg_in_sel=REG_IN_MEM)
UI_MEM_TO_BH =  Ui(reg_bh_wr=True, reg_in_sel=REG_IN_MEM, reg_h_mode=REG_H_MIRROR)

# note: UI_MEM_TO_BL is always (?) followed by PUSH_BL, might be worth optimizing

UI_POP_S =        Ui(wst_op=STK_POP, wst_sz=STK_SZ_S)
UI_POP_A_S8 =   Ui(wst_op=STK_POP, wst_sz=STK_SZ_8L, reg_al_wr=True, reg_ah_wr=True, reg_in_sel=REG_IN_WST, reg_h_mode=REG_H_SIGN)
UI_POP_A_U8 =   Ui(wst_op=STK_POP, wst_sz=STK_SZ_8L, reg_al_wr=True, reg_ah_wr=True, reg_in_sel=REG_IN_WST, reg_h_mode=REG_H_ZERO)
UI_POP_AW =     Ui(wst_op=STK_POP, wst_sz=STK_SZ_16, reg_al_wr=True, reg_ah_wr=True, reg_in_sel=REG_IN_WST, reg_h_mode=REG_H_H)
UI_POP_AS =     Ui(wst_op=STK_POP, wst_sz=STK_SZ_S, reg_al_wr=True, reg_ah_wr=True, reg_in_sel=REG_IN_WST, reg_h_mode=REG_H_H)
UI_POP_B_U8 =   Ui(wst_op=STK_POP, wst_sz=STK_SZ_8L, reg_bl_wr=True, reg_bh_wr=True, reg_in_sel=REG_IN_WST, reg_h_mode=REG_H_ZERO)
UI_POP_BS =     Ui(wst_op=STK_POP, wst_sz=STK_SZ_S, reg_bl_wr=True, reg_bh_wr=True, reg_in_sel=REG_IN_WST, reg_h_mode=REG_H_H)
UI_POP_CS =     Ui(wst_op=STK_POP, wst_sz=STK_SZ_S, reg_cl_wr=True, reg_ch_wr=True, reg_in_sel=REG_IN_WST, reg_h_mode=REG_H_H)

UI_PUSH_AS =    Ui(wst_op=STK_PUSH, wst_in_sel=STK_IN_REG_A, wst_sz=STK_SZ_S)
UI_PUSH_AW =    Ui(wst_op=STK_PUSH, wst_in_sel=STK_IN_REG_A, wst_sz=STK_SZ_16)
UI_PUSH_BS =    Ui(wst_op=STK_PUSH, wst_in_sel=STK_IN_REG_B, wst_sz=STK_SZ_S)
UI_PUSH_CS =    Ui(wst_op=STK_PUSH, wst_in_sel=STK_IN_REG_C, wst_sz=STK_SZ_S)

UI_PUSH_ALU_L = Ui(wst_op=STK_PUSH, wst_in_sel=STK_IN_ALU_RES, wst_sz=STK_SZ_8L)
UI_PUSH_ALU_S = Ui(wst_op=STK_PUSH, wst_in_sel=STK_IN_ALU_RES, wst_sz=STK_SZ_S)

UI_RPUSH_AS = Ui(rst_op=STK_PUSH, rst_in_sel=STK_IN_REG_A, rst_sz=STK_SZ_S)

UI_RPUSH_PC_W = Ui(rst_op=STK_PUSH, rst_in_sel=STK_IN_PC, rst_sz=STK_SZ_16)

def UI_ALU(alu_op): return Ui(alu_op=alu_op, alu_sel0=ALU_SEL0_A, alu_sel1=ALU_SEL1_B)

UI_ALU_A_PLUS_1 =  Ui(alu_op=ALU_OP_ADD, alu_sel0=ALU_SEL0_A, alu_sel1=ALU_SEL1_1)
UI_ALU_PC_PLUS_A = Ui(alu_op=ALU_OP_ADD, alu_sel0=ALU_SEL0_A, alu_sel1=ALU_SEL1_PC)


# Replace ALU_OP_([A-Z0-9_]+) = .+
# To ALU_OP_$1: "$1",
alu_op_str = {
    ALU_OP_X: "X",
    ALU_OP_PASS_OP0: "PASS_OP0",
    ALU_OP_ADD: "ADD",
    ALU_OP_SUB: "SUB",
    ALU_OP_MUL: "MUL",
    ALU_OP_EOR: "EOR",
    ALU_OP_SFT: "SFT",
    ALU_OP_EQU: "EQU",
    ALU_OP_NEQ: "NEQ",
    ALU_OP_GTH: "GTH",
    ALU_OP_LTH: "LTH",
    ALU_OP_AND: "AND",
    ALU_OP_ORA: "ORA",
}

alu_sel0_str = {
    ALU_SEL0_X: "X",
    ALU_SEL0_A: "A",
}

alu_sel1_str = {
    ALU_SEL1_X: "X",
    ALU_SEL1_1: "1",
    ALU_SEL1_B: "B",
    ALU_SEL1_PC: "PC",
}

mem_op_str = {
    MEM_NOP: "NOP",
    MEM_LD_AT_A: "LD(A)",
    MEM_LD_AT_PC: "LD(PC)",
    MEM_ST_BL_AT_A: "(A) <= BL",
    MEM_ST_BH_AT_A: "(A) <= BH",
}

mem_sp_str = {
    MEM_SP_X: "X",
    MEM_SP_RAM: "RAM",
    MEM_SP_DEV: "DEV",
}

pc_op_str = {
    PC_NOP: "NOP",
    PC_INCR: "INCR",
    PC_WARP_ALU: "->ALU",
    PC_WARP_ALU_IF_BL_NONZERO: "->ALU<br>if BL != 0",
    PC_WARP_DVEC_S: "->DVEC.s",
}

reg_in_sel_str = {
    REG_IN_X: "X",
    REG_IN_WST: "WST",
    REG_IN_MEM: "MEM",
    REG_IN_ALU: "ALU",
}

stk_in_str = {
    STK_IN_X: "X",
    STK_IN_ALU_RES: "ALU_RES",
    STK_IN_REG_A: "REG_A",
    STK_IN_REG_B: "REG_B",
    STK_IN_REG_C: "REG_C",
    STK_IN_PC: "PC",
}
