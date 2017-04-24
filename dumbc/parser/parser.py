__all__ = ('Parser',)

from dumbc.errors import DumbSyntaxError
from dumbc.errors import DumbEOFError
from dumbc.ast import ast


# In order to find more information about tokens
# take a look at module *lexer* in a package dumbc.parser.
OPERATOR_PRECEDENCE = {
    'ASSIGN':       1,
    'PLUSEQ':       1,
    'MINUSEQ':      1,
    'STAREQ':       1,
    'SLASHEQ':      1,
    'XOREQ':        1,
    'ANDEQ':        1,
    'OREQ':         1,
    'PERCENTEQ':    1,
    'SHLEQ':        1,
    'SHREQ':        1,
    'LOGICAL_OR':   2,
    'LOGICAL_AND':  3,
    'OR':           4,
    'XOR':          5,
    'AND':          6,
    'EQ':           7,
    'NE':           7,
    'LT':           8,
    'LE':           8,
    'GT':           8,
    'GE':           8,
    'SHL':          9,
    'SHR':          9,
    'PLUS':         10,
    'MINUS':        10,
    'STAR':         11,
    'SLASH':        11,
    'PERCENT':      11,
    'AS':           12
}


TOKEN_TO_BINOP = {
    'SHL':          ast.Operator.SHL,
    'SHR':          ast.Operator.SHR,
    'LOGICAL_OR':   ast.Operator.LOGICAL_OR,
    'LOGICAL_AND':  ast.Operator.LOGICAL_AND,
    'LT':           ast.Operator.LT,
    'LE':           ast.Operator.LE,
    'GT':           ast.Operator.GT,
    'GE':           ast.Operator.GE,
    'EQ':           ast.Operator.EQ,
    'NE':           ast.Operator.NE,
    'PLUS':         ast.Operator.ADD,
    'MINUS':        ast.Operator.SUB,
    'STAR':         ast.Operator.MUL,
    'SLASH':        ast.Operator.DIV,
    'PERCENT':      ast.Operator.MOD,
    'OR':           ast.Operator.OR,
    'AND':          ast.Operator.AND,
    'XOR':          ast.Operator.XOR
}

TOKEN_TO_UNARYOP = {
    'PLUS':         ast.Operator.UNARY_PLUS,
    'MINUS':        ast.Operator.UNARY_MINUS,
    'NOT':          ast.Operator.NOT,
    'LOGICAL_NOT':  ast.Operator.LOGICAL_NOT
}
UNARYOP_TOKENS = TOKEN_TO_UNARYOP.keys()


AUGMENT_ASSIGNMENT_OP = {
    'ASSIGN':       None,
    'PLUSEQ':       ast.Operator.ADD,
    'MINUSEQ':      ast.Operator.SUB,
    'STAREQ':       ast.Operator.MUL,
    'SLASHEQ':      ast.Operator.DIV,
    'PERCENTEQ':    ast.Operator.MOD,
    'XOREQ':        ast.Operator.XOR,
    'OREQ':         ast.Operator.OR,
    'ANDEQ':        ast.Operator.AND,
    'SHLEQ':        ast.Operator.SHL,
    'SHREQ':        ast.Operator.SHR
}
ASSIGNMENT_TOKENS = AUGMENT_ASSIGNMENT_OP.keys()


EXPR_BEGIN_TOKENS = (
    'INTEGER', 'FLOAT', 'BOOL', 'PLUS', 'MINUS',
    'STR', 'IDENT', 'LEFT_PAREN', 'NOT', 'LOGICAL_NOT'
)


def _get_precedence(token):
    try:
        return OPERATOR_PRECEDENCE[token.kind]
    except:
        return -1


def _unescape_string(s):
    return (s[1:-1].replace(r'\'', '\'')
        .replace(r'\"', '\"')
        .replace(r'\t', '\t')
        .replace(r'\n', '\n'))


