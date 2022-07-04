#!/usr/bin/env python3

import copy
import sys
from typing import Optional

from ucode_au20 import *

LOUD = 0
# LOUD = 1

g_cycle_number = 0

def P(*args, **kwargs):
    pc = seq.executing_pc if seq.executing_pc is not None else 0xFFFF
    print(f"[{g_cycle_number:6d} | {pc:04X}h ]", *args, **kwargs)

if LOUD:
    def T(*args, **kwargs):
        P(*args, **kwargs)
else:
    def T(*args, **kwargs):
        pass

class NextState:
    def __init__(self, current):
        self._current = current

    def __getattr__(self, name):
        # lazily copy from current state
        if name not in self.__dict__ and name in self._current:
            self.__dict__[name] = copy.deepcopy(self._current[name])

        return self.__dict__[name]

class Module:
    def __init__(self):
        self.__dict__["s"] = self.init()

    def execute(self, *args, **kwargs):
        next = NextState(self.s)

        self.update(next, *args, **kwargs)

        self.__dict__["_next"] = next

    def commit(self):
        del self._next.__dict__["_current"]

        for k in self._next.__dict__.keys():
            if k not in self.s:
                raise Exception(type(self).__name__ + ": undefined state variable " + k)

        self.s.update(self._next.__dict__)

    def __getattr__(self, name):
        return self.s[name]

    def __setattr__(self, name, value):
        raise Exception("Assignment of register via self. instead of next.")

class MemControl(Module):
    def init(self):
        return dict(_busy_ram=False,
                    _busy_dev=False,

                    ram_valid_o=False,
                    dev_valid_o=False,
                    wr_o=False,
                    addr_o=None,
                    wdata_o=None)

    def rdata(self, ram_rdata, dev_rdata):
        return ram_rdata if self._busy_ram else dev_rdata

    def ready(self):
        # TODO: could accept new request 1 cycle earlier
        return not self._busy_ram and not self._busy_dev

    def resp_valid(self, ram_valid_i, dev_valid_i):
        # assuming no unsolicited responses, of course
        return ram_valid_i if self._busy_ram else dev_valid_i

    def update(self, next, mem_op, pc, reg_a, reg_b, ram_valid_i, ram_data_i, dev_valid_i, dev_data_i, hint_fetching_code):
        if ram_valid_i:
            if hint_fetching_code:
                T(f"-- fetched RAM opcode {ram_data_i:02X}h {opcode_to_mnemonic(ram_data_i)}")
            else:
                T(f"-- fetched RAM data {ram_data_i:02X}h")
            assert self._busy_ram

        if dev_valid_i:
            T(f"-- fetched DEV {dev_data_i:02X}h")
            assert self._busy_dev

        if self._busy_ram and ram_valid_i:
            next._busy_ram = False

        if self._busy_dev and dev_valid_i:
            next._busy_dev = False

        next.ram_valid_o = False
        next.dev_valid_o = False
        next.wr_o = False
        next.addr_o = None
        next.wdata_o = None

        # data has priority
        if mem_op in {MEM_ST_BL_AT_A, MEM_ST_BH_AT_A}:
            assert self.ready()

            next.addr_o = reg_a
            next.ram_valid_o = (mem_sp == MEM_SP_RAM)
            next.dev_valid_o = (mem_sp == MEM_SP_DEV)
            next.wr_o = True
            next.wdata_o = {
                MEM_ST_BL_AT_A: reg_b & 0x00ff,
                MEM_ST_BH_AT_A: reg_b >> 8,
            }[mem_op]

            T(f"MEM_ST_B?_AT_A: [{reg_a:04X}h] <= {next.wdata_o:02X}h")
        elif mem_op in {MEM_LD_AT_A, MEM_LD_AT_PC}:
            assert self.ready()      # Ucode currently assumes that mem_op can not stall
                                        # (this will have to change...)

            next.addr_o = {
                MEM_LD_AT_PC: pc,
                MEM_LD_AT_A: reg_a
            }[mem_op]

            next.ram_valid_o = (mem_sp == MEM_SP_RAM)
            next._busy_ram = next.ram_valid_o

            next.dev_valid_o = (mem_sp == MEM_SP_DEV)
            next._busy_dev = next.dev_valid_o

            T(f"-- start code/data fetch @ {mem_sp_str[mem_sp]}:{next.addr_o:04X}h")


