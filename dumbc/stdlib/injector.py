from dumbc.ast import ast


# (name, return type, (args))
_BUILTIN_FUNCTIONS = (
    ('print', ast.BuiltinTypes.VOID,
        [('message', ast.BuiltinTypes.STR)]),
)


def _build_function(description):
    name, ret_ty, args = description
    args = list(map(lambda arg: ast.Argument(*arg), args))
    attrs = [ast.Attribute('external')]
    proto = ast.FunctionProto(name, args, ret_ty, attrs=attrs)
    func = ast.Function(proto)
    return func


def _inject_functions(translation_unit):
    funcs = list(map(_build_function, _BUILTIN_FUNCTIONS))
    translation_unit.decls = funcs + translation_unit.decls


def inject_stdlib(translation_unit):
    """Inject standard library to the AST.

    Args:
        translation_unit(TranslationUnit): Root of the AST.
    """
    _inject_functions(translation_unit)
