import pytest

import dumbc.ast.ast as ast

from dumbc.errors import DumbNameError
from dumbc.errors import DumbTypeError
from dumbc.transform.main_func_pass import MainFuncPass


def test_with_main_func():
    root = ast.TranslationUnit([
        ast.Function(ast.FunctionProto('foo', [], ast.BuiltinTypes.VOID)),
        ast.Function(ast.FunctionProto('main', [], ast.BuiltinTypes.I32))
    ])
    mfp = MainFuncPass()

    mfp.visit(root)


def test_without_main_func():
    root = ast.TranslationUnit([
        ast.Function(ast.FunctionProto('foo', [], ast.BuiltinTypes.VOID))
    ])
    mfp = MainFuncPass()

    with pytest.raises(DumbNameError):
        mfp.visit(root)


def test_main_func_bad_ret_ty():
    root = ast.TranslationUnit([
        ast.Function(ast.FunctionProto('foo', [], ast.BuiltinTypes.VOID)),
        ast.Function(ast.FunctionProto('main', [], ast.BuiltinTypes.VOID))
    ])
    mfp = MainFuncPass()

    with pytest.raises(DumbTypeError):
        mfp.visit(root)
