import dumbc.ast.ast as ast

from dumbc.errors import DumbNameError
from dumbc.errors import DumbTypeError
from dumbc.transform.base_pass import Pass


class MainFuncPass(Pass):

    def visit_TranslationUnit(self, node):
        for decl in node.decls:
            if not isinstance(decl, ast.Function): # pragma: nocover
                continue
            if decl.proto.name == 'main':
                if decl.proto.ret_ty != ast.BuiltinTypes.I32:
                    msg = 'main function has to return i32'
                    raise DumbTypeError(msg, loc=decl.loc)
                return
        raise DumbNameError('no main func was found')
