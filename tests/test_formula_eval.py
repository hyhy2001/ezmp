from ezmp.formula import evaluate_formula_string, ExcelError


def mock_ref_getter(ref: str):
    data = {
        "A1": 10,
        "A2": 20,
        "A3": 30,
        "Sheet2!A:C": [["apple", 5, 50], ["banana", 8, 80], ["cherry", 12, 120]],
    }
    return data.get(ref, None)


def test_eval_math_basic():
    # 10 + 20 * 2 = 50
    res = evaluate_formula_string("=A1 + A2 * 2", mock_ref_getter)
    assert res == 50


def test_eval_logic():
    # 10 > 5 -> True
    res = evaluate_formula_string("=A1 > 5", mock_ref_getter)
    assert res is True

    # 20 <> 20 -> False
    res = evaluate_formula_string("=A2 <> 20", mock_ref_getter)
    assert res is False


def test_eval_sum():
    res = evaluate_formula_string("=SUM(A1, A2, A3)", mock_ref_getter)
    assert res == 60


def test_eval_if():
    res = evaluate_formula_string('=IF(A1 > 5, "Large", "Small")', mock_ref_getter)
    assert res == "Large"

    res = evaluate_formula_string('=IF(A1 < 5, "Large", "Small")', mock_ref_getter)
    assert res == "Small"


def test_eval_vlookup():
    # Find "banana" in col 1, return col 3 (80)
    res = evaluate_formula_string(
        '=VLOOKUP("banana", Sheet2!A:C, 3, FALSE)', mock_ref_getter
    )
    assert res == 80

    res = evaluate_formula_string(
        '=VLOOKUP("dragonfruit", Sheet2!A:C, 3, FALSE)', mock_ref_getter
    )
    assert isinstance(res, ExcelError) and res.code == "#N/A"


def test_eval_vlookup_error():
    # Missing col
    res = evaluate_formula_string(
        '=VLOOKUP("cherry", Sheet2!A:C, 5, FALSE)', mock_ref_getter
    )
    assert isinstance(res, ExcelError) and res.code == "#REF!"


def test_eval_text():
    res = evaluate_formula_string('=LEFT("Hello", 2)', mock_ref_getter)
    assert res == "He"

    res = evaluate_formula_string('=RIGHT("World", 3)', mock_ref_getter)
    assert res == "rld"

    res = evaluate_formula_string('=LEN("ezmp")', mock_ref_getter)
    assert res == 4

    res = evaluate_formula_string('=CONCAT("A", "-", "B")', mock_ref_getter)
    assert res == "A-B"


def test_error_propagation():
    # Division by zero
    res = evaluate_formula_string("=10 / 0", mock_ref_getter)
    assert isinstance(res, ExcelError) and res.code == "#DIV/0!"

    # IFERROR traps it
    res = evaluate_formula_string('=IFERROR(10 / 0, "Fixed")', mock_ref_getter)
    assert res == "Fixed"
