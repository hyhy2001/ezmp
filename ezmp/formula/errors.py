class FormulaError(Exception):
    """Base exception for fundamental formula syntax errors."""

    pass


class ExcelError(Exception):
    """Represents a native Excel calculation error (e.g., #VALUE!, #DIV/0!)."""

    def __init__(self, code: str):
        self.code = code.upper()

    def __repr__(self):
        return f"ExcelError({self.code})"

    def __str__(self):
        return self.code

    def __eq__(self, other):
        if isinstance(other, ExcelError):
            return self.code == other.code
        return False
