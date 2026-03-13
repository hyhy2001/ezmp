from typing import Any, Callable, Optional, Union
from ezmp.formula.parser import (
    ASTNode,
    BinOpNode,
    FunctionNode,
    ReferenceNode,
    NumberNode,
    StringNode,
    BooleanNode,
    ErrorNode,
    UnaryOpNode,
)
from ezmp.formula.errors import ExcelError
from ezmp.formula.functions import FUNCTION_REGISTRY


class EvaluationContext:
    def __init__(self, ref_getter: Optional[Callable[[str], Any]] = None):
        """
        ref_getter: Function that takes a string like 'A1' or 'Sheet1!A1:B10'
        and returns the value from the workbook. For ranges, it should return a 2D list [[val, val], [val, val]].
        """
        self.ref_getter = ref_getter

    def get_reference(self, ref: str) -> Any:
        if self.ref_getter:
            return self.ref_getter(ref)
        return 0


class Evaluator:
    def __init__(self, context: EvaluationContext):
        self.context = context

    def evaluate(self, node: ASTNode) -> Any:
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, BooleanNode):
            return node.value
        elif isinstance(node, ErrorNode):
            return ExcelError(node.value)
        elif isinstance(node, ReferenceNode):
            return self.context.get_reference(node.value)
        elif isinstance(node, UnaryOpNode):
            val = self.evaluate(node.expr)
            if isinstance(val, ExcelError):
                return val

            try:
                if node.op == "-":
                    return -float(val)
                elif node.op == "+":
                    return float(val)
            except Exception:
                return ExcelError("#VALUE!")

        elif isinstance(node, BinOpNode):
            left = self.evaluate(node.left)

            # Short circuit IF optimizations or logical evaluations
            # Excel evaluates everything, but we can be slightly smarter if it doesn't affect side-effects
            right = self.evaluate(node.right)

            if isinstance(left, ExcelError):
                return left
            if isinstance(right, ExcelError):
                return right

            op = node.op
            if op == "&":
                return str(left if left is not None else "") + str(
                    right if right is not None else ""
                )

            # Comparisons
            if op in ("=", "<>", ">", "<", ">=", "<="):
                return self._compare(left, right, op)

            # Math operations
            try:
                lf = (
                    float(left) if left is not None and str(left).strip() != "" else 0.0
                )
                rf = (
                    float(right)
                    if right is not None and str(right).strip() != ""
                    else 0.0
                )
            except ValueError:
                return ExcelError("#VALUE!")

            try:
                if op == "+":
                    return lf + rf
                elif op == "-":
                    return lf - rf
                elif op == "*":
                    return lf * rf
                elif op == "/":
                    if rf == 0:
                        return ExcelError("#DIV/0!")
                    return lf / rf
                elif op == "^":
                    return lf**rf
            except OverflowError:
                return ExcelError("#NUM!")

        elif isinstance(node, FunctionNode):
            args = [self.evaluate(arg) for arg in node.args]
            func_name = node.name.upper()
            if func_name in FUNCTION_REGISTRY:
                return FUNCTION_REGISTRY[func_name](args)
            return ExcelError("#NAME?")

        return ExcelError("#VALUE!")

    def _compare(self, left: Any, right: Any, op: str) -> Union[bool, ExcelError]:
        # Excel cast logic: types usually must match, otherwise String > Number > Boolean(?)
        # For simplicity in this implementation, we convert to string for string-number mismatch
        # unless strictly typed.
        if type(left) != type(right):
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                pass  # let Python compare floats and ints
            else:
                left = str(left)
                right = str(right)

        try:
            if op == "=":
                return left == right
            elif op == "<>":
                return left != right
            elif op == ">":
                return left > right
            elif op == "<":
                return left < right
            elif op == ">=":
                return left >= right
            elif op == "<=":
                return left <= right
        except TypeError:
            return ExcelError("#VALUE!")
        return ExcelError("#VALUE!")
