from collections import defaultdict

import dumbc.ast.ast as ast

from dumbc.errors import DumbTypeError
from dumbc.errors import DumbNameError
from dumbc.ast.ast import Type
from dumbc.ast.ast import BuiltinTypes
from dumbc.ast.ast import Operator
from dumbc.transform.base_pass import Pass
from dumbc.utils.symbol_table import SymbolTable


def _parse_integral_type(ty):
    # Integral types have a form r'[iuf]\d+'.
    return ty.name[0], int(ty.name[1:])


def _integral_conversion(left_ty, right_ty):
    if left_ty == BuiltinTypes.F64 or right_ty == BuiltinTypes.F64:
        return BuiltinTypes.F64
    if left_ty == BuiltinTypes.F32 or right_ty == BuiltinTypes.F32:
        return BuiltinTypes.F32
    left_kind, left_nbits = _parse_integral_type(left_ty)
    right_kind, right_nbits = _parse_integral_type(right_ty)
    if left_kind == right_kind:
        result_kind = left_kind
    elif left_kind == 'u' and left_nbits < right_nbits:
        result_kind = 'i'
    elif right_kind == 'u' and right_nbits < left_nbits:
        result_kind = 'i'
    else:
        result_kind = 'u'
    result_nbits = max(left_nbits, right_nbits)
    result_ty = result_kind + str(result_nbits)
    return getattr(BuiltinTypes, result_ty.upper())


def _integral_promotion(from_ty, to_ty):
    if from_ty == to_ty:
        return None
    if to_ty == BuiltinTypes.F64:
        return to_ty
    if to_ty == BuiltinTypes.F32 and from_ty != BuiltinTypes.F64:
        return to_ty
    from_kind, from_nbits = _parse_integral_type(from_ty)
    to_kind, to_nbits = _parse_integral_type(to_ty)
    if from_kind == 'u' and from_nbits < to_nbits:
        return to_ty
    elif from_kind == 'i' and from_nbits <= to_nbits:
        return to_ty
    return None


def _boolean_conversion(left_ty, right_ty):
    if left_ty == right_ty:
        return left_ty
    return None


def _builtin_type_conversion(left_ty, right_ty):
    static_types = (BuiltinTypes.STR, BuiltinTypes.VOID)
    if left_ty in static_types or right_ty in static_types:
        return None
    if left_ty == BuiltinTypes.BOOL or right_ty == BuiltinTypes.BOOL:
        return _boolean_conversion(left_ty, right_ty)
    return _integral_conversion(left_ty, right_ty)


def _builtin_type_promotion(from_ty, to_ty):
    numerical_types = BuiltinTypes.NUMERICAL
    if from_ty in numerical_types and to_ty in numerical_types:
        return _integral_promotion(from_ty, to_ty)
    return None


def _validate_bitwise_binop(node, left_ty, right_ty):
    integer_types = BuiltinTypes.INTEGERS
    if left_ty not in integer_types or right_ty not in integer_types:
        msg = 'invalid operands to bitwise expression (%r and %r)' % (
            left_ty.name, right_ty.name)
        raise DumbTypeError(msg, loc=node.loc)


def _validate_shift_binop(node, left_ty, right_ty):
    integer_types = BuiltinTypes.INTEGERS
    if left_ty not in integer_types or right_ty not in integer_types:
        msg = 'invalid operands to shift expression (%r and %r)' % (
            left_ty.name, right_ty.name)
        raise DumbTypeError(msg, loc=node.loc)


def _validate_logical_binop(node, left_ty, right_ty):
    if node.op in (Operator.EQ, Operator.NE):
        return
    if left_ty != BuiltinTypes.BOOL or right_ty != BuiltinTypes.BOOL:
        msg = 'invalid operand types to logical expression (%r and %r)' % (
            left_ty.name, right_ty.name)
        raise DumbTypeError(msg, loc=node.loc)


def _validate_arithmetic_binop(node, left_ty, right_ty):
    numerical_types = BuiltinTypes.NUMERICAL
    if left_ty not in numerical_types or right_ty not in numerical_types:
        msg = 'invalid operands to arithmetic expression (%r and %r)' % (
            left_ty.name, right_ty.name)
        raise DumbTypeError(msg, loc=node.loc)


def _validate_assignment(node, left_ty, right_ty):
    if not isinstance(node.lvalue, ast.Identifier):
        msg = 'lvalue required as left operand of assignment'
        raise DumbTypeError(msg, loc=node.loc)


