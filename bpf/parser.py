from pyparsing import pythonStyleComment, Keyword, Regex, OneOrMore, Word, hexnums, nums
from pyparsing import Suppress, MatchFirst, ZeroOrMore, Group, Combine, Optional, Literal

from .ops import A, K


OPERATOR = Literal('+') | Literal('-')
DECIMAL = Combine(Optional(OPERATOR) + Word(nums)).setParseAction(lambda t: int(t[0]))
HEXADECIMAL = Suppress("0x") + Word(hexnums).setParseAction(lambda t: int(t[0], 16))
VALUE = DECIMAL ^ HEXADECIMAL

A_ADDRESS = (Suppress('[') + VALUE + Suppress(']')).setParseAction(lambda t: A(int(t[0])))
K_ADDRESS = (Suppress('#') + VALUE).setParseAction(lambda t: K(int(t[0])))
ADDRESS = MatchFirst((A_ADDRESS, K_ADDRESS))

STATEMENT_OP = MatchFirst([
    Keyword("ld"),
    Keyword("ldh"),
    Keyword("ldb"),
    Keyword("ldx"),
    Keyword("ldxb"),
    Keyword("st"),
    Keyword("stx"),
    Keyword("add"),
    Keyword("sub"),
    Keyword("mul"),
    Keyword("div"),
    Keyword("mod"),
    Keyword("neg"),
    Keyword("and"),
    Keyword("or"),
    Keyword("xor"),
    Keyword("lsh"),
    Keyword("rsh"),
    Keyword("ja"),
    Keyword("ret"),
    Keyword("tax"),
    Keyword("txa"),
])

JUMP_OP = MatchFirst([
    Keyword("jeq"),
    Keyword("jneq"),
    Keyword("jne"),
    Keyword("jlt"),
    Keyword("jle"),
    Keyword("jgt"),
    Keyword("jge"),
    Keyword("jset"),
])

STATEMENT = Group(STATEMENT_OP('op') + ADDRESS('val'))('statement')
TARGET = Suppress(',') + ADDRESS
JUMP = Group(
    JUMP_OP('op')
    + ADDRESS('val')
    + TARGET('true')
    + Optional(TARGET)('false')
)('jump')

TOKEN = Group(STATEMENT ^ JUMP ^ Group(pythonStyleComment('comment')))
PROGRAM = ZeroOrMore(TOKEN)
