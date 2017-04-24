__all__ = ('SourceFile',
           'Compiler')

import argparse
import os
import sys

import dumbc
import dumbc.ast.ast as ast

from dumbc.parser import Parser
from dumbc.parser import tokenize
from dumbc.stdlib.injector import inject_stdlib
from dumbc.transform import transform_ast
from dumbc.codegen import Codegen
from dumbc.codegen.utils import emit_object_file
from dumbc.codegen.utils import link_object_files
from dumbc.utils.diagnostics import DiagnosticsEngine
from dumbc.errors import Error


_STDLIBS = ['stddumb']


class SourceFile:
    """Object that encapsulates filename and content of a source file.

    Attributes:
        filename (str): Filename of the source file.
        text (str): Content of the source file.

    TODO: replace this class with the collections.namedtuple.
    """

    def __init__(self, filename, text):
        self.filename = filename
        self.text = text

    @classmethod
    def from_filename(cls, filename):
        """Read source code from a file.

        Args:
            filename (str): Filename of the file with a code.

        Returns:
            SourceFile
        """
        with open(filename, 'r') as f:
            text = f.read()
        return cls(filename, text)


class Compiler:
    """Compiler.

    Attributes:
        source (SourceFile): Source file to be compiled.
        output (str): Write executable to <output>.
        stdlib (str, optional): Path to the standard library(libstddumb).
            You need to set it only if the library was installed at
            non-standard location.
        dump_ir (bool, optional): Whether to print out LLVM IR.
        clean (bool, optional): If it is `True` then all object files will be
            deleted after compilation is done.
    """

    def __init__(self, source, output, stdlib=None, dump_ir=False, clean=True):
        self.source = source
        self.output = output
        self.stdlib = stdlib
        self.dump_ir = dump_ir
        self.clean = clean
        self.diag = DiagnosticsEngine(source.filename, source.text)

    def _build_module(self):
        try:
            tokens = tokenize(self.source.text)
            parser = Parser(tokens, self.diag)
            ast = parser.parse_translation_unit()

            inject_stdlib(ast)
            ast = transform_ast(ast)

            codegen = Codegen(module_name=self.source.filename)
            module = codegen.generate(ast)
        except Error as e:
            self.diag.error(e.message, loc=e.loc)
            sys.exit(-1)
        return module

    def run(self):
        module = self._build_module()

        if self.dump_ir:
            print(module)
            return

        object_file = self.output + '.o'
        emit_object_file(module, object_file)

        linker_args = {
            'output': self.output,
            'object_files': [object_file],
            'libs': _STDLIBS
        }
        if self.stdlib is not None:
            linker_args['lib_paths'] = [self.stdlib]
        link_object_files(**linker_args)

        if self.clean:
            os.remove(object_file)


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    build_cmd = subparsers.add_parser('build')
    build_cmd.add_argument('file',
                           help='Input file')
    build_cmd.add_argument('-o', '--output',
                           help='Where to place the output')
    build_cmd.add_argument('--ir', action='store_true',
                           help='Show LLVM IR', dest='dump_ir')
    build_cmd.add_argument('--clean', action='store_true',
                           help="If set it'll delete intermediate object files")
    build_cmd.add_argument('--stdlib',
                           help='Path to the std lib')

    parser.add_argument('--version', action='version', version=dumbc.VERSION)

    args = vars(parser.parse_args())
    return args


def _basename(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    return filename


def main():
    args = parse_args()
    source = SourceFile.from_filename(args['file'])
    compiler = Compiler(source=source,
                        output=_basename(args['file']),
                        stdlib=args['stdlib'],
                        dump_ir=args['dump_ir'],
                        clean=args['clean'])
    compiler.run()


if __name__ == '__main__':
    main()
