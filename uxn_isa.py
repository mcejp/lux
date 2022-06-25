OMODE_k = 0x80
OMODE_R = 0x40
OMODE_S = 0x20

OP_BRK = 0x00
OP_INC = 0x01
OP_POP = 0x02
OP_NIP = 0x03
OP_SWP = 0x04
OP_ROT = 0x05
OP_DUP = 0x06
OP_OVR = 0x07
OP_EQU = 0x08
OP_NEQ = 0x09
OP_GTH = 0x0a
OP_LTH = 0x0b
OP_JMP = 0x0c
OP_JCN = 0x0d
OP_JSR = 0x0e
OP_STH = 0x0f
OP_LDZ = 0x10
OP_STZ = 0x11
OP_LDR = 0x12
OP_STR = 0x13
OP_LDA = 0x14
OP_STA = 0x15
OP_DEI = 0x16
OP_DEO = 0x17
OP_ADD = 0x18
OP_SUB = 0x19
OP_MUL = 0x1A
OP_DIV = 0x1B
OP_AND = 0x1C
OP_ORA = 0x1D
OP_EOR = 0x1E
OP_SFT = 0x1F
OP_LIT = 0x80


opcode_to_str = {
    OP_BRK: "BRK",
    OP_INC: "INC",
    OP_POP: "POP",
    OP_NIP: "NIP",
    OP_SWP: "SWP",
    OP_ROT: "ROT",
    OP_DUP: "DUP",
    OP_OVR: "OVR",
    OP_EQU: "EQU",
    OP_NEQ: "NEQ",
    OP_GTH: "GTH",
    OP_LTH: "LTH",
    OP_JMP: "JMP",
    OP_JCN: "JCN",
    OP_JSR: "JSR",
    OP_STH: "STH",
    OP_LDZ: "LDZ",
    OP_STZ: "STZ",
    OP_LDR: "LDR",
    OP_STR: "STR",
    OP_LDA: "LDA",
    OP_STA: "STA",
    OP_DEI: "DEI",
    OP_DEO: "DEO",
    OP_ADD: "ADD",
    OP_SUB: "SUB",
    OP_MUL: "MUL",
    OP_DIV: "DIV",
    OP_AND: "AND",
    OP_ORA: "ORA",
    OP_EOR: "EOR",
    OP_SFT: "SFT",
    OP_LIT: "LIT",
}
