__all__ = ('tokenize',)

import collections
import re

from dumbc.errors import DumbValueError
from dumbc.ast import ast


Token = collections.namedtuple('Token', ('kind', 'value', 'loc'))


KEYWORDS = {
    'func',
    'return',

    'if',
    'else',

    'while',
    'break',
    'continue',

    'as',
    'var'
}

# (a token kind, regex to match the token kind)
TOKENS = (
    ('FLOAT', r'\d*\.\d+([eE][-+]?\d+)?'),
    ('INTEGER', r'\d+'),
    ('BOOL', r'true|false'),
    ('STR', r'"([^"\\]*(\\.[^"\\]*)*)"|\'([^\'\\]*(\\.[^\'\\]*)*)\''),
    ('IDENT', r'[a-zA-Z_][a-zA-Z_0-9]*'),

    ('SHLEQ', r'<<='),
    ('SHREQ', r'>>='),
    ('SHL', r'<<'),
    ('SHR', r'>>'),
    ('LOGICAL_OR', r'\|\|'),
    ('LOGICAL_AND', r'&&'),
    ('LE', r'<='),
    ('LT', r'<'),
    ('GE', r'>='),
    ('GT', r'>'),
    ('EQ', r'=='),
    ('NE', r'!='),
    ('PLUSEQ', r'\+='),
    ('PLUS', r'\+'),
    ('MINUSEQ', r'\-='),
    ('MINUS', r'\-'),
    ('STAREQ', r'\*='),
    ('STAR', r'\*'),
    ('SLASHEQ', r'/='),
    ('SLASH', r'/'),
    ('PERCENTEQ', r'%='),
    ('PERCENT', r'%'),
    ('OREQ', r'\|='),
    ('OR', r'\|'),
    ('ANDEQ', r'&='),
    ('AND', r'&'),
    ('XOREQ', r'\^='),
    ('XOR', r'\^'),
    ('LOGICAL_NOT', r'!'),
    ('ASSIGN', r'='),
    ('NOT', r'~'),

    ('ATTR_START', r'#\['),
    ('LEFT_PAREN', r'\('),
    ('RIGHT_PAREN', r'\)'),
    ('LEFT_CURLY_BRACKET', r'{'),
    ('RIGHT_CURLY_BRACKET', r'}'),
    ('LEFT_SQ_BRACKET', r'\['),
    ('RIGHT_SQ_BRACKET', r'\]'),
    ('COLON', r':'),
    ('SEMICOLON', r';'),
    ('COMMA', r','),

    ('COMMENT', r'#.*'),
    ('NEWLINE', r'\n'),
    ('WS', r'[ \t]+')
)


def tokenize(text):
    """Tokenize input string.

    Args:
        text (str): String with a source code.

    Yields:
        Token: Piece of the text that has some assigned
            meaning(a number, a keyword, etc).

    Raises:
        ValueError: Met some not "allowed" character.
    """

    tokens_regex = '|'.join('(?P<%s>%s)' % token for token in TOKENS)
    pat = re.compile(tokens_regex)
    scanner = pat.scanner(text)

    line = 1
    line_pos = -1
    pos = 0

    for m in iter(scanner.match, None):
        kind = m.lastgroup

        if kind == 'NEWLINE':
            line_pos = pos
            line += 1
        elif kind == 'WS' or kind == 'COMMENT':
            pass
        else:
            value = m.group()
            if kind == 'IDENT' and value in KEYWORDS:
                kind = value.upper()
            loc = ast.Location(line, pos - line_pos, len(value))
            yield Token(kind, value, loc)
        pos = m.end()

    if pos != len(text):
        raise DumbValueError('unexpected symbol at %d:%d' % (line, pos - line_pos))

    loc = ast.Location(line, pos - line_pos, 0)
    yield Token('EOF', None, loc)
