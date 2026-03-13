from typing import List, Optional
from dataclasses import dataclass
from ezmp.formula.lexer import Token


class ASTNode:
    pass


@dataclass
class NumberNode(ASTNode):
    value: float


@dataclass
class StringNode(ASTNode):
    value: str


@dataclass
class BooleanNode(ASTNode):
    value: bool


@dataclass
class ErrorNode(ASTNode):
    value: str


@dataclass
class ReferenceNode(ASTNode):
    value: str


@dataclass
class FunctionNode(ASTNode):
    name: str
    args: List[ASTNode]


@dataclass
class BinOpNode(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode


@dataclass
class UnaryOpNode(ASTNode):
    op: str
    expr: ASTNode


class ParserError(Exception):
    pass


class Parser:
    """
    Recursive Descent Parser for Excel Formulas.
    Grammar:
    expr   := term ((+ | - | & | = | <> | > | < | >= | <=) term)*
    term   := factor ((* | / | ^) factor)*
    factor := (+ | -) factor | NUMBER | STRING | BOOLEAN | EXCEL_ERROR | REFERENCE | RANGE | FUNCTION arglist | ( expr )
    arglist:= expr (SEPARATOR expr)* | empty
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token_type: str) -> Token:
        tok = self.current_token()
        if tok and tok.type == token_type:
            self.pos += 1
            return tok
        raise ParserError(
            f"Expected {token_type}, got {tok.type if tok else 'EOF'} at pos {self.pos}"
        )

    def parse(self) -> ASTNode:
        if not self.tokens:
            raise ParserError("Empty formula")
        node = self.expr()
        if self.pos < len(self.tokens):
            raise ParserError(
                f"Unexpected token {self.current_token().value} at end of formula"
            )
        return node

    def expr(self) -> ASTNode:
        node = self.term()
        while (
            self.current_token()
            and self.current_token().type == "OPERATOR"
            and self.current_token().value
            in ("+", "-", "&", "=", "<>", ">", "<", ">=", "<=")
        ):
            op = self.eat("OPERATOR").value
            right = self.term()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def term(self) -> ASTNode:
        node = self.factor()
        while (
            self.current_token()
            and self.current_token().type == "OPERATOR"
            and self.current_token().value in ("*", "/", "^")
        ):
            op = self.eat("OPERATOR").value
            right = self.factor()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def factor(self) -> ASTNode:
        tok = self.current_token()
        if not tok:
            raise ParserError("Unexpected end of formula in factor")

        if tok.type == "OPERATOR" and tok.value in ("+", "-"):
            op = self.eat("OPERATOR").value
            node = self.factor()
            return UnaryOpNode(op=op, expr=node)

        if tok.type == "NUMBER":
            return NumberNode(self.eat("NUMBER").value)
        elif tok.type == "STRING":
            return StringNode(self.eat("STRING").value)
        elif tok.type == "BOOLEAN":
            return BooleanNode(self.eat("BOOLEAN").value)
        elif tok.type == "EXCEL_ERROR":
            return ErrorNode(self.eat("EXCEL_ERROR").value)
        elif tok.type in ("REFERENCE", "RANGE"):
            return ReferenceNode(self.eat(tok.type).value)
        elif tok.type == "PAREN_L":
            self.eat("PAREN_L")
            node = self.expr()
            self.eat("PAREN_R")
            return node
        elif tok.type == "FUNCTION":
            func_name = self.eat("FUNCTION").value
            args = []
            if self.current_token() and self.current_token().type != "PAREN_R":
                args.append(self.expr())
                while self.current_token() and self.current_token().type == "SEPARATOR":
                    self.eat("SEPARATOR")
                    # Handle empty arguments like IF(A1,,B1)
                    if self.current_token() and self.current_token().type in (
                        "SEPARATOR",
                        "PAREN_R",
                    ):
                        args.append(
                            StringNode("")
                        )  # Treat empty arg as empty string or we can hold None
                    else:
                        args.append(self.expr())
            self.eat("PAREN_R")
            return FunctionNode(name=func_name, args=args)

        raise ParserError(f"Unexpected token {tok} in factor")


def parse_formula(tokens: List[Token]) -> ASTNode:
    parser = Parser(tokens)
    return parser.parse()
