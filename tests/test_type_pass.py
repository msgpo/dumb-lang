import pytest

import dumbc.ast.ast as ast

from dumbc import BuiltinTypes
from dumbc import DumbTypeError
from dumbc import DumbNameError
from dumbc import Operator
from dumbc.transform.type_pass import TypePass
from dumbc.transform.type_pass import _builtin_type_conversion
from dumbc.transform.type_pass import _builtin_type_promotion


@pytest.mark.parametrize('left_ty,right_ty,result_ty', [
    (BuiltinTypes.I8,    BuiltinTypes.I8,     BuiltinTypes.I8),
    (BuiltinTypes.I8,    BuiltinTypes.U8,     BuiltinTypes.U8),
    (BuiltinTypes.I8,    BuiltinTypes.I32,    BuiltinTypes.I32),
    (BuiltinTypes.I8,    BuiltinTypes.U32,    BuiltinTypes.U32),
    (BuiltinTypes.I8,    BuiltinTypes.I64,    BuiltinTypes.I64),
    (BuiltinTypes.I8,    BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.I8,    BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.I8,    BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.I8,    BuiltinTypes.BOOL,   None),
    (BuiltinTypes.I8,    BuiltinTypes.STR,    None),
    (BuiltinTypes.I8,    BuiltinTypes.VOID,   None),
    (BuiltinTypes.U8,    BuiltinTypes.U8,     BuiltinTypes.U8),
    (BuiltinTypes.U8,    BuiltinTypes.I32,    BuiltinTypes.I32),
    (BuiltinTypes.U8,    BuiltinTypes.U32,    BuiltinTypes.U32),
    (BuiltinTypes.U8,    BuiltinTypes.I64,    BuiltinTypes.I64),
    (BuiltinTypes.U8,    BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.U8,    BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.U8,    BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.U8,    BuiltinTypes.BOOL,   None),
    (BuiltinTypes.U8,    BuiltinTypes.STR,    None),
    (BuiltinTypes.U8,    BuiltinTypes.VOID,   None),
    (BuiltinTypes.I32,   BuiltinTypes.I32,    BuiltinTypes.I32),
    (BuiltinTypes.I32,   BuiltinTypes.U32,    BuiltinTypes.U32),
    (BuiltinTypes.I32,   BuiltinTypes.I64,    BuiltinTypes.I64),
    (BuiltinTypes.I32,   BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.I32,   BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.I32,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.I32,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.I32,   BuiltinTypes.STR,    None),
    (BuiltinTypes.I32,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.U32,   BuiltinTypes.U32,    BuiltinTypes.U32),
    (BuiltinTypes.U32,   BuiltinTypes.I64,    BuiltinTypes.I64),
    (BuiltinTypes.U32,   BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.U32,   BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.U32,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.U32,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.U32,   BuiltinTypes.STR,    None),
    (BuiltinTypes.U32,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.I64,   BuiltinTypes.I64,    BuiltinTypes.I64),
    (BuiltinTypes.I64,   BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.I64,   BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.I64,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.I64,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.I64,   BuiltinTypes.STR,    None),
    (BuiltinTypes.I64,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.U64,   BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.U64,   BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.U64,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.U64,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.U64,   BuiltinTypes.STR,    None),
    (BuiltinTypes.U64,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.F32,   BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.F32,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.F32,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.F32,   BuiltinTypes.STR,    None),
    (BuiltinTypes.F32,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.F64,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.F64,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.F64,   BuiltinTypes.STR,    None),
    (BuiltinTypes.F64,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.BOOL,  BuiltinTypes.BOOL,   BuiltinTypes.BOOL),
    (BuiltinTypes.BOOL,  BuiltinTypes.STR,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.VOID,   None),
    (BuiltinTypes.STR,   BuiltinTypes.STR,    None),
    (BuiltinTypes.STR,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.VOID,  BuiltinTypes.STR,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.VOID,   None),
    (BuiltinTypes.U8,    BuiltinTypes.I8,     BuiltinTypes.U8),
    (BuiltinTypes.I32,   BuiltinTypes.I8,     BuiltinTypes.I32),
    (BuiltinTypes.U32,   BuiltinTypes.I8,     BuiltinTypes.U32),
    (BuiltinTypes.I64,   BuiltinTypes.I8,     BuiltinTypes.I64),
    (BuiltinTypes.U64,   BuiltinTypes.I8,     BuiltinTypes.U64),
    (BuiltinTypes.F32,   BuiltinTypes.I8,     BuiltinTypes.F32),
    (BuiltinTypes.F64,   BuiltinTypes.I8,     BuiltinTypes.F64),
    (BuiltinTypes.BOOL,  BuiltinTypes.I8,     None),
    (BuiltinTypes.STR,   BuiltinTypes.I8,     None),
    (BuiltinTypes.VOID,  BuiltinTypes.I8,     None),
    (BuiltinTypes.I32,   BuiltinTypes.U8,     BuiltinTypes.I32),
    (BuiltinTypes.U32,   BuiltinTypes.U8,     BuiltinTypes.U32),
    (BuiltinTypes.I64,   BuiltinTypes.U8,     BuiltinTypes.I64),
    (BuiltinTypes.U64,   BuiltinTypes.U8,     BuiltinTypes.U64),
    (BuiltinTypes.F32,   BuiltinTypes.U8,     BuiltinTypes.F32),
    (BuiltinTypes.F64,   BuiltinTypes.U8,     BuiltinTypes.F64),
    (BuiltinTypes.BOOL,  BuiltinTypes.U8,     None),
    (BuiltinTypes.STR,   BuiltinTypes.U8,     None),
    (BuiltinTypes.VOID,  BuiltinTypes.U8,     None),
    (BuiltinTypes.U32,   BuiltinTypes.I32,    BuiltinTypes.U32),
    (BuiltinTypes.I64,   BuiltinTypes.I32,    BuiltinTypes.I64),
    (BuiltinTypes.U64,   BuiltinTypes.I32,    BuiltinTypes.U64),
    (BuiltinTypes.F32,   BuiltinTypes.I32,    BuiltinTypes.F32),
    (BuiltinTypes.F64,   BuiltinTypes.I32,    BuiltinTypes.F64),
    (BuiltinTypes.BOOL,  BuiltinTypes.I32,    None),
    (BuiltinTypes.STR,   BuiltinTypes.I32,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.I32,    None),
    (BuiltinTypes.I64,   BuiltinTypes.U32,    BuiltinTypes.I64),
    (BuiltinTypes.U64,   BuiltinTypes.U32,    BuiltinTypes.U64),
    (BuiltinTypes.F32,   BuiltinTypes.U32,    BuiltinTypes.F32),
    (BuiltinTypes.F64,   BuiltinTypes.U32,    BuiltinTypes.F64),
    (BuiltinTypes.BOOL,  BuiltinTypes.U32,    None),
    (BuiltinTypes.STR,   BuiltinTypes.U32,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.U32,    None),
    (BuiltinTypes.U64,   BuiltinTypes.I64,    BuiltinTypes.U64),
    (BuiltinTypes.F32,   BuiltinTypes.I64,    BuiltinTypes.F32),
    (BuiltinTypes.F64,   BuiltinTypes.I64,    BuiltinTypes.F64),
    (BuiltinTypes.BOOL,  BuiltinTypes.I64,    None),
    (BuiltinTypes.STR,   BuiltinTypes.I64,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.I64,    None),
    (BuiltinTypes.F32,   BuiltinTypes.U64,    BuiltinTypes.F32),
    (BuiltinTypes.F64,   BuiltinTypes.U64,    BuiltinTypes.F64),
    (BuiltinTypes.BOOL,  BuiltinTypes.U64,    None),
    (BuiltinTypes.STR,   BuiltinTypes.U64,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.U64,    None),
    (BuiltinTypes.F64,   BuiltinTypes.F32,    BuiltinTypes.F64),
    (BuiltinTypes.BOOL,  BuiltinTypes.F32,    None),
    (BuiltinTypes.STR,   BuiltinTypes.F32,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.F32,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.F64,    None),
    (BuiltinTypes.STR,   BuiltinTypes.F64,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.F64,    None),
    (BuiltinTypes.STR,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.VOID,  BuiltinTypes.BOOL,   None),
])
def test_builtin_type_conversion(left_ty, right_ty, result_ty):
    assert _builtin_type_conversion(left_ty, right_ty) == result_ty


