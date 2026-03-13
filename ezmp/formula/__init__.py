from .lexer import tokenize, LexerError, Token
from .parser import parse_formula, ParserError, ASTNode
from .evaluator import Evaluator, EvaluationContext
from .errors import ExcelError, FormulaError
from .functions import register, FUNCTION_REGISTRY


def evaluate_formula_string(formula_str: str, ref_getter=None):
    """
    Evaluates a raw Excel formula string (e.g. '=VLOOKUP(A1, Sheet2!A:Z, 2)')
    and computes the final real value.
    ref_getter is a callback function that resolves cell/range queries (like 'A1' or 'Sheet2!B:C').
    """
    try:
        tokens = tokenize(formula_str)
        ast = parse_formula(tokens)

        context = EvaluationContext(ref_getter)
        evaluator = Evaluator(context)
        return evaluator.evaluate(ast)

    except (LexerError, ParserError):
        # If we can't parse the formula (unsupported syntax, etc), default to #NAME?
        return ExcelError("#NAME?")
    except Exception:
        return ExcelError("#VALUE!")
