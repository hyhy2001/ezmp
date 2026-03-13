from ezmp.formula.lexer import tokenize, Token
from ezmp.formula.parser import (
    parse_formula,
    BinOpNode,
    FunctionNode,
    ReferenceNode,
    NumberNode,
    StringNode,
)


def test_lexer_basic():
    tokens = tokenize('=SUM(A1:B10, 5, "Hello")')
    assert len(tokens) == 7
    assert tokens[0] == Token("FUNCTION", "SUM")
    assert tokens[1] == Token("RANGE", "A1:B10")
    assert tokens[2] == Token("SEPARATOR", ",")
    assert tokens[3] == Token("NUMBER", 5.0)
    assert tokens[4] == Token("SEPARATOR", ",")
    assert tokens[5] == Token("STRING", "Hello")
    assert tokens[6] == Token("PAREN_R", ")")


def test_lexer_absolute_refs():
    tokens = tokenize("=VLOOKUP($A$1, Sheet2!$A:$Z, 2)")
    assert tokens[1] == Token("REFERENCE", "A1")
    assert tokens[3] == Token("RANGE", "Sheet2!A:Z")


def test_parser_arithmetic():
    ast = parse_formula(tokenize("=5 + 3 * 2"))
    assert isinstance(ast, BinOpNode)
    assert ast.op == "+"
    assert isinstance(ast.left, NumberNode) and ast.left.value == 5
    assert isinstance(ast.right, BinOpNode)
    assert ast.right.op == "*"


def test_parser_functions():
    ast = parse_formula(tokenize('=SUMIF(A1:A10, ">5", B1:B10)'))
    assert isinstance(ast, FunctionNode)
    assert ast.name == "SUMIF"
    assert len(ast.args) == 3
    assert isinstance(ast.args[0], ReferenceNode) and ast.args[0].value == "A1:A10"
    assert isinstance(ast.args[1], StringNode) and ast.args[1].value == ">5"


def test_parser_empty_args():
    ast = parse_formula(tokenize("=IF(A1,,B1)"))
    assert isinstance(ast, FunctionNode)
    assert len(ast.args) == 3
    assert isinstance(ast.args[0], ReferenceNode)
    assert isinstance(ast.args[1], StringNode) and ast.args[1].value == ""
    assert isinstance(ast.args[2], ReferenceNode)