@pytest.mark.parametrize('from_ty,to_ty,result_ty', [
    (BuiltinTypes.I8,    BuiltinTypes.I8,     None),
    (BuiltinTypes.I8,    BuiltinTypes.U8,     BuiltinTypes.U8),
    (BuiltinTypes.I8,    BuiltinTypes.I32,    BuiltinTypes.I32),
    (BuiltinTypes.I8,    BuiltinTypes.U32,    BuiltinTypes.U32),
    (BuiltinTypes.I8,    BuiltinTypes.I64,    BuiltinTypes.I64),
    (BuiltinTypes.I8,    BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.I8,    BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.I8,    BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.I8,    BuiltinTypes.BOOL,   None),
    (BuiltinTypes.I8,    BuiltinTypes.STR,    None),
    (BuiltinTypes.I8,    BuiltinTypes.VOID,   None),
    (BuiltinTypes.U8,    BuiltinTypes.U8,     None),
    (BuiltinTypes.U8,    BuiltinTypes.I32,    BuiltinTypes.I32),
    (BuiltinTypes.U8,    BuiltinTypes.U32,    BuiltinTypes.U32),
    (BuiltinTypes.U8,    BuiltinTypes.I64,    BuiltinTypes.I64),
    (BuiltinTypes.U8,    BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.U8,    BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.U8,    BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.U8,    BuiltinTypes.BOOL,   None),
    (BuiltinTypes.U8,    BuiltinTypes.STR,    None),
    (BuiltinTypes.U8,    BuiltinTypes.VOID,   None),
    (BuiltinTypes.I32,   BuiltinTypes.I32,    None),
    (BuiltinTypes.I32,   BuiltinTypes.U32,    BuiltinTypes.U32),
    (BuiltinTypes.I32,   BuiltinTypes.I64,    BuiltinTypes.I64),
    (BuiltinTypes.I32,   BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.I32,   BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.I32,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.I32,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.I32,   BuiltinTypes.STR,    None),
    (BuiltinTypes.I32,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.U32,   BuiltinTypes.U32,    None),
    (BuiltinTypes.U32,   BuiltinTypes.I64,    BuiltinTypes.I64),
    (BuiltinTypes.U32,   BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.U32,   BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.U32,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.U32,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.U32,   BuiltinTypes.STR,    None),
    (BuiltinTypes.U32,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.I64,   BuiltinTypes.I64,    None),
    (BuiltinTypes.I64,   BuiltinTypes.U64,    BuiltinTypes.U64),
    (BuiltinTypes.I64,   BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.I64,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.I64,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.I64,   BuiltinTypes.STR,    None),
    (BuiltinTypes.I64,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.U64,   BuiltinTypes.U64,    None),
    (BuiltinTypes.U64,   BuiltinTypes.F32,    BuiltinTypes.F32),
    (BuiltinTypes.U64,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.U64,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.U64,   BuiltinTypes.STR,    None),
    (BuiltinTypes.U64,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.F32,   BuiltinTypes.F32,    None),
    (BuiltinTypes.F32,   BuiltinTypes.F64,    BuiltinTypes.F64),
    (BuiltinTypes.F32,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.F32,   BuiltinTypes.STR,    None),
    (BuiltinTypes.F32,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.F64,   BuiltinTypes.F64,    None),
    (BuiltinTypes.F64,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.F64,   BuiltinTypes.STR,    None),
    (BuiltinTypes.F64,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.BOOL,  BuiltinTypes.BOOL,   None),
    (BuiltinTypes.BOOL,  BuiltinTypes.STR,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.VOID,   None),
    (BuiltinTypes.STR,   BuiltinTypes.STR,    None),
    (BuiltinTypes.STR,   BuiltinTypes.VOID,   None),
    (BuiltinTypes.VOID,  BuiltinTypes.BOOL,   None),
    (BuiltinTypes.VOID,  BuiltinTypes.STR,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.VOID,   None),

    (BuiltinTypes.U8,    BuiltinTypes.I8,     None),
    (BuiltinTypes.I32,   BuiltinTypes.I8,     None),
    (BuiltinTypes.U32,   BuiltinTypes.I8,     None),
    (BuiltinTypes.I64,   BuiltinTypes.I8,     None),
    (BuiltinTypes.U64,   BuiltinTypes.I8,     None),
    (BuiltinTypes.F32,   BuiltinTypes.I8,     None),
    (BuiltinTypes.F64,   BuiltinTypes.I8,     None),
    (BuiltinTypes.BOOL,  BuiltinTypes.I8,     None),
    (BuiltinTypes.STR,   BuiltinTypes.I8,     None),
    (BuiltinTypes.VOID,  BuiltinTypes.I8,     None),
    (BuiltinTypes.I32,   BuiltinTypes.U8,     None),
    (BuiltinTypes.U32,   BuiltinTypes.U8,     None),
    (BuiltinTypes.I64,   BuiltinTypes.U8,     None),
    (BuiltinTypes.U64,   BuiltinTypes.U8,     None),
    (BuiltinTypes.F32,   BuiltinTypes.U8,     None),
    (BuiltinTypes.F64,   BuiltinTypes.U8,     None),
    (BuiltinTypes.BOOL,  BuiltinTypes.U8,     None),
    (BuiltinTypes.STR,   BuiltinTypes.U8,     None),
    (BuiltinTypes.VOID,  BuiltinTypes.U8,     None),
    (BuiltinTypes.U32,   BuiltinTypes.I32,    None),
    (BuiltinTypes.I64,   BuiltinTypes.I32,    None),
    (BuiltinTypes.U64,   BuiltinTypes.I32,    None),
    (BuiltinTypes.F32,   BuiltinTypes.I32,    None),
    (BuiltinTypes.F64,   BuiltinTypes.I32,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.I32,    None),
    (BuiltinTypes.STR,   BuiltinTypes.I32,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.I32,    None),
    (BuiltinTypes.I64,   BuiltinTypes.U32,    None),
    (BuiltinTypes.U64,   BuiltinTypes.U32,    None),
    (BuiltinTypes.F32,   BuiltinTypes.U32,    None),
    (BuiltinTypes.F64,   BuiltinTypes.U32,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.U32,    None),
    (BuiltinTypes.STR,   BuiltinTypes.U32,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.U32,    None),
    (BuiltinTypes.U64,   BuiltinTypes.I64,    None),
    (BuiltinTypes.F32,   BuiltinTypes.I64,    None),
    (BuiltinTypes.F64,   BuiltinTypes.I64,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.I64,    None),
    (BuiltinTypes.STR,   BuiltinTypes.I64,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.I64,    None),
    (BuiltinTypes.F32,   BuiltinTypes.U64,    None),
    (BuiltinTypes.F64,   BuiltinTypes.U64,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.U64,    None),
    (BuiltinTypes.STR,   BuiltinTypes.U64,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.U64,    None),
    (BuiltinTypes.F64,   BuiltinTypes.F32,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.F32,    None),
    (BuiltinTypes.STR,   BuiltinTypes.F32,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.F32,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.F64,    None),
    (BuiltinTypes.STR,   BuiltinTypes.F64,    None),
    (BuiltinTypes.VOID,  BuiltinTypes.F64,    None),
    (BuiltinTypes.STR,   BuiltinTypes.BOOL,   None),
    (BuiltinTypes.VOID,  BuiltinTypes.BOOL,   None),
    (BuiltinTypes.VOID,  BuiltinTypes.STR,    None),
    (BuiltinTypes.BOOL,  BuiltinTypes.VOID,   None),
    (BuiltinTypes.STR,   BuiltinTypes.VOID,   None)
])
def test_builtin_type_promotion(from_ty, to_ty, result_ty):
    assert _builtin_type_promotion(from_ty, to_ty) == result_ty


