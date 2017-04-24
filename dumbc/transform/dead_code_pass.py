import dumbc.ast.ast as ast

from dumbc.transform.base_pass import Pass


def eliminate_dead_code(stmts):
    # Find the first return/break/continue statement and delete
    # the rest after it. The else clause executes when the loop
    # completes normally (in our case no return/break/continue
    # statements were found).
    classes = (ast.Return, ast.Break, ast.Continue)
    for i, stmt in enumerate(stmts):
        if any(isinstance(stmt, klass) for klass in classes):
            return stmts[:i + 1]
    else:
        return stmts


class DeadCodePass(Pass):

    def visit_Block(self, node):
        node.stmts = eliminate_dead_code(node.stmts)
        for stmt in node.stmts:
            self.visit(stmt)
