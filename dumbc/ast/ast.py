__all__ = ('Location',
           'Type',
           'BuiltinTypes',
           'Node',
           'Expr',
           'Stmt',
           'Decl',
           'Operator',
           'BinaryOp',
           'Assignment',
           'UnaryOp',
           'Cast',
           'IntegerConstant',
           'FloatConstant',
           'BooleanConstant',
           'StringConstant',
           'Identifier',
           'FuncCall',
           'Block',
           'If',
           'While',
           'Break',
           'Continue',
           'Return',
           'Var',
           'Expression',
           'Attribute',
           'Argument',
           'FunctionProto',
           'Function',
           'TranslationUnit')

import collections

from enum import Enum


Location = collections.namedtuple('Location', ('line', 'column', 'extent'))
Type = collections.namedtuple('Type', ('name',))


INITIAL_LOC = Location(1, 1, 0)


def _make_repr(node, fields_fmt=None):
    cls = node.__class__.__name__
    loc = node.loc
    fields = None

    if not loc:
        loc = Location('?', '?', 0)

    if not fields_fmt:
        fmt = '<{cls} at {line}:{col}>'
    else:
        fields = fields_fmt.format(**vars(node))
        fmt = '<{cls} {fields} at {line}:{col}>'

    return fmt.format(cls=cls, fields=fields, line=loc.line, col=loc.column)


class BuiltinTypes: # pragma: no cover
    I8 = Type('i8')
    U8 = Type('u8')
    I32 = Type('i32')
    U32 = Type('u32')
    I64 = Type('i64')
    U64 = Type('u64')
    F32 = Type('f32')
    F64 = Type('f64')
    BOOL = Type('bool')
    STR = Type('str')
    VOID = Type('void')

    FLOATS = (F32, F64)
    INTEGERS = (I8, U8, I32, U32, I64, U64)
    NUMERICAL = INTEGERS + FLOATS
    SIGNED_INTS = (I8, I32, I64)
    UNSIGNED_INTS = (U8, U32, U64)

    VAR_TYPES = NUMERICAL + (BOOL, STR)


class Operator(Enum): # pragma: no cover
    ADD = 0 # +
    SUB = 1 # -
    MUL = 2 # *
    DIV = 3 # /
    MOD = 4 # %
    AND = 5 # &
    OR = 6  # |
    XOR = 7 # ^
    SHL = 8 # <<
    SHR = 9 # >>

    LT = 100  # <
    LE = 101 # <=
    GT = 102 # >
    GE = 103 # >=
    EQ = 104 # ==
    NE = 105 # !=
    LOGICAL_OR = 106 # ||
    LOGICAL_AND = 107 # &&

    NOT = 200 # ~
    LOGICAL_NOT = 201 # !
    UNARY_PLUS = 202 # +
    UNARY_MINUS = 203 # -

    @staticmethod
    def arithmetic(op):
        return op.value in range(0, 100)

    @staticmethod
    def relational(op):
        return op.value in range(100, 200)

    @staticmethod
    def binary(op):
        return op.value in range(0, 200)

    @staticmethod
    def unary(op):
        return op.value in range(200, 300)

    @staticmethod
    def logical(op):
        return op.name in ('LOGICAL_OR', 'LOGICAL_AND',
                           'EQ', 'NE')

    @staticmethod
    def bitwise(op):
        return op.name in ('OR', 'AND', 'XOR')

    @staticmethod
    def shift(op):
        return op.name in ('SHL', 'SHR')


class Node: # pragma: no cover
    """Base node.

    Attributes:
        loc (Location): Position of the node in a source file.
    """

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self): # pragma: no cover
        return _make_repr(self)


class Expr(Node):
    pass


class Stmt(Node):
    pass


class Decl(Node):
    pass


class BinaryOp(Expr): # pragma: no cover
    """Binary operator node.

    `BinaryOp` nodes represent expressions like 1 + 2, 4 / (4 - 4), etc.

    Attributes:
        op (Operator): Binary operator(plus, minus, etc).
        left (Node): Left operand.
        right (Node): Right operand.
    """

    def __init__(self, op, left, right, *, ty=None, loc=None):
        super(BinaryOp, self).__init__(loc)
        self.op = op
        self.left = left
        self.right = right
        self.ty = ty

    def __repr__(self):
        return _make_repr(self, '{op!r}')