@pytest.fixture(params=[
    Operator.ADD,
    Operator.SUB,
    Operator.MUL,
    Operator.DIV,
    Operator.MOD
])
def arithmetic_binop(request):
    return request.param


@pytest.fixture(params=[
    Operator.LT,
    Operator.LE,
    Operator.GT,
    Operator.GE,
    Operator.EQ,
    Operator.NE
])
def relational_binop(request):
    return request.param


@pytest.fixture(params=[
    Operator.OR,
    Operator.AND,
    Operator.XOR
])
def bitwise_binop(request):
    return request.param


@pytest.fixture(params=[
    Operator.SHL,
    Operator.SHR
])
def shift_binop(request):
    return request.param


@pytest.fixture(params=[
    Operator.LOGICAL_OR,
    Operator.LOGICAL_AND
])
def logical_binop(request):
    return request.param


@pytest.mark.parametrize('value,expected_ty', [
    (ast.IntegerConstant(1), BuiltinTypes.I32),
    (ast.FloatConstant(1.0), BuiltinTypes.F32),
    (ast.BooleanConstant(True), BuiltinTypes.BOOL),
    (ast.StringConstant('foo'), BuiltinTypes.STR)
])
def test_builtin_literal_types(value, expected_ty):
    tp = TypePass()

    actual_ty = tp.visit(value)

    assert actual_ty == expected_ty


