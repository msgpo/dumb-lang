import pytest
import mock

import dumbc.ast.ast as ast

from dumbc import ExprVisitor
from dumbc import StmtVisitor
from dumbc import DeclVisitor


class StubExprVisitor(ExprVisitor):

    def visit_BinaryOp(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_Assignment(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_UnaryOp(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_Cast(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_IntegerConstant(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_FloatConstant(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_BooleanConstant(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_StringConstant(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_Identifier(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_FuncCall(self, node):
        raise RuntimeError('Unexpected call.')


class StubStmtVisitor(StmtVisitor):

    def visit_If(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_While(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_Break(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_Continue(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_Block(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_Return(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_Var(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_Expression(self, node):
        raise RuntimeError('Unexpected call.')


class StubDeclVisitor(DeclVisitor):

    def visit_Function(self, node):
        raise RuntimeError('Unexpected call.')

    def visit_TranslationUnit(self, node):
        raise RuntimeError('Unexpected call.')


@pytest.mark.parametrize('node', [
    ast.BinaryOp(None, None, None),
    ast.Assignment(None, None),
    ast.UnaryOp(None, None),
    ast.Cast(None, None),
    ast.IntegerConstant(None),
    ast.FloatConstant(None),
    ast.BooleanConstant(None),
    ast.StringConstant(None),
    ast.Identifier(None),
    ast.FuncCall(None, None)
])
def test_expr_visitor(node):
    visitor = StubExprVisitor()
    method_name = 'visit_' + type(node).__name__
    with mock.patch.object(visitor, method_name):
        visitor.visit(node)
        getattr(visitor, method_name).assert_called_once_with(node)


@pytest.mark.parametrize('node', [
    ast.Block(None),
    ast.If(None, None),
    ast.While(None, None),
    ast.Break(),
    ast.Continue(),
    ast.Return(),
    ast.Var(None, None),
    ast.Expression(None)
])
def test_stmt_visitor(node):
    visitor = StubStmtVisitor()
    method_name = 'visit_' + type(node).__name__
    with mock.patch.object(visitor, method_name):
        visitor.visit(node)
        getattr(visitor, method_name).assert_called_once_with(node)


@pytest.mark.parametrize('node', [
    ast.Function(None, None),
    ast.TranslationUnit(None)
])
def test_decl_visitor(node):
    visitor = StubDeclVisitor()
    method_name = 'visit_' + type(node).__name__
    with mock.patch.object(visitor, method_name):
        visitor.visit(node)
        getattr(visitor, method_name).assert_called_once_with(node)
