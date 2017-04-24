from dumbc.transform.base_pass import Pass
from dumbc.errors import DumbSyntaxError


class LoopPass(Pass):

    def __init__(self):
        self.loop_depth = 0

    def visit_While(self, node):
        self.loop_depth += 1
        self.visit(node.body)
        self.loop_depth -= 1

    def visit_Break(self, node):
        if self.loop_depth == 0:
            raise DumbSyntaxError("'break' outside loop", loc=node.loc)

    def visit_Continue(self, node):
        if self.loop_depth == 0:
            raise DumbSyntaxError("'continue' outside loop", loc=node.loc)