class Sequencer(Module):
    def init(self):
        return dict(pc=0x100,
                    executing_pc=None,
                    ucode_addr=len(UCODE_ROM),
                    r_mode=False,
                    s_mode=False,
                    k_mode=False,
                    fetching_code=False,
                    # tvec=0x0100,
                    dvec=0xff80,
                    )

    def current_uins(self) -> Optional[AuroraUins]:
        if self.ucode_addr < len(UCODE_ROM):
            return UCODE_ROM[self.ucode_addr]
        else:
            return None

    def update(self, next, mem_ready, alu_res, reg_b, mem_valid_i, ram_data_i, stk_trap_i):
        """
        Fetcher logic:
        - if fetch in progress:
            - code fetch completed?
                - if out of uprog, load new uprog
            - data fetch completed?
                - unstall pipeline (don't really do nothing)
        - else:
            - if need to fetch data, begin fetch
            - if ucode ran out, begin fetch + increment PC
        """

        is_out_of_uprog = (self.ucode_addr == len(UCODE_ROM))

        if self.fetching_code:
            if mem_valid_i:
                opcode = ram_data_i

                if opcode == 0x00:
                    # print("BRK")
                    print()
                    sys.exit()

                try:
                    start, length = UCODE_LUT[opcode & ~(OMODE_R | OMODE_k)]
                except KeyError:
                    raise Exception(f"unimplemented {opcode:02X}h") from None

                next.ucode_addr = start

                next.r_mode = (opcode & OMODE_R) != 0
                next.s_mode = (opcode & OMODE_S) != 0
                next.k_mode = (opcode & OMODE_k) != 0
                # pc_op = PC_INCR

                next.fetching_code = False
            else:
                T("-- code stall")

            pc_op = PC_NOP

        # ucode_addr automaton
        if not is_out_of_uprog:
            uins = UCODE_ROM[self.ucode_addr]

            pc_op = uins.pc_op

            # advance to next uins, unless stalled
            mem_stall = (uins.reg_in_sel == REG_IN_MEM and not mem_valid_i)

            if stk_trap_i:
                # TODO: save stack id & error number

                next.ucode_addr = UCODE_LUT[OP_ZZ_STKTRAP][0]
            elif mem_stall:
                T("-- memory stall")
            else:
                if uins.last:
                    next.ucode_addr = len(UCODE_ROM)
                else:
                    next.ucode_addr = self.ucode_addr + 1
            T("-- uexec", uins)

        if is_out_of_uprog and mem_ready:
            # TODO: can probably start fetching next opcode sooner

            next.fetching_code = True

            next.executing_pc = self.pc   # not really true until fetch complete, but we'll stall anyway

            # increment PC when code fetch starting (this logic should be simplified / moved to ucode)
            pc_op = PC_INCR

        if pc_op == PC_INCR:
            next.pc = self.pc + 1
        elif pc_op == PC_WARP_ALU:
            T("WARP to ALU_RES: alu_res=", alu_res)

            next.pc = alu_res
        elif pc_op == PC_WARP_ALU_IF_BL_NONZERO:
            T("WARP to ALU_RES if B[7:0] != 0: alu_res=", alu_res, "b=", reg_b)

            if (reg_b & 0x00ff) != 0:
                next.pc = alu_res
        elif pc_op == PC_WARP_DVEC_S:
            T("JUMP to DVEC.s")

            next.pc = self.dvec | (16 if self.s_mode else 0)
            # next.uprog = []
            assert uins.last
        else:
            assert pc_op == PC_NOP


class RegFile(Module):
    def init(self):
        return dict(a=0, b=0, c=0)

    def update(self, next, al_wr, ah_wr, bl_wr, bh_wr, cl_wr, ch_wr,
               sel, h_mode, alu_res, mem_rdata, wst_top, rst_top):
        inp = {
            REG_IN_X:       None,
            REG_IN_ALU:     alu_res,
            REG_IN_MEM:     mem_rdata,
            REG_IN_RST:     rst_top,
            REG_IN_WST:     wst_top,
        }[sel]

        inp_l = (inp & 0x00ff) if inp is not None else None

        inp_h = {
            REG_H_X:        None,
            REG_H_ALU_H:    (alu_res >> 8) if alu_res is not None else None,
            REG_H_MIRROR:   inp_l,
            REG_H_SIGN:     0xff if (inp_l is not None and inp_l & 0x80) else 0,
            REG_H_ZERO:     0x00,
            REG_H_H:        (inp >> 8) if inp is not None else None,
        }[h_mode]

        if al_wr:
            T(f"AL <= {inp_l:02X}h")
            next.a = (next.a & 0xff00) | inp_l

        if ah_wr:
            T(f"AH <= {inp_h:02X}h")
            next.a = (next.a & 0x00ff) | (inp_h << 8)

        if bl_wr:
            T(f"BL <= {inp_l:02X}h")
            next.b = (next.b & 0xff00) | inp_l

        if bh_wr:
            T(f"BH <= {inp_h:02X}h")
            next.b = (next.b & 0x00ff) | (inp_h << 8)

        if cl_wr:
            T(f"CL <= {inp_l:02X}h")
            next.c = (next.c & 0xff00) | inp_l

        if ch_wr:
            T(f"CH <= {inp_h:02X}h")
            next.c = (next.c & 0x00ff) | (inp_h << 8)


