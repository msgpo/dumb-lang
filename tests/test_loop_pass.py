import pytest

import dumbc.ast.ast as ast

from dumbc.errors import DumbSyntaxError
from dumbc.transform.loop_pass import LoopPass


def test_break():
    root = ast.Block([
        ast.While(ast.BooleanConstant(True),
                  ast.Block([ast.Break()]))
    ])
    lp = LoopPass()
    lp.visit(root)


def test_break_outside_loop():
    root = ast.Block([ast.Break()])
    lp = LoopPass()
    with pytest.raises(DumbSyntaxError):
        lp.visit(root)


def test_continue():
    root = ast.Block([
        ast.While(ast.BooleanConstant(True),
                  ast.Block([ast.Continue()]))
    ])
    lp = LoopPass()
    lp.visit(root)


def test_continue_outside_loop():
    root = ast.Block([ast.Continue()])
    lp = LoopPass()
    with pytest.raises(DumbSyntaxError):
        lp.visit(root)
