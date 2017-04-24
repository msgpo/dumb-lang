__all__ = ('transform_ast',)

from dumbc.transform.type_pass import TypePass
from dumbc.transform.loop_pass import LoopPass
from dumbc.transform.dead_code_pass import DeadCodePass
from dumbc.transform.attr_pass import AttrPass
from dumbc.transform.main_func_pass import MainFuncPass


def transform_ast(ast):
    passes = [TypePass(),
              LoopPass(),
              DeadCodePass(),
              AttrPass(),
              MainFuncPass()]
    for _pass in passes:
        _pass.visit(ast)
    return ast
