import datetime
from typing import Callable, Any, List
from .errors import ExcelError

FUNCTION_REGISTRY = {}


def register(name: str):
    """
    Decorator to register an Excel function into the AST engine.
    Allows easy injection of custom implementations by the user.
    """

    def decorator(func: Callable):
        FUNCTION_REGISTRY[name.upper()] = func
        return func

    return decorator


def _flatten_args(args: List[Any], skip_errors=False) -> List[Any]:
    flat = []
    for arg in args:
        if isinstance(arg, ExcelError) and not skip_errors:
            return [arg]  # Short-circuit
        if isinstance(arg, (list, tuple)):
            nested = _flatten_args(arg, skip_errors=skip_errors)
            if nested and isinstance(nested[0], ExcelError) and not skip_errors:
                return nested
            flat.extend(nested)
        else:
            flat.append(arg)
    return flat


def _to_float(val: Any) -> float:
    if val is None or val == "":
        return 0.0
    if isinstance(val, bool):
        return 1.0 if val else 0.0
    try:
        return float(val)
    except Exception:
        raise ExcelError("#VALUE!")


# --- 1. Basic Math ---
@register("SUM")
def excel_sum(args: List[Any]) -> Any:
    flat = _flatten_args(args)
    if flat and isinstance(flat[0], ExcelError):
        return flat[0]
    total = 0.0
    for v in flat:
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            total += v
        elif isinstance(v, str):
            try:
                # Excel SUM ignores text strings in ranges, but tries to parse direct strings.
                # To be safe, we just ignore strings like Excel does for range selections.
                pass
            except Exception:
                pass
    return total


@register("AVERAGE")
def excel_average(args: List[Any]) -> Any:
    flat = _flatten_args(args)
    if flat and isinstance(flat[0], ExcelError):
        return flat[0]
    total = 0.0
    count = 0
    for v in flat:
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            total += v
            count += 1
    if count == 0:
        return ExcelError("#DIV/0!")
    return total / count


@register("MIN")
def excel_min(args: List[Any]) -> Any:
    flat = [
        v
        for v in _flatten_args(args)
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    ]
    return min(flat) if flat else 0


@register("MAX")
def excel_max(args: List[Any]) -> Any:
    flat = [
        v
        for v in _flatten_args(args)
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    ]
    return max(flat) if flat else 0


@register("COUNT")
def excel_count(args: List[Any]) -> Any:
    flat = _flatten_args(args)
    return sum(
        1 for v in flat if isinstance(v, (int, float)) and not isinstance(v, bool)
    )


@register("COUNTA")
def excel_counta(args: List[Any]) -> Any:
    flat = _flatten_args(args)
    return sum(1 for v in flat if v is not None and v != "")


# --- 2. Logic & Conditional ---
@register("IF")
def excel_if(args: List[Any]) -> Any:
    if len(args) < 2 or len(args) > 3:
        return ExcelError("#VALUE!")
    cond = args[0]
    if isinstance(cond, ExcelError):
        return cond

    is_true = False
    if isinstance(cond, bool):
        is_true = cond
    elif isinstance(cond, (int, float)):
        is_true = cond != 0
    elif isinstance(cond, str):
        is_true = cond.upper() == "TRUE"

    if is_true:
        return args[1]
    else:
        if len(args) == 3:
            return args[2]
        else:
            return False


@register("IFERROR")
def excel_iferror(args: List[Any]) -> Any:
    if len(args) != 2:
        return ExcelError("#VALUE!")
    val = args[0]
    if isinstance(val, ExcelError):
        return args[1]
    return val


# Very simplified implementations for SUMIF/COUNTIF
@register("COUNTIF")
def excel_countif(args: List[Any]) -> Any:
    if len(args) != 2:
        return ExcelError("#VALUE!")
    range_flat = _flatten_args([args[0]])
    criteria = args[1]

    count = 0
    for v in range_flat:
        if str(v).lower() == str(criteria).lower():
            count += 1
    return count


@register("SUMIF")
def excel_sumif(args: List[Any]) -> Any:
    if len(args) not in (2, 3):
        return ExcelError("#VALUE!")
    range_vals = _flatten_args([args[0]])
    criteria = args[1]
    sum_vals = _flatten_args([args[2]]) if len(args) == 3 else range_vals

    total = 0.0
    for i, v in enumerate(range_vals):
        if str(v).lower() == str(criteria).lower() and i < len(sum_vals):
            num = sum_vals[i]
            if isinstance(num, (int, float)):
                total += num
    return total


# --- 3. Lookup & Reference ---
@register("VLOOKUP")
def excel_vlookup(args: List[Any]) -> Any:
    if len(args) not in (3, 4):
        return ExcelError("#VALUE!")
    lookup_val = args[0]
    table_array = args[1]  # Expected to be a 2D list (list of rows)
    col_index = _to_float(args[2])
    exact_match = (
        False if len(args) == 4 and str(args[3]).upper() == "TRUE" else True
    )  # default False match in excel is Exact string match

    if isinstance(lookup_val, ExcelError):
        return lookup_val
    if not isinstance(table_array, list):
        return ExcelError("#N/A")
    if col_index < 1:
        return ExcelError("#VALUE!")

    idx = int(col_index) - 1
    # Simple top-down exact match
    for row in table_array:
        if not isinstance(row, list):
            continue
        if len(row) > 0 and str(row[0]).lower() == str(lookup_val).lower():
            if idx < len(row):
                return row[idx]
            else:
                return ExcelError("#REF!")
    return ExcelError("#N/A")


# --- 4. Text & Date ---
@register("LEFT")
def excel_left(args: List[Any]) -> Any:
    if len(args) not in (1, 2):
        return ExcelError("#VALUE!")
    text = str(args[0])
    chars = int(_to_float(args[1])) if len(args) == 2 else 1
    if chars < 0:
        return ExcelError("#VALUE!")
    return text[:chars]


@register("RIGHT")
def excel_right(args: List[Any]) -> Any:
    if len(args) not in (1, 2):
        return ExcelError("#VALUE!")
    text = str(args[0])
    chars = int(_to_float(args[1])) if len(args) == 2 else 1
    if chars < 0:
        return ExcelError("#VALUE!")
    return text[-chars:] if chars > 0 else ""


@register("LEN")
def excel_len(args: List[Any]) -> Any:
    if len(args) != 1:
        return ExcelError("#VALUE!")
    return len(str(args[0]))


@register("CONCAT")
def excel_concat(args: List[Any]) -> Any:
    flat = [str(v) for v in _flatten_args(args) if v is not None]
    return "".join(flat)


@register("NOW")
def excel_now(args: List[Any]) -> Any:
    return datetime.datetime.now()


@register("TODAY")
def excel_today(args: List[Any]) -> Any:
    return datetime.datetime.now().date()