class Alu(Module):
    def init(self):
        return dict(res=0xBAAD)

    def update(self, next, alu_op, alu_sel0, alu_sel1, reg_a, reg_b, pc):
        op0 = {
            ALU_SEL0_A: reg_a,
            ALU_SEL0_0: 0,
            ALU_SEL0_X: None,
        }[alu_sel0]

        if alu_sel1 == ALU_SEL1_1:
            op1 = 1
        elif alu_sel1 == ALU_SEL1_B:
            op1 = reg_b
        elif alu_sel1 == ALU_SEL1_PC:
            op1 = pc
        else:
            op1 = 0x77777777

        alu_ops = {
            ALU_OP_ADD: ("+",   lambda op0, op1: op0 + op1),
            ALU_OP_AND: ("&",   lambda op0, op1: op0 & op1),
            ALU_OP_EOR: ("^",   lambda op0, op1: op0 ^ op1),
            ALU_OP_EQU: ("==",  lambda op0, op1: 1 if op0 == op1 else 0),
            ALU_OP_GTH: (">",   lambda op0, op1: 1 if op0 > op1 else 0),
            ALU_OP_LTH: ("<",   lambda op0, op1: 1 if op0 < op1 else 0),
            ALU_OP_MUL: ("*",   lambda op0, op1: op0 * op1),
            ALU_OP_NEQ: ("!=",  lambda op0, op1: 1 if op0 != op1 else 0),
            ALU_OP_ORA: ("|",   lambda op0, op1: op0 | op1),
            ALU_OP_SFT: ("SFT", lambda op0, op1: op0 >> (op1 & 0x0f) << ((op1 & 0xf0) >> 4)),
            ALU_OP_SUB: ("-",   lambda op0, op1: op0 - op1),
        }

        if alu_op == ALU_OP_PASS_OP0:
            next.res = op0
        elif alu_op == ALU_OP_X:
            next.res = None
        else:
            operator, func = alu_ops[alu_op]

            next.res = func(op0, op1) & 0xffff
            T(op0, operator, op1, "=", next.res)


class Stack(Module):
    def __init__(self, name):
        super().__init__()
        self.__dict__["_name"] = name

    def init(self):
        return dict(values=[None] * 254, rpos=0, wpos=0)

    def top(self, sz, s):
        if sz == -1:
            return None

        eff_sz = {
            STK_SZ_S: 2 if s else 1,
            STK_SZ_16: 2,
            STK_SZ_8L: 1,
            STK_SZ_8H: 1,
        }[sz]

        if eff_sz == 1:
            return self.values[self.rpos - 1] if self.rpos >= 1 else None
        else:
            return ((self.values[self.rpos - 2] << 8) | self.values[self.rpos - 1]) if self.rpos >= 2 else None

    # does this uop cause a trap (over/underflow)?
    def trap_req_o(self, op, sz, s) -> bool:
        eff_sz = {      # FIXME DRY
            STK_SZ_X: None,
            STK_SZ_S: 2 if s else 1,
            STK_SZ_16: 2,
            STK_SZ_8L: 1,
            STK_SZ_8H: 1,
        }[sz]

        if op == STK_PUSH:
            return (self.wpos + eff_sz >= len(self.values))
        elif op == STK_POP:
            return (self.rpos - eff_sz < 0)
        else:
            return False

    def update(self, next, instr_start, op, in_sel, sz, s, k, alu_res, reg_a, reg_b, reg_c, pc):
        """
        K-mode logic:
          if not k:
            push updates wpos
            pop updates rpos, wpos
          if k:
            push updates wpos
            pop updates rpos

        End of instruction (always):
          rpos <= wpos

        A microprogram must not POP after PUSHing since push doesn't update rpos.
        """

        data_i = {
            STK_IN_X:       None,
            STK_IN_ALU_RES: alu_res,
            STK_IN_REG_A:   reg_a,
            STK_IN_REG_B:   reg_b,
            STK_IN_REG_C:   reg_c,
            STK_IN_PC:      pc,
        }[in_sel]

        if data_i is not None:
            data_i = {
                STK_SZ_S:  data_i,      # only Lo8 will be used anyway
                STK_SZ_16: data_i,
                STK_SZ_8L: data_i & 0xff,
                STK_SZ_8H: data_i >> 16,
            }[sz]

        eff_sz = {      # FIXME DRY
            STK_SZ_X: None,
            STK_SZ_S: 2 if s else 1,
            STK_SZ_16: 2,
            STK_SZ_8L: 1,
            STK_SZ_8H: 1,
        }[sz]

        if op == STK_PUSH and self.wpos + eff_sz < len(self.values):
            if eff_sz == 1:
                T(f"PUSH {self._name}[{self.wpos}] <= {data_i & 0xff:02X}h")
                # assert self.wpos + 1 < len(self.values)

                next.values[self.wpos] = data_i & 0xff
                next.wpos = self.wpos + 1
            else:
                T(f"PUSH {self._name}[{self.wpos}:{self.wpos+1}] <= {data_i:04X}h")
                # assert self.wpos + 2 < len(self.values)

                next.values[self.wpos] = (data_i >> 8)
                next.values[self.wpos + 1] = (data_i & 0xff)
                next.wpos = self.wpos + 2
        elif op == STK_POP and self.rpos - eff_sz >= 0:
            if eff_sz == 1:
                T(f"POP {self._name} => {self.top(sz, s):02X}h")

                # assert self.rpos - 1 >= 0
                next.rpos = self.rpos - 1
            else:
                T(f"POP {self._name} => {self.top(sz, s):04X}h")

                # assert self.rpos - 2 >= 0
                next.rpos = self.rpos - 2

            if not k:
                next.wpos = next.rpos
        else:
            assert op in {STK_NOP, STK_POP, STK_PUSH}

        if instr_start:
            # re-synchronize pointers if previous instruction was keep-mode
            next.rpos = next.wpos