class Assignment(Expr): # pragma: no cover
    """Assignment operator node."""

    def __init__(self, lvalue, rvalue, op=None, *, ty=None, loc=None):
        super(Assignment, self).__init__(loc)
        self.op = op
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.ty = ty


class UnaryOp(Expr): # pragma: no cover
    """Unary operator node.

    `UnaryOp` nodes represent expressions like +1, -1, !true, etc.

    Attributes:
        op (str): Unary operator(-, !, etc).
        value (Node): Operand of the operator.
    """

    def __init__(self, op, value, *, ty=None, loc=None):
        super(UnaryOp, self).__init__(loc)
        self.op = op
        self.value = value
        self.ty = ty

    def __repr__(self):
        return _make_repr(self, '{op!r}')


class Cast(Expr): # pragma: no cover
    """Type casting node.

    Attributes:
        value (Node): A value to be casted.
        src_ty (Type): Type of the value.
        dst_ty (Type): A type to which the value will be casted.
    """

    def __init__(self, value, dst_ty, src_ty=None, *, loc=None):
        super(Cast, self).__init__(loc)
        self.value = value
        self.src_ty = src_ty
        self.dst_ty = dst_ty

    def __repr__(self):
        return _make_repr(self, '{dst_ty.name!r}')


class IntegerConstant(Expr): # pragma: no cover
    """Integer literal node.

    Attributes:
        value (int): Value of the literal.
    """

    def __init__(self, value, *, loc=None):
        super(IntegerConstant, self).__init__(loc)
        self.value = value

    def __repr__(self):
        return _make_repr(self, '{value!r}')


class FloatConstant(Expr): # pragma: no cover
    """Float literal node.

    Attributes:
        value (float): Value of the literal.
    """

    def __init__(self, value, *, loc=None):
        super(FloatConstant, self).__init__(loc)
        self.value = value

    def __repr__(self):
        return _make_repr(self, '{value:.2}')


class BooleanConstant(Expr): # pragma: no cover
    """Boolean literal node.

    Attributes:
        value (bool): Value of the literal.
    """

    def __init__(self, value, *, loc=None):
        super(BooleanConstant, self).__init__(loc)
        self.value = value

    def __repr__(self):
        return _make_repr(self, '{value!r}')


class StringConstant(Expr): # pragma: no cover
    """String literal node.

    Attributes:
        value (str): Value of the literal.
    """

    def __init__(self, value, *, loc=None):
        super(StringConstant, self).__init__(loc)
        self.value = value

    def __repr__(self):
        return _make_repr(self, '{value!r}')


class Identifier(Expr): # pragma: no cover
    """Identifier node.

    An identifier is a name of a variable or a function.

    Attributes:
        name (str): Identifier.
    """

    def __init__(self, name, *, loc=None):
        super(Identifier, self).__init__(loc)
        self.name = name

    def __repr__(self):
        return _make_repr(self, '{name!r}')


class FuncCall(Expr): # pragma: no cover
    """Function call node.

    Attributes:
        name (str): Name of the function.
        args (list): List of all passed arguments.
    """

    def __init__(self, name, args, *, loc=None):
        super(FuncCall, self).__init__(loc)
        self.name = name
        self.args = args

    def __repr__(self):
        return _make_repr(self, '{name!r}')


class Block(Stmt): # pragma: no cover
    """Block node.

    Attributes:
        stmts (list): List of subsequent statements.
    """

    def __init__(self, stmts, *, loc=None):
        super(Block, self).__init__(loc)
        self.stmts = stmts


class If(Stmt): # pragma: no cover
    """If node.

    Attributes:
        cond (Node): Boolean condition.
        then (Block): Consequent.
        otherwise(Block, optional): Alternative.
    """

    def __init__(self, cond, then, otherwise=None, *, loc=None):
        super(If, self).__init__(loc)
        self.cond = cond
        self.then = then
        self.otherwise = otherwise


