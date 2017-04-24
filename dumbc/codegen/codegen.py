__all__ = ('Codegen',)

from llvmlite import ir

from dumbc.codegen.decl_codegen import DeclarationCodegen
from dumbc.utils.symbol_table import SymbolTable


class Context: # pragma: nocover

    def __init__(self, module_name):
        self.module = ir.Module(name=module_name)
        self.builder = None
        self.symbol_table = SymbolTable()
        self.function_table = SymbolTable()


class Codegen: # pragma: nocover

    def __init__(self, module_name):
        self.ctx = Context(module_name)
        self.codegenerator = DeclarationCodegen(self.ctx)

    def generate(self, ast):
        self.codegenerator.visit(ast)
        return self.ctx.module
