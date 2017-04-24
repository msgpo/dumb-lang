import dumbc.ast.ast as ast

from llvmlite import ir

from dumbc.ast.ast import Operator
from dumbc.ast.ast import BuiltinTypes
from dumbc.ast.visitor import ExprVisitor
from dumbc.codegen.utils import NBITS
from dumbc.codegen.utils import convert_to_llvm_ty

# TODO: refactor this crap out


_CMP_OP = {
    Operator.LT: '<',
    Operator.LE: '<=',
    Operator.GT: '>',
    Operator.GE: '>=',
    Operator.EQ: '==',
    Operator.NE: '!='
}

_SI_BINOP_METHODS = {
    Operator.ADD: 'add',
    Operator.SUB: 'sub',
    Operator.MUL: 'mul',
    Operator.DIV: 'sdiv',
    Operator.MOD: 'srem',
    Operator.AND: 'and_',
    Operator.OR:  'or_',
    Operator.XOR: 'xor',
    Operator.SHL: 'shl',
    Operator.SHR: 'ashr'
}

_UI_BINOP_METHODS = {
    Operator.ADD: 'add',
    Operator.SUB: 'sub',
    Operator.MUL: 'mul',
    Operator.DIV: 'udiv',
    Operator.MOD: 'urem',
    Operator.AND: 'and_',
    Operator.OR:  'or_',
    Operator.XOR: 'xor',
    Operator.SHL: 'shl',
    Operator.SHR: 'lshr'
}

_FP_BINOP_METHODS = {
    Operator.ADD: 'fadd',
    Operator.SUB: 'fsub',
    Operator.MUL: 'fmul',
    Operator.DIV: 'fdiv',
    Operator.MOD: 'frem'
}


def _make_global_constant(module, value, name): # pragma: nocover
    name = module.get_unique_name(name)
    const = ir.GlobalVariable(module, value.type, name=name)
    const.global_constant = True
    const.initializer = value
    const.linkage = 'internal'
    return const


