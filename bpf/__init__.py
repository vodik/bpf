import ctypes
import enum
import socket
import struct

from hexdump import hexdump

from aioraw.constants import SO_ATTACH_FILTER
from aioraw.constants import ETH_P_IP
from .ops import Class, Op, Size, bpf_jump, bpf_stmt


class bpf(list):
    def compile(self):
        buf = ctypes.create_string_buffer(bytes(self))
        return struct.pack('HL', len(self), ctypes.addressof(buf)), buf

    def __bytes__(self):
        return b''.join(self)


def attach_program(sock, bpf):
    bpf_repr, program = bpf.compile()
    sock.setsockopt(socket.SOL_SOCKET, SO_ATTACH_FILTER, bpf_repr)
    return program


OP_TABLE = {
    'ld': lambda v: bpf_stmt(Class.LD.op(Size.W, v.bpf_type), v),
    'ldh': lambda v: bpf_stmt(Class.LD.op(Size.H, v.bpf_type), v),
    'ldb': lambda v: bpf_stmt(Class.LD.op(Size.B, v.bpf_type), v),

    'ldx': lambda v: bpf_stmt(Class.LDX.op(Size.W, v.bpf_type), v),
    'ldxb': lambda v: bpf_stmt(Class.LDX.op(Size.H, v.bpf_type), v),

    'st': lambda v: bpf_stmt(Class.ST.op(), v),
    'stx': lambda v: bpf_stmt(Class.STX.op(), v),

    'add': lambda v: bpf_stmt(Class.ALU.op(Op.ADD, v.bpf_type), v),
    'sub': lambda v: bpf_stmt(Class.ALU.op(Op.SUB, v.bpf_type), v),
    'mul': lambda v: bpf_stmt(Class.ALU.op(Op.MUL, v.bpf_type), v),
    'div': lambda v: bpf_stmt(Class.ALU.op(Op.DIV, v.bpf_type), v),
    'mod': lambda v: bpf_stmt(Class.ALU.op(Op.MOD, v.bpf_type), v),
    'neg': lambda v: bpf_stmt(Class.ALU.op(Op.NEG, v.bpf_type), v),
    'and': lambda v: bpf_stmt(Class.ALU.op(Op.AND, v.bpf_type), v),
    'or': lambda v: bpf_stmt(Class.ALU.op(Op.OR, v.bpf_type), v),
    'xor': lambda v: bpf_stmt(Class.ALU.op(Op.XOR, v.bpf_type), v),
    'lsh': lambda v: bpf_stmt(Class.ALU.op(Op.LSH, v.bpf_type), v),
    'rsh': lambda v: bpf_stmt(Class.ALU.op(Op.RSH, v.bpf_type), v),

    'ja': lambda v, t, f: bpf_stmt(Class.JMP.op(Op.JA), v),

    'ret': lambda v: bpf_stmt(Class.RET.op(v.bpf_type), v),

    'tax': lambda v: bpf_stmt(Class.MISC.op(Op.TAX), v),
    'txa': lambda v: bpf_stmt(Class.MISC.op(Op.TXA), v)
}

JMP_TABLE = {
    'jeq': lambda v, t, f: bpf_jump(Class.JMP.op(Op.JEQ, v.bpf_type), v, t, f),
    'jneq': lambda v, t, f: bpf_jump(Class.JMP.op(Op.JEQ, v.bpf_type), v, f, t),
    'jne': lambda v, t, f: bpf_jump(Class.JMP.op(Op.JEQ, v.bpf_type), v, f, t),
    'jlt': lambda v, t, f: bpf_jump(Class.JMP.op(Op.JGE, v.bpf_type), v, f, t),
    'jle': lambda v, t, f: bpf_jump(Class.JMP.op(Op.JGT, v.bpf_type), v, f, t),
    'jgt': lambda v, t, f: bpf_jump(Class.JMP.op(Op.JGT, v.bpf_type), v, t, f),
    'jge': lambda v, t, f: bpf_jump(Class.JMP.op(Op.JGE, v.bpf_type), v, t, f),
    'jset': lambda v, t, f: bpf_jump(Class.JMP.op(Op.JSET, v.bpf_type), v, t, f)
}


def compile(program):
    from .parser import PROGRAM

    def emit_ops(ops):
        for line in ops:
            statement = line.get('statement')
            jump = line.get('jump')

            if statement:
                op = statement.get('op')
                val = statement.get('val')

                val = type(val)(ctypes.c_uint32(val).value)

                stmt = OP_TABLE.get(op)
                if not stmt:
                    raise NotImplementedError(op)

                yield stmt(val)
            elif jump:
                op = jump.get('op')
                val = jump.get('val')

                stmt = JMP_TABLE.get(op)
                if not stmt:
                    raise NotImplementedError(op)

                yield stmt(val,
                           jump['true'][0],
                           jump.get('false', [0])[0])

    output = PROGRAM.parseString(program, parseAll=True)
    return bpf(emit_ops(output))