class Ram(Module):
    def __init__(self, name, size):
        self.__dict__["_name"] = name
        self.__dict__["_size"] = size
        super().__init__()

    def init(self):
        mem_array = [0x00] * self._size

        return dict(mem_array=mem_array,
                    valid_o=False, data_o=None,
                    _patches=[])

    def commit(self):
        super().commit()

        # deepcopy too slow to do every step, so just patch specific addresses
        for addr, value in self._patches:
            self.s["mem_array"][addr] = value
        self._patches.clear()

    def load(self, addr, data):
        self.s["mem_array"][addr:addr + len(data)] = data

    def update(self, next, valid_i, wr, addr, data_i):
        # 1-cycle write
        if valid_i and wr:
            T(f"{self._name}[{addr:04X}h] <= {data_i:02X}h")
            #next.mem_array[addr] = data_i  too slow
            self._patches.append((addr, data_i))

        next.valid_o = valid_i and not wr
        next.data_o = self.mem_array[addr] if valid_i else 0xAA
        # data_o may be looked at by Reg file even if not valid so we use a reasonable placeholder


mem = MemControl()
seq = Sequencer()
reg = RegFile()
alu = Alu()
stk = Stack("wst")
rst = Stack("rst")
ram = Ram("ram", 0x10000)
dev = Ram("dev", 0x100)


args = sys.argv[1:]
if args[0] == "-hex":
    hex_stdout = True
    args.pop(0)
else:
    hex_stdout = False

with open("fw/fw.rom", "rb") as f:
    ram.load(0x100, f.read())

with open(args[0], "rb") as f:
    ram.load(0x100, f.read())

MAXCYC = 4_000_000      # div16_gen.rom currently the longest

