import pytest
import json
import os
import re
import mock

from dumbc import tokenize
from dumbc import Parser
from dumbc import DumbSyntaxError
from dumbc import DumbEOFError
from dumbc.utils.diagnostics import DiagnosticsEngine


dirname = os.path.abspath(os.path.dirname(__file__))

INLINE_MARKER_RE = re.compile(r'<<<<<<<<<<(.*)>>>>>>>>>>', re.DOTALL)
SAMPLES_DIR = 'data/parser_samples'


def verify_tree(root, tree_desc):
    """Verify a tree using an AST description.

    It's a little bit hard to test a parser. One way to test
    a parser is to run it on a big set of source files and
    compare AST produced by the parser and AST which we expect
    to have.

    Let's say we want to test a parser with input `123 + 3 * 4`.
    In order to do that we have to
      (a) describe expected AST(see below);
      (b) run actual parser;
      (c) compare ASTs.

    Expected AST is described with JSON format. For example, here
    is description of expected AST of expression `123 + 3 * 4`:
    {
        "type": "BinaryOp",
        "op": "PLUS",
        "left": 123,
        "right": {
            "type": "BinaryOp",
            "op": "STAR",
            "left": 3,
            "right": 4
        }
    }

    NOTE: use "type" field to indicate type of an AST node.
    NOTE: don't specify "type" field for primitive types.

    PS: Yeah, I know it's a little bit messed up function...
    """
    for key, expected_value in tree_desc.items():
        if key == 'type':
            assert type(root).__name__ == expected_value
            continue

        attr_val = getattr(root, key)

        if type(expected_value) is not dict:
            assert type(attr_val) == type(expected_value)

        if isinstance(expected_value, float):
            assert attr_val == pytest.approx(expected_value)
        elif isinstance(expected_value, list):
            for child_node, child_tree_desc in zip(attr_val, expected_value):
                if not isinstance(child_tree_desc, dict):
                    raise ValueError('invalid AST description.')
                verify_tree(child_node, child_tree_desc)
        elif isinstance(expected_value, dict):
            if 'type' not in expected_value:
                raise ValueError('invalid AST description.')
            verify_tree(attr_val, expected_value)
        else:
            assert attr_val == expected_value


def verify_forest(roots, forest_desc):
    for root, tree_desc in zip(roots, forest_desc):
        verify_tree(root, tree_desc)


def all_tests(kind):
    samples_dir = os.path.join(dirname, SAMPLES_DIR, kind)
    for dirpath, dirnames, files in os.walk(samples_dir):
        for file in files:
            yield os.path.join(dirpath, file)


def load_sample(filename):
    with open(filename, 'r') as f:
        data = f.read()
    desc_text = re.search(INLINE_MARKER_RE, data).groups()[0]
    desc = json.loads(desc_text)
    code = re.sub(INLINE_MARKER_RE, '', data)
    return code, desc


@pytest.fixture(params=all_tests('good'))
def good_input(request):
    filename = request.param
    return load_sample(filename)


@pytest.fixture(params=all_tests('bad'))
def bad_input(request):
    filename = request.param
    return load_sample(filename)


@pytest.fixture
def diag():
    return mock.Mock(spec=DiagnosticsEngine)


def test_output_ast(good_input, diag):
    code, desc = good_input
    token_stream = tokenize(code)
    parser = Parser(token_stream, diag)
    parse_method = getattr(parser, desc['hook'])

    ast = parse_method()

    if 'root' in desc:
        tree_desc = desc['root']
        verify_tree(ast, tree_desc)
    else:
        forest_desc = desc['forest']
        verify_forest(ast, forest_desc)


def test_bad_input(bad_input, diag):
    code, desc = bad_input

    token_stream = tokenize(code)
    parser = Parser(token_stream, diag)
    parse_method = getattr(parser, desc['hook'])

    with pytest.raises(DumbSyntaxError):
        parse_method()


def test_eof_handling(diag):
    code = ''
    token_stream = tokenize(code)
    parser = Parser(token_stream, diag)

    # Current token is EOF, so the next advance() method call
    # should cause an error.
    with pytest.raises(DumbEOFError):
        parser.advance()