@pytest.mark.parametrize('left,right,expected_ty', [
    (ast.IntegerConstant(1), ast.IntegerConstant(2), BuiltinTypes.I32),
    (ast.IntegerConstant(1), ast.FloatConstant(2.0), BuiltinTypes.F32),
    (ast.FloatConstant(2.0), ast.IntegerConstant(1), BuiltinTypes.F32),
    (ast.FloatConstant(2.0), ast.FloatConstant(2.0), BuiltinTypes.F32),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.StringConstant('foo'), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.FloatConstant(1.0), ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.BooleanConstant(True), ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.StringConstant('foo'), ast.StringConstant('foo'), None)),
])
def test_arithmetic_binop(arithmetic_binop, left, right, expected_ty):
    root = ast.BinaryOp(arithmetic_binop, left, right)
    tp = TypePass()

    actual_ty = tp.visit(root)

    assert actual_ty == expected_ty


@pytest.mark.parametrize('left,right', [
    (ast.IntegerConstant(1), ast.IntegerConstant(2)),
    (ast.IntegerConstant(1), ast.FloatConstant(2.0)),
    (ast.FloatConstant(2.0), ast.IntegerConstant(1)),
    (ast.FloatConstant(2.0), ast.FloatConstant(1.0)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.BooleanConstant(True))),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.StringConstant('foo'))),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.FloatConstant(1.0), ast.BooleanConstant(True))),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.FloatConstant(1.0), ast.StringConstant('foo'))),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.StringConstant('foo'), ast.StringConstant('foo'))),
])
def test_relational_binop(relational_binop, left, right):
    root = ast.BinaryOp(relational_binop, left, right)
    tp = TypePass()

    actual_ty = tp.visit(root)

    assert actual_ty == BuiltinTypes.BOOL


