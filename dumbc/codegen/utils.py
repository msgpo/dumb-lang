import subprocess
import itertools

from llvmlite import ir
from llvmlite import binding as llvm

from dumbc.ast.ast import BuiltinTypes


NBITS = {ty:int(ty.name[1:]) for ty in BuiltinTypes.NUMERICAL}

_BUILTIN_TY_TO_LLVM_TY = {
    BuiltinTypes.I8: ir.IntType(8),
    BuiltinTypes.U8: ir.IntType(8),
    BuiltinTypes.I32: ir.IntType(32),
    BuiltinTypes.U32: ir.IntType(32),
    BuiltinTypes.I64: ir.IntType(64),
    BuiltinTypes.I64: ir.IntType(64),
    BuiltinTypes.F32: ir.FloatType(),
    BuiltinTypes.F64: ir.DoubleType(),
    BuiltinTypes.BOOL: ir.IntType(1),
    BuiltinTypes.STR: ir.IntType(8).as_pointer(),
    BuiltinTypes.VOID: ir.VoidType()
}


def convert_to_llvm_ty(ty): # pragma: nocover
    """Convert internal type class to LLVM representation.

    Args:
        ty (ast.Type): Type to be converted.

    Returns:
        ir.Type: converted builtin type.
    """
    return _BUILTIN_TY_TO_LLVM_TY[ty]


def emit_object_file(module, output_file, triple=None): # pragma: nocover
    """Emit object file from a module.

    Args:
        module (Module): Module with an LLVM IR.
        output_file (str): Where to put emitted object file.
        triple (str, optional): Platform triple.
    """
    llvm.initialize()
    llvm.initialize_native_asmprinter()
    llvm.initialize_native_target()
    if triple is None:
        target = llvm.Target.from_default_triple()
    else:
        target = llvm.Target.from_triple(triple)
    machine = target.create_target_machine()
    mod = llvm.parse_assembly(str(module))
    mod.verify()
    with open(output_file, 'wb') as f:
        f.write(machine.emit_object(mod))


def link_object_files(output, object_files, libs=None, lib_paths=None): # pragma: nocover
    """Link object files.

    Args:
        output (str): Output executable filename.
        object_files (list): List with object files.
        libs (list, optional): Library names to link.
        lib_paths (list, optional): Library search paths.

    NOTE: clang is used to link object files.
    """
    linker_args = []
    if libs is not None:
        linker_args.extend(map(lambda lib: '-l' + lib, libs))
    if lib_paths is not None:
        linker_args.extend(map(lambda path: '-L' + path, lib_paths))
    args = itertools.chain(('clang', '-o', output),
                           object_files,
                           linker_args)
    subprocess.run(args)