for i in range(MAXCYC):
    g_cycle_number = i

    uins = seq.current_uins()

    if uins is None:
        if not seq.fetching_code:
            mem_op = MEM_LD_AT_PC       # this is what currently triggers opcode fetch
        else:
            mem_op = MEM_NOP

        reg_al_wr = False; reg_ah_wr = False
        reg_bl_wr = False; reg_bh_wr = False
        reg_cl_wr = False; reg_ch_wr = False
        reg_in_sel = REG_IN_X
        reg_h_mode = REG_H_MIRROR
        alu_op = ALU_OP_X
        alu_sel0 = ALU_SEL0_X
        alu_sel1 = ALU_SEL1_X
        wst_op = STK_NOP; wst_in_sel = STK_IN_X; wst_sz = STK_SZ_X
        rst_op = STK_NOP; rst_in_sel = STK_IN_X; rst_sz = STK_SZ_X
        mem_sp = MEM_SP_RAM           # needed to fetch code
        s = 0
        k = 0
    else:
        reg_al_wr = uins.reg_al_wr; reg_ah_wr = uins.reg_ah_wr
        reg_bl_wr = uins.reg_bl_wr; reg_bh_wr = uins.reg_bh_wr
        reg_cl_wr = uins.reg_cl_wr; reg_ch_wr = uins.reg_ch_wr
        reg_in_sel = uins.reg_in_sel
        reg_h_mode = uins.reg_h_mode
        alu_op = uins.alu_op
        alu_sel0 = uins.alu_sel0
        alu_sel1 = uins.alu_sel1

        if not seq.r_mode:
            wst_op = uins.wst_op; wst_in_sel = uins.wst_in_sel; wst_sz = uins.wst_sz
            rst_op = uins.rst_op; rst_in_sel = uins.rst_in_sel; rst_sz = uins.rst_sz
        else:
            rst_op = uins.wst_op; rst_in_sel = uins.wst_in_sel; rst_sz = uins.wst_sz
            wst_op = uins.rst_op; wst_in_sel = uins.rst_in_sel; wst_sz = uins.rst_sz

        mem_op = uins.mem_op
        mem_sp = uins.mem_sp

        if seq.r_mode:
            if reg_in_sel == REG_IN_WST:
                reg_in_sel = REG_IN_RST
            elif reg_in_sel == REG_IN_RST:
                reg_in_sel = REG_IN_WST

        s = seq.s_mode
        k = seq.k_mode

    mem.execute(mem_op=mem_op,
                pc=seq.pc,
                reg_a=reg.a,
                reg_b=reg.b,
                ram_valid_i=ram.valid_o,
                ram_data_i=ram.data_o,
                dev_valid_i=dev.valid_o,
                dev_data_i=dev.data_o,

                hint_fetching_code=seq.fetching_code,
                )
    seq.execute(mem_ready=mem.ready(),
                alu_res=alu.res,
                reg_b=reg.b,
                mem_valid_i=mem.resp_valid(ram_valid_i=ram.valid_o, dev_valid_i=dev.valid_o),
                ram_data_i=ram.data_o,
                stk_trap_i=stk.trap_req_o(op=wst_op, sz=wst_sz, s=s) or rst.trap_req_o(op=rst_op, sz=rst_sz, s=s))
    reg.execute(al_wr=reg_al_wr, ah_wr=reg_ah_wr,
                bl_wr=reg_bl_wr, bh_wr=reg_bh_wr,
                cl_wr=reg_cl_wr, ch_wr=reg_ch_wr,
                sel=reg_in_sel,
                h_mode=reg_h_mode,
                alu_res=alu.res,
                mem_rdata=mem.rdata(ram_rdata=ram.data_o, dev_rdata=dev.data_o),
                wst_top=stk.top(sz=wst_sz, s=s),
                rst_top=rst.top(sz=rst_sz, s=s))
    alu.execute(alu_op=alu_op, alu_sel0=alu_sel0, alu_sel1=alu_sel1, reg_a=reg.a, reg_b=reg.b, pc=seq.pc)
    # TODO: instr_start logic
    stk.execute(instr_start=uins is None, op=wst_op, in_sel=wst_in_sel, sz=wst_sz, s=s, k=k, alu_res=alu.res,
                reg_a=reg.a, reg_b=reg.b, reg_c=reg.c, pc=seq.pc)
    rst.execute(instr_start=uins is None, op=rst_op, in_sel=rst_in_sel, sz=rst_sz, s=s, k=k, alu_res=alu.res,
                reg_a=reg.a, reg_b=reg.b, reg_c=reg.c, pc=seq.pc)
    ram.execute(valid_i=mem.ram_valid_o,
                wr=mem.wr_o,
                addr=mem.addr_o,
                data_i=mem.wdata_o)
    dev.execute(valid_i=mem.dev_valid_o,
                wr=mem.wr_o,
                addr=mem.addr_o,
                data_i=mem.wdata_o)

    if mem.dev_valid_o and mem.wr_o:
        addr, value = mem.addr_o, mem.wdata_o

        if addr == 0x18:
            # print(f"DEO [{addr:04X}h] <= {value:02X}h {value:c}")
            if hex_stdout:
                print(f"{value:02x}", end="")
            else:
                sys.stdout.write(chr(value))
        elif addr == 0x0f and value != 0:
            # HALT
            break

    mem.commit(); seq.commit(); reg.commit(); alu.commit(); stk.commit(); rst.commit(); ram.commit(); dev.commit()
    T()
else:
    raise Exception("Execution limit reached. Presumably the program got stuck or you need to increase MAXCYC")

print()

print(i + 1, file=sys.stderr)
