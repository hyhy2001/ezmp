import re
from typing import List, NamedTuple, Any


class Token(NamedTuple):
    type: str
    value: Any


# Regex patterns for Excel tokens
# Note: Order matters. We must match longer/specific patterns before general ones.
TOKEN_SPEC = [
    ("EXCEL_ERROR", r"\#[A-Z0-9\/]+[!\?]?"),  # #N/A, #VALUE!, #DIV/0!
    ("FUNCTION", r"[A-Za-z0-9_]+\("),  # SUM(, VLOOKUP(
    (
        "RANGE",
        r"[A-Za-z0-9_]+![A-Za-z0-9_\$]+:[A-Za-z0-9_\$]+|[A-Za-z0-9_\$]+:[A-Za-z0-9_\$]+",
    ),  # Sheet1!A1:B2 or A1:B2
    (
        "REFERENCE",
        r"[A-Za-z0-9_]+![A-Za-z0-9_\$]+|[A-Za-z\$]+[0-9\$]+",
    ),  # Sheet1!A1 or $A$1 or A1
    ("NUMBER", r"\d+(\.\d*)?"),  # 123 or 123.45
    ("STRING", r'"[^"]*"'),  # "hello"
    ("BOOLEAN", r"\b(TRUE|FALSE)\b"),  # TRUE / FALSE
    ("OPERATOR", r"<=|>=|<>|<|>|=|&|\+|\-|\*|\/|\^"),  # Operators
    ("SEPARATOR", r"[,;]"),  # , or ;
    ("PAREN_R", r"\)"),  # )
    ("PAREN_L", r"\("),  # (
    ("WHITESPACE", r"[ \t]+"),  # Spaces
    ("MISMATCH", r"."),  # Any other character
]

TOKEN_REGEX = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC), re.IGNORECASE
)


class LexerError(Exception):
    pass


def tokenize(formula: str) -> List[Token]:
    """
    Tokenizes an Excel formula string into a list of Tokens.
    Strips the leading '=' if present.
    """
    if formula.startswith("="):
        formula = formula[1:]

    tokens = []
    for match in TOKEN_REGEX.finditer(formula):
        kind = match.lastgroup
        value = match.group()

        if kind == "WHITESPACE":
            continue
        elif kind == "MISMATCH":
            raise LexerError(f"Unexpected character in formula: {value!r}")

        if kind == "NUMBER":
            value = float(value) if "." in value else int(value)
        elif kind == "STRING":
            value = value[1:-1]  # Strip quotes
        elif kind == "BOOLEAN":
            value = value.upper() == "TRUE"
        elif kind == "FUNCTION":
            value = value[:-1].upper()  # Strip '(' and uppercase
            kind = "FUNCTION"
        elif kind == "EXCEL_ERROR":
            value = value.upper()
        elif kind in ("REFERENCE", "RANGE"):
            # Strip absolute reference locks for evaluation
            # e.g., $A$1 -> A1
            value = value.replace("$", "")

        tokens.append(Token(kind, value))

    return tokens
