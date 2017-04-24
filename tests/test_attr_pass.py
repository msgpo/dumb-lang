import pytest
import dumbc.ast.ast as ast

from dumbc.errors import DumbTypeError
from dumbc.errors import DumbNameError
from dumbc.transform.attr_pass import AttrPass


def test_no_attrs_has_body():
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], ast.BuiltinTypes.I32),
        ast.Block([
            ast.Return()
        ]))
    ap = AttrPass()
    ap.visit(foo_func)


def test_no_attrs_no_body():
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], ast.BuiltinTypes.I32))
    ap = AttrPass()
    with pytest.raises(DumbTypeError):
        ap.visit(foo_func)


def test_external_attr_has_body():
    attrs = [ast.Attribute('external')]
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], ast.BuiltinTypes.I32, attrs),
        ast.Block([
            ast.Return()
        ]))
    ap = AttrPass()
    with pytest.raises(DumbTypeError):
        ap.visit(foo_func)


def test_external_attr_no_body():
    attrs = [ast.Attribute('external')]
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], ast.BuiltinTypes.I32, attrs))
    ap = AttrPass()
    ap.visit(foo_func)


def test_external_attr_with_args():
    attrs = [ast.Attribute('external',
                           args=(ast.BooleanConstant(True),))]
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], ast.BuiltinTypes.I32, attrs))
    ap = AttrPass()
    with pytest.raises(DumbTypeError):
        ap.visit(foo_func)


def test_unknown_attr():
    attrs = [ast.Attribute('foobar')]
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], ast.BuiltinTypes.I32, attrs))
    ap = AttrPass()
    with pytest.raises(DumbNameError):
        ap.visit(foo_func)
