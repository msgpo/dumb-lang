from dumbc.ast.visitor import GenericVisitor


class Pass(GenericVisitor): # pragma: no cover
    """Base semantic analysis pass."""

    def visit_BinaryOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Assignment(self, node):
        self.visit(node.lvalue)
        self.visit(node.rvalue)

    def visit_UnaryOp(self, node):
        self.visit(node.value)

    def visit_Cast(self, node):
        self.visit(node.value)

    def visit_IntegerConstant(self, node):
        pass

    def visit_FloatConstant(self, node):
        pass

    def visit_BooleanConstant(self, node):
        pass

    def visit_StringConstant(self, node):
        pass

    def visit_Identifier(self, node):
        pass

    def visit_FuncCall(self, node):
        for arg in node.args:
            self.visit(arg)

    def visit_If(self, node):
        self.visit(node.cond)
        self.visit(node.then)
        if node.otherwise is not None:
            self.visit(node.otherwise)

    def visit_While(self, node):
        self.visit(node.cond)
        self.visit(node.body)

    def visit_Break(self, node):
        pass

    def visit_Continue(self, node):
        pass

    def visit_Block(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_Return(self, node):
        if node.value:
            self.visit(node.value)

    def visit_Var(self, node):
        self.visit(node.initial_value)

    def visit_Expression(self, node):
        self.visit(node.expr)

    def visit_Function(self, node):
        if node.body is not None:
            self.visit(node.body)

    def visit_TranslationUnit(self, node):
        for decl in node.decls:
            self.visit(decl)
