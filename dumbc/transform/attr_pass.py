import dumbc.ast.ast as ast

from dumbc.errors import DumbTypeError
from dumbc.errors import DumbNameError
from dumbc.transform.base_pass import Pass


class AttrPass(Pass):

    def check_no_attrs(self, node):
        if node.body is None:
            msg = 'function body expected %r' % node.proto.name
            raise DumbTypeError(msg, loc=node.loc)

    def check_external_attr(self, node, attr):
        if attr.args is not None:
            msg = 'external attribute takes no arguments'
            raise DumbTypeError(msg, loc=attr.loc)

        if node.body is not None:
            msg = ('function with external attribute should '
                   'define only prototype')
            raise DumbTypeError(msg, loc=node.loc)

    def visit_Function(self, node):
        attrs = node.proto.attrs

        if attrs is None:
            self.check_no_attrs(node)
            return

        for attr in attrs:
            if attr.name == 'external':
                self.check_external_attr(node, attr)
            else:
                msg = 'ambiguous function attribute name %r' % attr.name
                raise DumbNameError(msg, loc=attr.loc)
