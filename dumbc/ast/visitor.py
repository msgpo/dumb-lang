__all__ = ('Visitor',
           'ExprVisitor',
           'StmtVisitor',
           'DeclVisitor',
           'GenericVisitor')

from abc import ABCMeta
from abc import abstractmethod


class Visitor(metaclass=ABCMeta):
    """Base visitor class."""

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        method = getattr(self, method_name)
        result = method(node)
        return result


class ExprVisitor(Visitor): # pragma: no cover
    """Base expression visitor."""

    @abstractmethod
    def visit_BinaryOp(self, node):
        pass

    @abstractmethod
    def visit_Assignment(self, node):
        pass

    @abstractmethod
    def visit_UnaryOp(self, node):
        pass

    @abstractmethod
    def visit_Cast(self, node):
        pass

    @abstractmethod
    def visit_IntegerConstant(self, node):
        pass

    @abstractmethod
    def visit_FloatConstant(self, node):
        pass

    @abstractmethod
    def visit_BooleanConstant(self, node):
        pass

    @abstractmethod
    def visit_StringConstant(self, node):
        pass

    @abstractmethod
    def visit_Identifier(self, node):
        pass

    @abstractmethod
    def visit_FuncCall(self, node):
        pass


class StmtVisitor(Visitor): # pragma: no cover
    """Base statement visitor."""

    @abstractmethod
    def visit_If(self, node):
        pass

    @abstractmethod
    def visit_While(self, node):
        pass

    @abstractmethod
    def visit_Break(self, node):
        pass

    @abstractmethod
    def visit_Continue(self, node):
        pass

    @abstractmethod
    def visit_Block(self, node):
        pass

    @abstractmethod
    def visit_Return(self, node):
        pass

    @abstractmethod
    def visit_Var(self, node):
        pass

    @abstractmethod
    def visit_Expression(self, node):
        pass


class DeclVisitor(Visitor): # pragma: no cover
    """Base declaration visitor."""

    @abstractmethod
    def visit_Function(self, node):
        pass

    @abstractmethod
    def visit_TranslationUnit(self, node):
        pass


class GenericVisitor(ExprVisitor, StmtVisitor, DeclVisitor):
    pass