class Parser:
    """Parser.

    This is top-down parser; each parse_* method corresponds
    to some rule in a grammar of the language. Expressions
    are parsed by an operator-precedence parser.

    Attributes:
        token_stream (generator): A stream of tokens generated
            by a lexer.
        curr_token (Token): Current token. Call `advance()`
            method to advance it.

    Examples:

        Parse translation unit:

        >>> from dumbc import tokenize
        >>> from dumbc import Parser
        >>> from dumbc.utils.diagnostics import DiagnosticsEngine
        >>> code = '''
        ... func factorial(n: i32): i32 {
        ...     if n < 2 {
        ...         return 1
        ...     }
        ...     n * factorial(n - 1)
        ... }
        ... '''
        >>> token_stream = tokenize(code)
        >>> diag = DiagnosticsEngine('foo.txt', code)
        >>> parser = Parser(token_stream, diag)
        >>> parser.parse_translation_unit()
        <TranslationUnit at 1:1>
    """

    def __init__(self, token_stream, diag):
        self.token_stream = token_stream
        self.curr_token = next(self.token_stream)
        self.diag = diag

    def advance(self, expect_kind=None):
        """Advance to the next token.

        Args:
            expect_kind (str, optional): What kind of current
                token should be. If `expect_kind` is not equal
                to `self.curr_token.kind` an exception will be raised.

        Returns:
            Token: Next token in the token stream.

        Raises:
            SyntaxError: Current token is different from what
                we have expected.
        """
        if expect_kind and self.curr_token.kind != expect_kind:
            msg = 'unexpected token(expected=%r, actual=%r)' % (
                expect_kind,
                self.curr_token.kind)
            self.diag.error(self.curr_token.loc, msg)
            raise DumbSyntaxError(msg)

        try:
            self.curr_token = next(self.token_stream)
        except StopIteration:
            raise DumbEOFError('unexpected EOF')

        return self.curr_token

    def parse_expr(self):
        """Parse an expression with operator-precedence parser.

        Links:
            * https://en.wikipedia.org/wiki/Operator-precedence_parser

        Grammar:
            expr : INTEGER
                 | FLOAT
                 | BOOL
                 | STR
                 | ( expr )
                 | + expr
                 | - expr
                 | ! expr
                 | IDENT
                 | IDENT func_call_args
        """
        left = self.parse_unary_expr()
        return self.parse_binop_rhs(left, 0)

    def parse_unary_expr(self):
        """
        expr : + expr
             | - expr
             | ! expr
        """
        if self.curr_token.kind not in UNARYOP_TOKENS:
            return self.parse_primary()

        op = self.curr_token
        self.advance()
        value = self.parse_unary_expr()
        return ast.UnaryOp(TOKEN_TO_UNARYOP[op.kind], value, loc=op.loc)

    def parse_binop_rhs(self, left, min_precedence=0):
        while True:
            precedence = _get_precedence(self.curr_token)
            if precedence < min_precedence:
                return left
            op = self.curr_token
            self.advance()

            if op.kind == 'AS':
                right = self.parse_type()
            else:
                right = self.parse_unary_expr()

            next_precedence = _get_precedence(self.curr_token)
            if precedence < next_precedence:
                right = self.parse_binop_rhs(right, precedence + 1)

            if op.kind == 'AS':
                left = ast.Cast(left, right, loc=op.loc)
            elif op.kind in ASSIGNMENT_TOKENS:
                left = ast.Assignment(left, right,
                                      op=AUGMENT_ASSIGNMENT_OP[op.kind],
                                      loc=op.loc)
            else:
                left = ast.BinaryOp(TOKEN_TO_BINOP[op.kind],
                                    left, right, loc=op.loc)

    def parse_primary(self):
        """
        expr : INTEGER
             | FLOAT
             | BOOL
             | STR
             | IDENT
             | IDENT func_call_args
             | ( expr )
        """
        kind = self.curr_token.kind

        if kind == 'INTEGER':
            return self.parse_integer()
        elif kind == 'FLOAT':
            return self.parse_float()
        elif kind == 'BOOL':
            return self.parse_bool()
        elif kind == 'STR':
            return self.parse_string()
        elif kind == 'IDENT':
            return self.parse_ident()
        elif kind == 'LEFT_PAREN':
            return self.parse_paren_expr()
        else:
            msg = 'unexpected token %r' % self.curr_token.value
            self.diag.error(self.curr_token.loc, msg)
            raise DumbSyntaxError(msg)

    def parse_integer(self):
        """expr : INTEGER"""
        integer_tok = self.curr_token
        node = ast.IntegerConstant(int(integer_tok.value),
                                   loc=integer_tok.loc)
        self.advance()
        return node

    def parse_float(self):
        """expr : FLOAT"""
        float_tok = self.curr_token
        node = ast.FloatConstant(float(float_tok.value),
                                 loc=float_tok.loc)
        self.advance()
        return node

    def parse_bool(self):
        """expr : BOOL"""
        bool_tok = self.curr_token
        value = True if bool_tok.value == 'true' else False
        node = ast.BooleanConstant(value, loc=bool_tok.loc)
        self.advance()
        return node

    def parse_string(self):
        """expr : STR"""
        string_tok = self.curr_token
        value = _unescape_string(string_tok.value)
        node = ast.StringConstant(value, loc=string_tok.loc)
        self.advance()
        return node

    def parse_ident(self, no_func_call=False):
        """
        expr : IDENT
             | IDENT func_call_args
        """
        ident_tok = self.curr_token
        self.advance()

        if self.curr_token.kind != 'LEFT_PAREN' or no_func_call:
            return ast.Identifier(ident_tok.value, loc=ident_tok.loc)

        func_args = self.parse_func_call_args()
        return ast.FuncCall(ident_tok.value, func_args, loc=ident_tok.loc)

    def parse_func_call_args(self):
        """
        func_call_args : ()
                       | (args)

        args : expr
             | args , expr
        """
        args = []
        self.advance('LEFT_PAREN')
        while self.curr_token.kind != 'RIGHT_PAREN':
            args.append(self.parse_expr())
            if self.curr_token.kind == 'RIGHT_PAREN':
                break
            self.advance('COMMA')
        self.advance('RIGHT_PAREN')
        return args

    def parse_paren_expr(self):
        """expr : ( expr )"""
        self.advance()
        expr = self.parse_expr()
        self.advance('RIGHT_PAREN')
        return expr

    def skip_semicolon(self):
        while self.curr_token.kind == 'SEMICOLON':
            self.advance()

    def parse_stmt(self):
        """
        stmt : if_stmt
             | while_stmt
             | break_stmt
             | continue_stmt
             | return_stmt
             | block
             | var_stmt
             | expr_stmt
        """
        kind = self.curr_token.kind

        if kind == 'IF':
            node = self.parse_if()
        elif kind == 'WHILE':
            node = self.parse_while()
        elif kind == 'BREAK':
            node = self.parse_break()
        elif kind == 'CONTINUE':
            node = self.parse_continue()
        elif kind == 'RETURN':
            node = self.parse_return()
        elif kind == 'LEFT_CURLY_BRACKET':
            node = self.parse_block()
        elif kind == 'VAR':
            node = self.parse_var()
        else:
            node = self.parse_expr_stmt()

        self.skip_semicolon()
        return node

    def parse_block(self):
        """
        block : { stmt_list }
        stmt_list : stmt
                  | stmt_list stmt
        """
        loc = self.curr_token.loc
        stmts = []
        self.advance('LEFT_CURLY_BRACKET')
        self.skip_semicolon()
        while self.curr_token.kind != 'RIGHT_CURLY_BRACKET':
            stmts.append(self.parse_stmt())
        self.advance('RIGHT_CURLY_BRACKET')
        return ast.Block(stmts, loc=loc)

    def parse_if(self):
        """
        if_stmt : IF expr block
                | IF expr block ELSE block
                | IF expr block ELSE if_stmt
        """
        loc = self.curr_token.loc
        self.advance('IF')
        cond = self.parse_expr()
        then = self.parse_block()
        if self.curr_token.kind != 'ELSE':
            return ast.If(cond, then, loc=loc)
        self.advance('ELSE')
        if self.curr_token.kind == 'IF':
            otherwise = self.parse_if()
        else:
            otherwise = self.parse_block()
        return ast.If(cond, then, otherwise, loc=loc)

    def parse_while(self):
        """while_stmt : WHILE expr block"""
        loc = self.curr_token.loc
        self.advance('WHILE')
        cond = self.parse_expr()
        body = self.parse_block()
        return ast.While(cond, body, loc=loc)

    def parse_break(self):
        """break_stmt : BREAK"""
        node = ast.Break(loc=self.curr_token.loc)
        self.advance('BREAK')
        return node

    def parse_continue(self):
        """continue_stmt : CONTINUE"""
        node = ast.Continue(loc=self.curr_token.loc)
        self.advance('CONTINUE')
        return node

    def parse_return(self):
        """
        return_stmt : RETURN
                    | RETURN expr
        """
        loc = self.curr_token.loc
        self.advance('RETURN')
        if self.curr_token.kind in EXPR_BEGIN_TOKENS:
            ret_val = self.parse_expr()
            return ast.Return(ret_val, loc=loc)
        return ast.Return(loc=loc)

    def parse_var(self):
        """
        var_stmt : VAR IDENT = expr
                 | VAR IDENT : ty = expr
        """
        loc = self.curr_token.loc
        self.advance('VAR')
        name = self.curr_token.value
        self.advance('IDENT')
        if self.curr_token.kind == 'COLON':
            self.advance()
            ty = self.parse_type()
        else:
            ty = None
        self.advance('ASSIGN')
        initial_value = self.parse_expr()
        return ast.Var(name, initial_value, ty, loc=loc)

    def parse_expr_stmt(self):
        """
        expr_stmt : expr
        """
        loc = self.curr_token.loc
        expr = self.parse_expr()
        return ast.Expression(expr, loc=loc)

    def parse_type(self):
        """ty : IDENT"""
        ty = self.curr_token
        self.advance('IDENT')
        return ast.Type(ty.value)

    def parse_attrs(self):
        """
        attr_spec : #[ attrs ]

        attrs : attr
              | attrs , attr
        """
        attrs = []
        self.advance('ATTR_START')
        if self.curr_token.kind == 'RIGHT_SQ_BRACKET':
            msg = 'no attributes'
            self.diag.error(self.curr_token.loc, msg)
            raise DumbSyntaxError(msg)
        while True:
            attrs.append(self.parse_attr())
            if self.curr_token.kind == 'RIGHT_SQ_BRACKET':
                break
            self.advance('COMMA')
        self.advance('RIGHT_SQ_BRACKET')
        return attrs

    def parse_attr(self):
        """
        attr : IDENT
             | IDENT attr_args
        """
        loc = self.curr_token.loc
        name = self.curr_token.value
        self.advance('IDENT')
        if self.curr_token.kind != 'LEFT_PAREN':
            return ast.Attribute(name, loc=loc)
        attr_args = self.parse_attr_args()
        return ast.Attribute(name, args=attr_args, loc=loc)

    def parse_attr_args(self):
        """
        attr_args : ( args )

        args : arg
             | args , arg

        arg : INTEGER
            | BOOL
            | FLOAT
            | IDENT
        """
        args = []
        self.advance('LEFT_PAREN')
        if self.curr_token.kind == 'RIGHT_PAREN':
            msg = 'no arguments were given for an attribute.'
            self.diag.error(self.curr_token.loc, msg)
            raise DumbSyntaxError(msg)
        while True:
            if self.curr_token.kind == 'INTEGER':
                args.append(self.parse_integer())
            elif self.curr_token.kind == 'BOOL':
                args.append(self.parse_bool())
            elif self.curr_token.kind == 'FLOAT':
                args.append(self.parse_float())
            elif self.curr_token.kind == 'IDENT':
                args.append(self.parse_ident(no_func_call=True))
            else:
                msg = 'unknown type of attribute argument'
                self.diag.error(self.curr_token.loc, msg)
                raise DumbSyntaxError(msg)
            if self.curr_token.kind == 'RIGHT_PAREN':
                break
            self.advance('COMMA')
        self.advance('RIGHT_PAREN')
        return args

    def parse_func_proto(self):
        """
        func_proto : FUNC IDENT func_args
                   | FUNC IDENT func_args : ty
        """
        loc = self.curr_token.loc
        self.advance('FUNC')
        name = self.curr_token.value
        self.advance('IDENT')
        func_args = self.parse_func_args()
        if self.curr_token.kind == 'COLON':
            self.advance()
            ret_ty = self.parse_type()
        else:
            ret_ty = ast.BuiltinTypes.VOID
        return ast.FunctionProto(name, func_args, ret_ty, loc=loc)

    def parse_func_args(self):
        """
        func_args : ()
                  | ( args )

        args : arg
             | args , arg
        """
        args = []
        self.advance('LEFT_PAREN')
        if self.curr_token.kind == 'RIGHT_PAREN':
            self.advance()
            return args
        while True:
            args.append(self.parse_func_arg())
            if self.curr_token.kind == 'RIGHT_PAREN':
                break
            self.advance('COMMA')
        self.advance('RIGHT_PAREN')
        return args

    def parse_func_arg(self):
        """arg : IDENT : ty"""
        loc = self.curr_token.loc
        name = self.curr_token.value
        self.advance('IDENT')
        self.advance('COLON')
        ty = self.parse_type()
        return ast.Argument(name, ty, loc=loc)

    def parse_func(self):
        """
        func : func_proto
             | func_proto block
        """
        loc = self.curr_token.loc
        proto = self.parse_func_proto()
        if self.curr_token.kind != 'LEFT_CURLY_BRACKET':
            return ast.Function(proto, loc=loc)
        body = self.parse_block()
        return ast.Function(proto, body, loc=loc)

    def parse_with_attrs(self):
        attrs = self.parse_attrs()
        if self.curr_token.kind == 'FUNC':
            node = self.parse_func()
            node.proto.attrs = attrs
        else:
            msg = 'applying attributes is allowed only to functions'
            self.diag.error(self.curr_token.loc, msg)
            raise DumbSyntaxError(msg)
        return node

    def parse_translation_unit(self):
        """Parse translation unit.

        Returns:
            TranslationUnit: Root of the AST.

        Grammar:
            top_level_decl : func
                           | top_level_decl func
        """
        decls = []
        while self.curr_token.kind != 'EOF':
            if self.curr_token.kind == 'FUNC':
                decls.append(self.parse_func())
            elif self.curr_token.kind == 'ATTR_START':
                decls.append(self.parse_with_attrs())
            else:
                msg = 'unexpected token at top level'
                self.diag.error(self.curr_token.loc, msg)
                raise DumbSyntaxError(msg)
        return ast.TranslationUnit(decls)