@pytest.mark.parametrize('op,value,expected_ty', [
    (Operator.LOGICAL_NOT, ast.BooleanConstant(True), BuiltinTypes.BOOL),
    (Operator.NOT, ast.IntegerConstant(1), BuiltinTypes.I32),
    (Operator.UNARY_PLUS, ast.IntegerConstant(1), BuiltinTypes.I32),
    (Operator.UNARY_PLUS, ast.FloatConstant(1.0), BuiltinTypes.F32),
    (Operator.UNARY_MINUS, ast.IntegerConstant(1), BuiltinTypes.I32),
    (Operator.UNARY_MINUS, ast.FloatConstant(1.0), BuiltinTypes.F32),
    pytest.mark.xfail(raises=DumbTypeError)(
        (Operator.LOGICAL_NOT, ast.IntegerConstant(1), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (Operator.LOGICAL_NOT, ast.FloatConstant(1.0), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (Operator.LOGICAL_NOT, ast.StringConstant('foo'), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (Operator.NOT, ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (Operator.NOT, ast.FloatConstant(1.0), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (Operator.NOT, ast.StringConstant('foo'), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (Operator.UNARY_PLUS, ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (Operator.UNARY_MINUS, ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (Operator.UNARY_MINUS, ast.StringConstant('foo'), None)),
])
def test_unaryop(op, value, expected_ty):
    root = ast.UnaryOp(op, value)
    tp = TypePass()

    actual_ty = tp.visit(root)

    assert actual_ty == expected_ty


@pytest.mark.parametrize('left,right,expected_ty', [
    (ast.IntegerConstant(1), ast.IntegerConstant(2), BuiltinTypes.I32),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.FloatConstant(2.0), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.FloatConstant(2.0), ast.FloatConstant(2.0), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.BooleanConstant(True), ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.StringConstant('foo'), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.StringConstant('foo'), ast.StringConstant('foo'), None)),
])
def test_bitwise_binop(bitwise_binop, left, right, expected_ty):
    root = ast.BinaryOp(bitwise_binop, left, right)
    tp = TypePass()

    actual_ty = tp.visit(root)

    assert actual_ty == expected_ty


@pytest.mark.parametrize('left,right,expected_ty', [
    (ast.IntegerConstant(1), ast.IntegerConstant(2), BuiltinTypes.I32),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.FloatConstant(2.0), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.BooleanConstant(True), ast.BooleanConstant(True), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.StringConstant('foo'), None)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.StringConstant('foo'), ast.StringConstant('foo'), None)),
])
def test_shift_binop(shift_binop, left, right, expected_ty):
        root = ast.BinaryOp(shift_binop, left, right)
        tp = TypePass()

        actual_ty = tp.visit(root)

        assert actual_ty == expected_ty


@pytest.mark.parametrize('left,right', [
    (ast.BooleanConstant(True), ast.BooleanConstant(True)),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.IntegerConstant(1))),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.BooleanConstant(True))),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.FloatConstant(1.0), ast.FloatConstant(1.0))),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.IntegerConstant(1), ast.StringConstant('foo'))),
    pytest.mark.xfail(raises=DumbTypeError)(
        (ast.StringConstant('foo'), ast.StringConstant('foo'))),
])
def test_logical_binop(logical_binop, left, right):
    root = ast.BinaryOp(logical_binop, left, right)
    tp = TypePass()

    actual_ty = tp.visit(root)

    assert actual_ty == BuiltinTypes.BOOL


