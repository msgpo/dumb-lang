import itertools
import os
import pytest

from dumbc import tokenize
from dumbc import DumbValueError
from dumbc.parser.lexer import KEYWORDS


dirname = os.path.abspath(os.path.dirname(__file__))

SPLIT_MARKER = '***** Tokens *****'
SAMPLES_DIR = 'data/lexer_samples'


def extract_field(seq, field):
    without_eof = itertools.takewhile(lambda t: t.kind != 'EOF', seq)
    fields = map(lambda e: getattr(e, field), without_eof)
    return fields


def get_kind_list(code):
    tokens = tokenize(code)
    return list(extract_field(tokens, 'kind'))


def get_loc_list(code):
    tokens = tokenize(code)
    t1, t2 = itertools.tee(tokens, 2)
    loc = extract_field(t1, 'loc')
    return list(loc)


@pytest.mark.parametrize('bad_input', [
    '$foo = 1',
    'vlad@example.com and pizza',
    '123.e123',
    '123.e-123',
    '.e33333',
    '.e-33333'
])
def test_invalid_input(bad_input):
    with pytest.raises(DumbValueError):
        get_kind_list(bad_input)


@pytest.mark.parametrize('text,tokens', [
    ('123',        ['INTEGER']),
    ('123.0',      ['FLOAT']),
    ('.123',       ['FLOAT']),
    ('123.3E123',  ['FLOAT']),
    ('123.3E-123', ['FLOAT']),
    ('123.3e123',  ['FLOAT']),
    ('123.3e-123', ['FLOAT']),
])
def test_integral(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('text,tokens', [
    ('true',  ['BOOL']),
    ('false', ['BOOL']),
])
def test_boolean(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('text,tokens', [
    (r'"hello"', ['STR']),
    (r'"hello, \"dude\""', ['STR']),
    (r"'hello'", ['STR']),
    (r"'hello, \'dude\''", ['STR'])
])
def test_string(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('text,tokens', [
    ('_',     ['IDENT']),
    ('a',     ['IDENT']),
    ('boo',   ['IDENT']),
    ('bar_1', ['IDENT']),
])
def test_ident(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('text,tokens', [
    ('+=',  ['PLUSEQ']),
    ('-=',  ['MINUSEQ']),
    ('*=',  ['STAREQ']),
    ('/=',  ['SLASHEQ']),
    ('%=',  ['PERCENTEQ']),
    ('|=',  ['OREQ']),
    ('&=',  ['ANDEQ']),
    ('^=',  ['XOREQ']),
    ('<<=', ['SHLEQ']),
    ('>>=', ['SHREQ']),
])
def test_assignment(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('keyword', KEYWORDS)
def test_keyword(keyword):
    assert get_kind_list(keyword) == [keyword.upper()]


@pytest.mark.parametrize('text,tokens', [
    ('<<', ['SHL']),
    ('>>', ['SHR']),
    ('<',  ['LT']),
    ('<=', ['LE']),
    ('>',  ['GT']),
    ('>=', ['GE']),
    ('==', ['EQ']),
    ('!=', ['NE']),
    ('+',  ['PLUS']),
    ('-',  ['MINUS']),
    ('*',  ['STAR']),
    ('/',  ['SLASH']),
    ('%',  ['PERCENT']),
    ('|',  ['OR']),
    ('&',  ['AND']),
    ('^',  ['XOR']),
    ('=',  ['ASSIGN']),
    ('||', ['LOGICAL_OR']),
    ('&&', ['LOGICAL_AND']),
])
def test_binop(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('text,tokens', [
    ('!', ['LOGICAL_NOT']),
    ('~', ['NOT'])
])
def test_unary(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('text,tokens', [
    ('# hello world *&@\n# another one', []),
    ('# pizza\n+', ['PLUS']),
])
def test_comment(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('text,tokens', [
    ('#[', ['ATTR_START']),
    ('# [', []),
])
def test_attr_start(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('text,tokens', [
    ('(', ['LEFT_PAREN']),
    (')', ['RIGHT_PAREN']),
    ('{', ['LEFT_CURLY_BRACKET']),
    ('}', ['RIGHT_CURLY_BRACKET']),
    ('[', ['LEFT_SQ_BRACKET']),
    (']', ['RIGHT_SQ_BRACKET']),
])
def test_brackets(text, tokens):
    assert get_kind_list(text) == tokens


@pytest.mark.parametrize('text,tokens', [
    (':', ['COLON']),
    (';', ['SEMICOLON']),
    (',', ['COMMA']),
])
def test_misc(text, tokens):
    assert get_kind_list(text) == tokens


def test_loc():
    code = '+-\n3454 2   3\n\nabcd'
    loc_list = [
        (1, 1, 1), # +
        (1, 2, 1), # -
        (2, 1, 4), # 3454
        (2, 6, 1), # 2
        (2, 10, 1), # 3
        (4, 1, 4)] # abcd
    assert get_loc_list(code) == loc_list


def all_samples():
    samples_dir = os.path.join(dirname, SAMPLES_DIR)
    for dirpath, dirnames, files in os.walk(samples_dir):
        for file in files:
            yield os.path.join(dirpath, file)


@pytest.fixture(params=all_samples())
def tokenized_sample(request):
    with open(request.param, 'r') as f:
        text = f.read()
    code, tokens_text = text.split(SPLIT_MARKER)
    tokens = tokens_text.strip().split('\n')
    return code, tokens


def test_tokenize_sample(tokenized_sample):
    code, tokens = tokenized_sample
    assert get_kind_list(code) == tokens