class ExpressionCodegen(ExprVisitor): # pragma: nocover

    def __init__(self, ctx):
        self.ctx = ctx

    def _apply_binop(self, node, binop_methods, cmp_func):
        builder = self.ctx.builder
        left = self.visit(node.left)
        right = self.visit(node.right)
        if Operator.arithmetic(node.op):
            method_name = binop_methods[node.op]
            binop = getattr(builder, method_name)
            return binop(left, right, name='res')
        binop = getattr(builder, cmp_func)
        return binop(_CMP_OP[node.op], left, right, name='res')

    def visit_BinaryOp_sint(self, node):
        return self._apply_binop(node, _SI_BINOP_METHODS, 'icmp_signed')

    def visit_BinaryOp_uint(self, node):
        return self._apply_binop(node, _UI_BINOP_METHODS, 'icmp_unsigned')

    def visit_BinaryOp_float(self, node):
        return self._apply_binop(node, _FP_BINOP_METHODS, 'fcmp_ordered')

    def visit_BinaryOp_bool(self, node):
        builder = self.ctx.builder
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == Operator.LOGICAL_OR:
            return builder.or_(left, right)
        elif node.op == Operator.LOGICAL_AND:
            return builder.and_(left, right)
        raise RuntimeError('unknown boolean binop %r' % node.op)

    def visit_BinaryOp(self, node):
        ty = node.ty
        if ty in BuiltinTypes.SIGNED_INTS:
            return self.visit_BinaryOp_sint(node)
        elif ty in BuiltinTypes.UNSIGNED_INTS:
            return self.visit_BinaryOp_uint(node)
        elif ty in BuiltinTypes.FLOATS:
            return self.visit_BinaryOp_float(node)
        elif ty == BuiltinTypes.BOOL:
            return self.visit_BinaryOp_bool(node)
        raise RuntimeError('bad operands %r' % ty)

    def visit_UnaryOp(self, node):
        builder = self.ctx.builder
        value = self.visit(node.value)
        op = node.op
        if op == Operator.NOT:
            return builder.not_(value, name='res')
        elif op == Operator.LOGICAL_NOT:
            return builder.not_(value, name='res')
        elif op == Operator.UNARY_PLUS:
            return value
        elif op == Operator.UNARY_MINUS:
            if node.ty in BuiltinTypes.INTEGERS:
                return builder.neg(value, name='res')
            return builder.fsub(ir.Constant(value.type, 0), value, name='res')
        raise RuntimeError('unknown unary operator %r' % op)

    def visit_Assignment(self, node):
        ctx = self.ctx
        if node.op is not None:
            tmp = ast.BinaryOp(node.op, node.lvalue, node.rvalue,
                               ty=node.ty, loc=node.loc)
            right = self.visit_BinaryOp(tmp)
        else:
            right = self.visit(node.rvalue)
        ptr = ctx.symbol_table.get(node.lvalue.name)
        result = ctx.builder.store(right, ptr, align=4)
        return result

    def _cast_int_to_float(self, value, from_ty, to_ty):
        """Cast signed/unsigned integer value to floating value."""
        builder = self.ctx.builder
        ty = convert_to_llvm_ty(to_ty)
        if from_ty in BuiltinTypes.SIGNED_INTS:
            return builder.sitofp(value, ty, name='sitofp')
        return builder.uitofp(value, ty, name='uitofp')

    def _cast_float_to_int(self, value, from_ty, to_ty):
        """Cast float value to signed/unsigned integer value."""
        builder = self.ctx.builder
        ty = convert_to_llvm_ty(to_ty)
        if to_ty in BuiltinTypes.SIGNED_INTS:
            return builder.fptosi(value, ty, name='fptosi')
        return builder.fptoui(value, ty, name='fptoui')

    def _cast_int_to_int(self, value, from_ty, to_ty):
        """Truncate or extend an integer value."""
        from_nbits = NBITS[from_ty]
        to_nbits = NBITS[to_ty]
        if to_nbits == from_nbits:
            return value
        builder = self.ctx.builder
        ty = convert_to_llvm_ty(to_ty)
        if from_nbits > to_nbits:
            return builder.trunc(value, ty, name='trunc')
        if from_ty in BuiltinTypes.SIGNED_INTS:
            return builder.sext(value, ty, name='ext')
        return builder.zext(value, ty, name='ext')

    def _cast_float_to_float(self, value, from_ty, to_ty):
        """Truncate or extend a float value."""
        from_nbits = NBITS[from_ty]
        to_nbits = NBITS[to_ty]
        if from_nbits == to_nbits:
            return value
        builder = self.ctx.builder
        ty = convert_to_llvm_ty(to_ty)
        if from_nbits > to_nbits:
            return builder.fptrunc(value, ty, name='trunc')
        return builder.fpext(value, ty, name='ext')

    def visit_Cast(self, node):
        value = self.visit(node.value)
        from_ty, to_ty = node.src_ty, node.dst_ty
        integers = BuiltinTypes.INTEGERS
        floats = BuiltinTypes.FLOATS
        if from_ty in integers and to_ty in integers:
            return self._cast_int_to_int(value, from_ty, to_ty)
        elif from_ty in integers and to_ty in floats:
            return self._cast_int_to_float(value, from_ty, to_ty)
        elif from_ty in floats and to_ty in integers:
            return self._cast_float_to_int(value, from_ty, to_ty)
        elif from_ty in floats and to_ty in floats:
            return self._cast_float_to_float(value, from_ty, to_ty)
        raise RuntimeError('cannot cast %r to %r' % (from_ty, to_ty))

    def visit_IntegerConstant(self, node):
        ty = convert_to_llvm_ty(BuiltinTypes.I32)
        result = ir.Constant(ty, node.value)
        return result

    def visit_FloatConstant(self, node):
        ty = convert_to_llvm_ty(BuiltinTypes.F32)
        result = ir.Constant(ty, node.value)
        return result

    def visit_BooleanConstant(self, node):
        ty = convert_to_llvm_ty(BuiltinTypes.BOOL)
        result = ir.Constant(ty, int(node.value))
        return result

    def visit_StringConstant(self, node):
        ctx = self.ctx
        buf = bytearray((node.value + '\00').encode('ascii'))
        value = ir.Constant(ir.ArrayType(ir.IntType(8), len(buf)), buf)
        const = _make_global_constant(ctx.module, value, 'str')
        ty = convert_to_llvm_ty(BuiltinTypes.STR)
        result = ctx.builder.bitcast(const, ty, name='res')
        return result

    def visit_Identifier(self, node):
        ctx = self.ctx
        ptr = ctx.symbol_table.get(node.name)
        result = ctx.builder.load(ptr, name='res', align=4)
        return result

    def visit_FuncCall(self, node):
        ctx = self.ctx
        fn = ctx.function_table.get(node.name)
        args = list(map(self.visit, node.args))
        result = ctx.builder.call(fn, args, name='res')
        return result