@pytest.mark.parametrize('value,ty', [
    (ast.IntegerConstant(1), BuiltinTypes.VOID),
    (ast.IntegerConstant(1), BuiltinTypes.STR)
])
def test_cast_bad_type(value, ty):
    root = ast.Cast(value, ty)
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_cast():
    root = ast.Cast(ast.FloatConstant(1.0),
                    BuiltinTypes.I32)
    tp = TypePass()

    actual_ty = tp.visit(root)

    assert actual_ty == BuiltinTypes.I32


def test_identifier_unknown():
    root = ast.Identifier('foo')
    tp = TypePass()

    with pytest.raises(DumbNameError):
        tp.visit(root)


def test_identifier():
    root = ast.Block([
        ast.Var('foo', ast.IntegerConstant(1), BuiltinTypes.I32),
        ast.Identifier('foo')
    ])
    tp = TypePass()

    tp.visit(root)


def test_funccall_wrong_num_args():
    foo_func = ast.Function(ast.FunctionProto('foo', [], BuiltinTypes.VOID))
    foo_call = ast.FuncCall('foo', [ast.IntegerConstant(1)])
    main_func = ast.Function(ast.FunctionProto('main', [], BuiltinTypes.VOID),
                             ast.Block([foo_call]))
    root = ast.TranslationUnit([foo_func, main_func])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


@pytest.mark.parametrize('arg_list,val_list', [
    ([ast.Argument('foo', BuiltinTypes.I32)], [ast.BooleanConstant(True)]),
    ([ast.Argument('foo', BuiltinTypes.I32)], [ast.FloatConstant(1.0)]),
])
def test_funccall_bad_arg(arg_list, val_list):
    foo_func = ast.Function(
        ast.FunctionProto('foo', arg_list, BuiltinTypes.VOID))
    foo_call = ast.FuncCall('foo', val_list)
    main_func = ast.Function(ast.FunctionProto('main', [], BuiltinTypes.VOID),
                             ast.Block([foo_call]))
    root = ast.TranslationUnit([foo_func, main_func])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_funccall_unknown_func():
    foo_call = ast.FuncCall('foo', [ast.IntegerConstant(0)])
    main_func = ast.Function(ast.FunctionProto('main', [], BuiltinTypes.VOID),
                             ast.Block([foo_call]))
    root = ast.TranslationUnit([main_func])
    tp = TypePass()

    with pytest.raises(DumbNameError):
        tp.visit(root)