class While(Stmt): # pragma: no cover
    """While node.

    Attributes:
        cond (Node): Boolean condition.
        body (Block): Body of the loop.
    """

    def __init__(self, cond, body, *, loc=None):
        super(While, self).__init__(loc)
        self.cond = cond
        self.body = body


class Break(Stmt): # pragma: no cover
    """Break statement node."""

    def __init__(self, *, loc=None):
        super(Break, self).__init__(loc)


class Continue(Stmt): # pragma: no cover
    """Continue statement node."""

    def __init__(self, *, loc=None):
        super(Continue, self).__init__(loc)


class Return(Stmt): # pragma: no cover
    """Return statement node.

    Attributes:
        value (Node, optional): Return value.
    """

    def __init__(self, value=None, *, loc=None):
        super(Return, self).__init__(loc)
        self.value = value


class Var(Stmt): # pragma: no cover
    """Variable declaration node.

    Note: Type of the variable can be omitted. In that case type of
    the variable will be inferred by a compiler.

    Attributes:
        name (str): Name of the variable.
        ty (Type, optional): Type of the variable.
        initial_value (Node): Initial value of the variable.
    """

    def __init__(self, name, initial_value, ty=None, *, loc=None):
        super(Var, self).__init__(loc)
        self.name = name
        self.ty = ty
        self.initial_value = initial_value

    def __repr__(self):
        if self.ty is not None:
            return _make_repr(self, '{name!r} as {ty.name!r}')
        return _make_repr(self, '{name!r}')


class Expression(Stmt): # pragma: no cover
    """Wrapper around Expr node."""

    def __init__(self, expr, *, loc=None):
        super(Expression, self).__init__(loc)
        self.expr = expr

    def __repr__(self):
        return _make_repr(self)


class Attribute(Decl): # pragma: no cover
    """Attribute node.

    Attribute node is attached to a top level node(like function).
    Its purpose is to instruct a compiler about things like mangling,
    etc.

    Attributes:
        name (str): Name of an attribute.
        args (list, optional): Arguments passed to the attribute.
    """

    def __init__(self, name, *, args=None, loc=None):
        super(Attribute, self).__init__(loc)
        self.name = name
        self.args = args

    def __repr__(self):
        return _make_repr(self, '{name!r}')


class Argument(Decl): # pragma: no cover
    """Function argument node.

    Attributes:
        name (str): Name of the argument.
        ty (Type): Type of the argument.
    """

    def __init__(self, name, ty, *, loc=None):
        super(Argument, self).__init__(loc)
        self.name = name
        self.ty = ty

    def __repr__(self):
        return _make_repr(self, '{name!r} as {ty.name!r}')


class FunctionProto(Decl): # pragma: no cover
    """Function prototype node.

    Attributes:
        name (str): Name of the function.
        args (list): List of function arguments.
        ret_ty (Type): Type of return value. If it's None the function
            returns nothing.
        attrs (list): List of attached attributes.
    """

    def __init__(self, name, args, ret_ty, attrs=None, *, loc=None):
        super(FunctionProto, self).__init__(loc)
        self.name = name
        self.args = args
        self.ret_ty = ret_ty
        self.attrs = attrs

    def __repr__(self):
        if self.ret_ty is not None:
            return _make_repr(self, '{name!r} -> {ret_ty.name!r}')
        return _make_repr(self, '{name!r}')


class Function(Decl): # pragma: no cover
    """Function node.

    Attributes:
        proto (FunctionProto): Prototype of the function.
        body (Block, optional): Body of the function. If the function
            is exported from an external library the field is set to None.
    """

    def __init__(self, proto, body=None, *, loc=None):
        super(Function, self).__init__(loc)
        self.proto = proto
        self.body = body

    def __repr__(self):
        return _make_repr(self, '{proto.name!r}')


class TranslationUnit(Decl): # pragma: no cover

    def __init__(self, decls):
        super(TranslationUnit, self).__init__(INITIAL_LOC)
        self.decls = decls