def _validate_logical_not_unaryop(node, value_ty):
    if value_ty != BuiltinTypes.BOOL:
        msg = 'invalid operand type %r' % value_ty.name
        raise DumbTypeError(msg, loc=node.loc)


def _validate_not_unaryop(node, value_ty):
    if value_ty not in BuiltinTypes.INTEGERS:
        msg = 'invalid operand type %r (integer type expected)' % value_ty.name
        raise DumbTypeError(msg, loc=node.loc)


def _validate_arithmetic_unaryop(node, value_ty):
    if value_ty not in BuiltinTypes.NUMERICAL:
        msg = 'invalid operand type %r (integral type expected)' % value_ty.name
        raise DumbTypeError(msg, loc=node.loc)


def _validate_cast(node, src_ty, dst_ty):
    if dst_ty in (BuiltinTypes.STR, BuiltinTypes.VOID):
        msg = 'invalid type'
        raise DumbTypeError(msg, loc=node.loc)


class TypePass(Pass):
    """Type checking semantic analysis pass."""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.func_table = SymbolTable()

    def visit_BinaryOp(self, node):
        op = node.op
        left_ty = self.visit(node.left)
        right_ty = self.visit(node.right)
        result_ty = _builtin_type_conversion(left_ty, right_ty)
        if result_ty is None:
            msg = 'invalid operands to binary expression (%r and %r)' % (
                left_ty.name, right_ty.name)
            raise DumbTypeError(msg, loc=node.loc)
        if Operator.logical(op):
            _validate_logical_binop(node, left_ty, right_ty)
        elif Operator.bitwise(op):
            _validate_bitwise_binop(node, left_ty, right_ty)
        elif Operator.shift(op):
            _validate_shift_binop(node, left_ty, right_ty)
        else:
            _validate_arithmetic_binop(node, left_ty, right_ty)
        # Promote left and right operand to the common type.
        node.ty = result_ty
        left_promote_ty = _builtin_type_promotion(left_ty, result_ty)
        right_promote_ty = _builtin_type_promotion(right_ty, result_ty)
        if left_promote_ty:
            node.left = ast.Cast(node.left, left_promote_ty, left_ty)
        if right_promote_ty:
            node.right = ast.Cast(node.right, right_promote_ty, right_ty)
        if Operator.relational(op):
            result_ty = BuiltinTypes.BOOL
        return result_ty

    def visit_Assignment(self, node):
        lvalue_ty = self.visit(node.lvalue)
        rvalue_ty = self.visit(node.rvalue)
        node.ty = lvalue_ty
        _validate_assignment(node, lvalue_ty, rvalue_ty)
        if node.op is not None:
            expr = ast.BinaryOp(node.op, node.lvalue, node.rvalue,
                                loc=node.loc)
            self.visit(expr)
        if lvalue_ty == rvalue_ty:
            return lvalue_ty
        promote_to = _builtin_type_promotion(rvalue_ty, lvalue_ty)
        if not promote_to:
            msg = 'cannot implicitly cast %r to %r' % (
                rvalue_ty.name, lvalue_ty.name)
            raise DumbTypeError(msg, loc=node.loc)
        node.rvalue = ast.Cast(node.rvalue, lvalue_ty, rvalue_ty)
        return lvalue_ty

    def visit_UnaryOp(self, node):
        op = node.op
        value_ty = self.visit(node.value)
        node.ty = value_ty
        if op == Operator.LOGICAL_NOT:
            _validate_logical_not_unaryop(node, value_ty)
        elif op == Operator.NOT:
            _validate_not_unaryop(node, value_ty)
        elif op in (Operator.UNARY_PLUS, Operator.UNARY_MINUS):
            _validate_arithmetic_unaryop(node, value_ty)

        return value_ty

    def visit_Cast(self, node):
        value_ty = self.visit(node.value)
        node.src_ty = value_ty
        _validate_cast(node, value_ty, node.dst_ty)
        return node.dst_ty

    def visit_IntegerConstant(self, node):
        return BuiltinTypes.I32

    def visit_FloatConstant(self, node):
        return BuiltinTypes.F32

    def visit_BooleanConstant(self, node):
        return BuiltinTypes.BOOL

    def visit_StringConstant(self, node):
        return BuiltinTypes.STR

    def visit_Identifier(self, node):
        ty = self.symbol_table.get(node.name)
        if ty is None:
            msg = 'name %r is not defined.' % node.name
            raise DumbNameError(msg, loc=node.loc)
        return ty

    def visit_FuncCall(self, node):
        func = self.func_table.get(node.name)
        if not func:
            msg = 'name %r is not defined' % node.name
            raise DumbNameError(msg, loc=node.loc)
        proto = func.proto
        if len(node.args) != len(proto.args):
            msg = '%s() takes %d arguments (%d given)' % (
                proto.name, len(proto.args), len(node.args))
            raise DumbTypeError(msg, loc=node.loc)
        for i, value in enumerate(node.args):
            arg_ty = proto.args[i].ty
            value_ty = self.visit(value)
            if arg_ty == value_ty:
                continue
            promote_to = _builtin_type_promotion(value_ty, arg_ty)
            if not promote_to:
                msg = 'cannot implicitly cast %r to %r' % (
                    value_ty.name, arg_ty.name)
                raise DumbTypeError(msg, loc=node.loc)
            node.args[i] = ast.Cast(value, arg_ty, value_ty)
        return proto.ret_ty

    def visit_Block(self, node):
        self.symbol_table.push()
        for stmt in node.stmts:
            ty = self.visit(stmt)
        self.symbol_table.pop()

    def visit_If(self, node):
        cond_ty = self.visit(node.cond)
        if cond_ty != BuiltinTypes.BOOL:
            msg = "condition expression must be of the type 'bool'"
            raise DumbTypeError(msg, loc=node.loc)
        self.visit(node.then)
        if node.otherwise is not None:
            self.visit(node.otherwise)

    def visit_While(self, node):
        cond_ty = self.visit(node.cond)
        if cond_ty != BuiltinTypes.BOOL:
            msg = "condition expression must be of the type 'bool'"
            raise DumbTypeError(msg, loc=node.loc)
        self.visit(node.body)

    def visit_Return(self, node):
        proto = self.curr_function.proto
        if proto.ret_ty == BuiltinTypes.VOID and node.value is not None:
            msg = 'unexpected return value'
            raise DumbTypeError(msg, loc=node.loc)
        if proto.ret_ty != BuiltinTypes.VOID and node.value is None:
            msg = 'expected %r return value' % proto.ret_ty.name
            raise DumbTypeError(msg, loc=node.loc)
        if not node.value:
            return
        value_ty = self.visit(node.value)
        if value_ty == proto.ret_ty:
            return
        promote_to = _builtin_type_promotion(value_ty, proto.ret_ty)
        if not promote_to:
            msg = 'cannot implicitly cast %r to %r' % (
                value_ty.name, proto.ret_ty.name)
            raise DumbTypeError(msg, loc=node.loc)
        node.value = ast.Cast(node.value, proto.ret_ty, value_ty, loc=node.loc)

    def visit_Var(self, node):
        value_ty = self.visit(node.initial_value)
        if not node.ty:
            node.ty = value_ty
        elif node.ty not in BuiltinTypes.VAR_TYPES:
            raise DumbTypeError('unknown type %r' % node.ty.name, loc=node.loc)
        if node.ty != value_ty:
            promote_to = _builtin_type_promotion(value_ty, node.ty)
            if promote_to:
                node.initial_value = ast.Cast(node.initial_value,
                                              promote_to,
                                              value_ty)
            else:
                msg = 'cannot implicitly cast %r to %r' % (
                    value_ty.name, node.ty.name)
                raise DumbTypeError(msg, loc=node.loc)
        self.symbol_table.set(node.name, node.ty)

    def visit_Function(self, node):
        self.symbol_table.push()
        for arg in node.proto.args:
            if self.symbol_table.has(arg.name):
                msg = 'name %r has been defined' % arg.name
                raise DumbNameError(msg, loc=arg.loc)
            if arg.ty == BuiltinTypes.VOID:
                msg = 'invalid argument type (%r)' % arg.ty.name
                raise DumbTypeError(msg, loc=arg.loc)
            self.symbol_table.set(arg.name, arg.ty)
        if node.body:
            self.curr_function = node
            self.visit(node.body)
            self.curr_function = None
        self.symbol_table.pop()

    def _populate_func_table(self, translation_unit):
        self.func_table.push()
        for decl in translation_unit.decls:
            if not isinstance(decl, ast.Function): # pragma: no cover
                continue
            proto = decl.proto
            if self.func_table.has(proto.name):
                raise DumbNameError('name %r has been defined' % proto.name,
                                    loc=decl.loc)
            self.func_table.set(proto.name, decl)

    def visit_TranslationUnit(self, node):
        self._populate_func_table(node)
        for decl in node.decls:
            self.visit(decl)
        self.func_table.pop()