def test_funccall_promote_arg():
    foo_func = ast.Function(
        ast.FunctionProto('foo',
                          [ast.Argument('foo', BuiltinTypes.F32)],
                          BuiltinTypes.VOID))
    foo_call = ast.FuncCall('foo', [ast.IntegerConstant(0)])
    main_func = ast.Function(ast.FunctionProto('main', [], BuiltinTypes.VOID),
                             ast.Block([foo_call]))
    root = ast.TranslationUnit([foo_func, main_func])
    tp = TypePass()

    tp.visit(root)


def test_funccall():
    foo_func = ast.Function(
        ast.FunctionProto('foo',
                          [ast.Argument('foo', BuiltinTypes.I32)],
                          BuiltinTypes.VOID))
    foo_call = ast.FuncCall('foo', [ast.IntegerConstant(0)])
    main_func = ast.Function(ast.FunctionProto('main', [], BuiltinTypes.VOID),
                             ast.Block([foo_call]))
    root = ast.TranslationUnit([foo_func, main_func])
    tp = TypePass()

    tp.visit(root)


def test_assignment_promotion():
    root = ast.Block([
        ast.Var('foo', ast.FloatConstant(0.0), BuiltinTypes.F32),
        ast.Assignment(ast.Identifier('foo'), ast.IntegerConstant(1))
    ])
    tp = TypePass()

    tp.visit(root)


def test_assignment_incompatible_types():
    root = ast.Block([
        ast.Var('foo', ast.IntegerConstant(0), BuiltinTypes.I32),
        ast.Assignment(ast.Identifier('foo'), ast.FloatConstant(1.0))
    ])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


@pytest.mark.parametrize('lvalue', [
    ast.IntegerConstant(1),
    ast.FloatConstant(1),
    ast.BooleanConstant(True)
])
def test_assignment_bad_lvalue(lvalue):
    root = ast.Block([
        ast.Assignment(lvalue, ast.IntegerConstant(1))
    ])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_assignment():
    root = ast.Block([
        ast.Var('foo', ast.IntegerConstant(0), BuiltinTypes.I32),
        ast.Assignment(ast.Identifier('foo'), ast.IntegerConstant(1))
    ])
    tp = TypePass()

    tp.visit(root)


def test_augmented_assignment_bad():
    root = ast.Block([
        ast.Var('foo', ast.IntegerConstant(0), BuiltinTypes.I32),
        ast.Assignment(ast.Identifier('foo'),
                       ast.IntegerConstant(1),
                       Operator.LOGICAL_OR)
    ])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_augmented_assignment():
    root = ast.Block([
        ast.Var('foo', ast.IntegerConstant(0), BuiltinTypes.I32),
        ast.Assignment(ast.Identifier('foo'),
                       ast.IntegerConstant(1),
                       Operator.ADD)
    ])
    tp = TypePass()

    tp.visit(root)


@pytest.mark.parametrize('cond', [
    ast.IntegerConstant(1),
    ast.FloatConstant(1.0),
    ast.BinaryOp(Operator.ADD, ast.IntegerConstant(0), ast.IntegerConstant(0)),
])
def test_if_bad_cond(cond):
    root = ast.If(cond, ast.Block([]))
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


@pytest.mark.parametrize('cond', [
    ast.BooleanConstant(True),
    ast.BinaryOp(Operator.LT, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.LE, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.GT, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.GE, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.EQ, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.NE, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.LOGICAL_OR,
                 ast.BooleanConstant(True),
                 ast.BooleanConstant(False)),
    ast.BinaryOp(Operator.LOGICAL_AND,
                 ast.BooleanConstant(True),
                 ast.BooleanConstant(False)),
])
def test_if(cond):
    root = ast.If(cond, ast.Block([]))
    tp = TypePass()

    tp.visit(root)


def test_if_with_else():
    cond = ast.BooleanConstant(True)
    root = ast.If(cond, ast.Block([]), ast.Block([]))
    tp = TypePass()

    tp.visit(root)


@pytest.mark.parametrize('cond', [
    ast.IntegerConstant(1),
    ast.FloatConstant(1.0),
    ast.BinaryOp(Operator.ADD, ast.IntegerConstant(0), ast.IntegerConstant(0)),
])
def test_while_bad_cond(cond):
    root = ast.While(cond, ast.Block([]))
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


