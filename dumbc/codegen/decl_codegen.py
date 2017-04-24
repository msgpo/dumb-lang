from llvmlite import ir

import dumbc.ast.ast as ast

from dumbc.ast.visitor import DeclVisitor
from dumbc.codegen.stmt_codegen import StatementCodegen
from dumbc.codegen.utils import convert_to_llvm_ty


class DeclarationCodegen(DeclVisitor): # pragma: nocover

    def __init__(self, ctx):
        self.ctx = ctx
        self.stmt_codegen = StatementCodegen(ctx)

    def visit_Function(self, node):
        if node.body is None:
            return
        proto = node.proto
        func = self.ctx.function_table.get(proto.name)
        with self.ctx.symbol_table.scope():
            entry = func.append_basic_block(name='entry')
            builder = ir.IRBuilder(entry)
            arg_names = map(lambda arg: arg.name, proto.args)
            for name, value in zip(arg_names, func.args):
                arg = builder.alloca(value.type, name=name)
                builder.store(value, arg, align=4)
                self.ctx.symbol_table.set(name, arg)
            self.ctx.builder = builder
            self.stmt_codegen.visit(node.body)
            if builder.block.terminator is None:
                builder.ret_void()

    def _fill_function_table(self, node):
        for decl in node.decls:
            if not isinstance(decl, ast.Function):
                continue
            proto = decl.proto
            ret_ty = convert_to_llvm_ty(proto.ret_ty)
            args = list(map(lambda arg: convert_to_llvm_ty(arg.ty),
                            proto.args))
            func_ty = ir.FunctionType(ret_ty, args)
            func = ir.Function(self.ctx.module, func_ty, name=proto.name)
            self.ctx.function_table.set(proto.name, func)

    def visit_TranslationUnit(self, node):
        with self.ctx.function_table.scope():
            self._fill_function_table(node)
            for decl in node.decls:
                self.visit(decl)
