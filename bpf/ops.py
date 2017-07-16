import enum
from functools import reduce
import operator
import struct


class Class(enum.IntEnum):
    LD = 0x00
    LDX = 0x01
    ST = 0x02
    STX = 0x03
    ALU = 0x04
    JMP = 0x05
    RET = 0x06
    MISC = 0x07

    def op(self, *args):
        return reduce(operator.or_, args, self.value)


class Size(enum.IntEnum):
    W = 0x00
    H = 0x08
    B = 0x10


class Mode(enum.IntEnum):
    IMM = 0x00
    ABS = 0x20
    IND = 0x40
    MEM = 0x60
    LEN = 0x80
    MSH = 0xa0


class Op(enum.IntEnum):
    ADD = 0x00
    SUB = 0x10
    MUL = 0x20
    DIV = 0x30
    OR = 0x40
    AND = 0x50
    LSH = 0x60
    RSH = 0x70
    NEG = 0x80
    MOD = 0x90
    XOR = 0xa0
    JA = 0x00
    JEQ = 0x10
    JGT = 0x20
    JGE = 0x30
    JSET = 0x40


class Src(enum.IntEnum):
    K = 0x00
    X = 0x08


class MiscOp(enum.IntEnum):
    TAX = 0x00
    TXA = 0x80


def bpf_jump(ops, k, jt, jf):
    return struct.pack('HBBI', ops, jt, jf, k)


def bpf_stmt(ops, k):
    return bpf_jump(ops, k, 0, 0)
