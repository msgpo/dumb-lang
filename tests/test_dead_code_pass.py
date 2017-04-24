import pytest

import dumbc.ast.ast as ast

from dumbc.transform.dead_code_pass import DeadCodePass


def assert_tree(tree, expected):
    assert type(tree) == type(expected)
    if isinstance(tree, list):
        assert len(tree) == len(expected)
        for _tree, _expected in zip(tree, expected):
            assert_tree(_tree, _expected)
    elif isinstance(tree, ast.Node):
        for attr_name, expected_value in vars(expected).items():
            assert_tree(getattr(tree, attr_name), expected_value)
    else:
        assert tree == expected


@pytest.mark.parametrize('with_dead_code,without_dead_code', [
    ([], []),
    ([
        ast.BinaryOp(ast.Operator.ADD,
                     ast.IntegerConstant(0),
                     ast.IntegerConstant(1)),
        ast.Return(),
        ast.Break()
    ],
    [
        ast.BinaryOp(ast.Operator.ADD,
                     ast.IntegerConstant(0),
                     ast.IntegerConstant(1)),
        ast.Return()
    ]),
    ([
        ast.BinaryOp(ast.Operator.ADD,
                     ast.IntegerConstant(0),
                     ast.IntegerConstant(1)),
        ast.Break(),
        ast.Return()
    ],
    [
        ast.BinaryOp(ast.Operator.ADD,
                     ast.IntegerConstant(0),
                     ast.IntegerConstant(1)),
        ast.Break()
    ]),
    ([
        ast.BinaryOp(ast.Operator.ADD,
                     ast.IntegerConstant(0),
                     ast.IntegerConstant(1)),
        ast.Continue(),
        ast.Break()
    ],
    [
        ast.BinaryOp(ast.Operator.ADD,
                     ast.IntegerConstant(0),
                     ast.IntegerConstant(1)),
        ast.Continue()
    ]),
    ([
        ast.BinaryOp(ast.Operator.ADD,
                     ast.IntegerConstant(0),
                     ast.IntegerConstant(1))
    ],
    [
        ast.BinaryOp(ast.Operator.ADD,
                     ast.IntegerConstant(0),
                     ast.IntegerConstant(1))
    ])
])
def test_dce(with_dead_code, without_dead_code):
    root = ast.Block(with_dead_code)
    dcp = DeadCodePass()

    dcp.visit(root)

    assert_tree(root.stmts, without_dead_code)