@pytest.mark.parametrize('cond', [
    ast.BooleanConstant(True),
    ast.BinaryOp(Operator.LT, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.LE, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.GT, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.GE, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.EQ, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.NE, ast.IntegerConstant(0), ast.IntegerConstant(0)),
    ast.BinaryOp(Operator.LOGICAL_OR,
                 ast.BooleanConstant(True),
                 ast.BooleanConstant(False)),
    ast.BinaryOp(Operator.LOGICAL_AND,
                 ast.BooleanConstant(True),
                 ast.BooleanConstant(False)),
])
def test_while(cond):
    root = ast.While(cond, ast.Block([]))
    tp = TypePass()

    tp.visit(root)


def test_return_no_ret_no_val():
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], BuiltinTypes.VOID),
        ast.Block([
            ast.Return()
        ]))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    tp.visit(root)


def test_return_ret_val():
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], BuiltinTypes.I32),
        ast.Block([
            ast.Return(ast.IntegerConstant(1))
        ]))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    tp.visit(root)


def test_return_ret_no_val():
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], BuiltinTypes.I32),
        ast.Block([
            ast.Return()
        ]))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_return_no_ret_val():
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], BuiltinTypes.VOID),
        ast.Block([
            ast.Return(ast.IntegerConstant(1))
        ]))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_return_incompatible_val():
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], BuiltinTypes.I32),
        ast.Block([
            ast.Return(ast.FloatConstant(1.0))
        ]))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_return_promote_val():
    foo_func = ast.Function(
        ast.FunctionProto('foo', [], BuiltinTypes.F32),
        ast.Block([
            ast.Return(ast.IntegerConstant(1))
        ]))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    tp.visit(root)


def test_var():
    root = ast.Block([ast.Var('foo', ast.IntegerConstant(0))])
    tp = TypePass()

    tp.visit(root)


@pytest.mark.parametrize('value,ty', [
    (ast.FloatConstant(0.0), BuiltinTypes.I32),
    (ast.StringConstant('foo'), BuiltinTypes.I32),
])
def test_var_incompatible_types(value, ty):
    root = ast.Block([ast.Var('foo', value, ty)])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_var_with_promotion():
    root = ast.Block([
        ast.Var('foo',
                ast.IntegerConstant(0.0),
                BuiltinTypes.F32)
    ])
    tp = TypePass()

    tp.visit(root)


def test_var_unknown_type():
    root = ast.Block([
        ast.Var('foo',
                ast.FloatConstant(0.0),
                ast.Type('mytype'))
    ])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_func_redeclaration():
    foo_func = ast.Function(ast.FunctionProto('foo', [], BuiltinTypes.VOID))
    foo_func_dup = ast.Function(
        ast.FunctionProto('foo', [], BuiltinTypes.I32))
    root = ast.TranslationUnit([foo_func, foo_func_dup])
    tp = TypePass()

    with pytest.raises(DumbNameError):
        tp.visit(root)


def test_func_dup_arg():
    args = [
        ast.Argument('a', BuiltinTypes.I32),
        ast.Argument('a', BuiltinTypes.I32)
    ]
    foo_func = ast.Function(
        ast.FunctionProto('foo', args, BuiltinTypes.VOID))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    with pytest.raises(DumbNameError):
        tp.visit(root)


def test_func_bad_arg_type():
    args = [
        ast.Argument('a', BuiltinTypes.VOID)
    ]
    foo_func = ast.Function(
        ast.FunctionProto('foo', args, BuiltinTypes.VOID))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    with pytest.raises(DumbTypeError):
        tp.visit(root)


def test_func_proto():
    args = [
        ast.Argument('a', BuiltinTypes.I32),
        ast.Argument('b', BuiltinTypes.I32)
    ]
    foo_func = ast.Function(
        ast.FunctionProto('foo', args, BuiltinTypes.VOID))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    tp.visit(root)


def test_func():
    args = [
        ast.Argument('a', BuiltinTypes.I32),
        ast.Argument('b', BuiltinTypes.I32)
    ]
    foo_func = ast.Function(
        ast.FunctionProto('foo', args, BuiltinTypes.VOID),
        ast.Block([]))
    root = ast.TranslationUnit([foo_func])
    tp = TypePass()

    tp.visit(root)
