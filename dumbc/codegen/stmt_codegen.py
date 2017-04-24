from llvmlite import ir
from collections import deque

from dumbc.ast.visitor import StmtVisitor
from dumbc.codegen.expr_codegen import ExpressionCodegen
from dumbc.codegen.utils import convert_to_llvm_ty
from dumbc.utils.symbol_table import SymbolTable


class StatementCodegen(StmtVisitor): # pragma: nocover

    def __init__(self, ctx):
        self.ctx = ctx
        self.expr_codegen = ExpressionCodegen(ctx)
        self.loop_stack = SymbolTable()

    def visit_If(self, node):
        builder = self.ctx.builder

        then_bb = builder.append_basic_block(name='if.then')
        else_bb = builder.append_basic_block(name='if.else')
        exit_bb = builder.append_basic_block(name='if.exit')

        # Generate conditional branch
        cond = self.expr_codegen.visit(node.cond)
        br = builder.cbranch(cond, then_bb, else_bb)

        # Generate then block
        builder.position_at_end(then_bb)
        self.visit(node.then)
        if builder.block.terminator is None:
            builder.branch(exit_bb)

        # Generate else block
        builder.position_at_end(else_bb)
        if node.otherwise is not None:
            self.visit(node.otherwise)
        if builder.block.terminator is None:
            builder.branch(exit_bb)

        # Block after if statement
        builder.position_at_end(exit_bb)

    def visit_While(self, node):
        builder = self.ctx.builder

        with self.loop_stack.scope():
            cond_bb = builder.append_basic_block('while.cond')
            body_bb = builder.append_basic_block('while.body')
            exit_bb = builder.append_basic_block('while.exit')

            self.loop_stack.set('entry_bb', cond_bb)
            self.loop_stack.set('exit_bb', exit_bb)

            # Generate condition
            builder.branch(cond_bb)
            builder.position_at_end(cond_bb)
            cond = self.expr_codegen.visit(node.cond)
            br = builder.cbranch(cond, body_bb, exit_bb)

            # Generate body of the loop
            builder.position_at_end(body_bb)
            self.visit(node.body)
            if builder.block.terminator is None:
                builder.branch(cond_bb)

            # Block after loop
            builder.position_at_end(exit_bb)

    def visit_Break(self, node):
        builder = self.ctx.builder
        exit_bb = self.loop_stack.get('exit_bb')
        builder.branch(exit_bb)

    def visit_Continue(self, node):
        builder = self.ctx.builder
        entry_bb = self.loop_stack.get('entry_bb')
        builder.branch(entry_bb)

    def visit_Block(self, node):
        with self.ctx.symbol_table.scope():
            for stmt in node.stmts:
                self.visit(stmt)

    def visit_Return(self, node):
        builder = self.ctx.builder
        if node.value is None:
            builder.ret_void()
            return
        value = self.expr_codegen.visit(node.value)
        builder.ret(value)

    def visit_Var(self, node):
        builder = self.ctx.builder
        ty = convert_to_llvm_ty(node.ty)
        initial_value = self.expr_codegen.visit(node.initial_value)
        ptr = builder.alloca(ty, name=node.name)
        builder.store(initial_value, ptr)
        self.ctx.symbol_table.set(node.name, ptr)

    def visit_Expression(self, node):
        self.expr_codegen.visit(node.expr)
