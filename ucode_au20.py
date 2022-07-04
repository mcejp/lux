from ucode_au20_gen import UCODE_LUT, UCODE_ROM

from aurora import *
from uxn_isa import *

# all short loads are fucked slow since we're afraid to start next mem at last cycle of 1st

# To flip instruction normal<->R-mode:
#  - exchange rst_*, wst_* fields
#  - exchange REG_IN_WST <-> REG_IN_RST
# (done by sequencer based on opcode R bit; this saves a lot of ROM)

def validate_ucode():
    for uins in UCODE_ROM:
        # pre-check since we want to merge these fields
        assert uins.rst_op is STK_NOP or uins.wst_op is STK_NOP
        assert uins.rst_in_sel is STK_IN_X or uins.wst_in_sel is STK_IN_X or uins.rst_in_sel == uins.wst_in_sel
        assert uins.rst_sz is STK_IN_X or uins.wst_sz is STK_IN_X or uins.rst_sz == uins.wst_sz

        # if only one register is ever written at a time, we could do something with that
        a_wr = uins.reg_al_wr or uins.reg_ah_wr
        b_wr = uins.reg_bl_wr or uins.reg_bh_wr
        c_wr = uins.reg_cl_wr or uins.reg_ch_wr
        assert sum([a_wr, b_wr, c_wr]) <= 1

        #
        if uins.mem_op != MEM_NOP:
            assert uins.mem_sp != MEM_SP_X

validate_ucode()
