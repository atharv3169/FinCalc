"""Regression and boundary tests for FinCalc."""

from decimal import Decimal

import pytest

from fincalc import (
    FinancialInputError, amortization_schedule, calculate, compound_interest,
    investment_cagr, loan_emi, main, money, present_value, record_history,
    to_decimal,
)


def near(actual, expected, tolerance="0.01"):
    assert abs(actual - Decimal(str(expected))) <= Decimal(tolerance)


def test_compound_interest():
    near(compound_interest(1000, 12, 1, 12), "1126.83")
    assert compound_interest(500, 0, 5) == 500
    assert compound_interest(500, 6, 0) == 500
    assert compound_interest(100, -5, 1, 1) == Decimal("95")


def test_loan_emi():
    near(loan_emi(100000, 12, 1), "8884.88")
    near(loan_emi(1200, 0, 1), "100")


def test_investment_cagr():
    near(investment_cagr(100, 121, 2), "10")
    near(investment_cagr(100, 81, 2), "-10")
    near(investment_cagr(50, 50, 3), "0")


def test_present_value():
    near(present_value(110, 10, 1), "100")
    assert present_value(500, 0, 10) == 500
    assert present_value(0, 4, 2) == 0


@pytest.mark.parametrize("fn,args", [
    (compound_interest, (-1, 5, 2)),
    (compound_interest, (100, -101, 1, 1)),
    (compound_interest, (100, 5, 0.1, 12)),
    (loan_emi, (0, 5, 2)),
    (loan_emi, (500, -1, 2)),
    (loan_emi, (500, 5, 0.15)),
    (investment_cagr, (0, 120, 2)),
    (investment_cagr, (100, 0, 2)),
    (investment_cagr, (100, 200, 0)),
    (present_value, (100, -100, 2)),
    (present_value, (100, 5, -2)),
    (present_value, (float('inf'), 5, 2)),
])
def test_invalid_inputs(fn, args):
    with pytest.raises(FinancialInputError):
        fn(*args)


@pytest.mark.parametrize("bad", ["", "abc", "NaN", "Infinity", None, True])
def test_to_decimal_rejects_bad_input(bad):
    with pytest.raises(FinancialInputError):
        to_decimal(bad, label="Value")


def test_amortization_schedule():
    rows = amortization_schedule(1200, 0, 1)
    assert len(rows) == 12
    assert rows[0]["payment"] == Decimal("100")
    assert rows[-1]["balance"] == 0
    rows2 = amortization_schedule(100000, 12, 1)
    assert rows2[-1]["balance"] == 0
    near(sum((row["principal"] for row in rows2), Decimal(0)), 100000, "0.000001")


def test_money_rounding():
    assert money(Decimal("1234.565")) == "1,234.57"


def test_calculate_dispatch():
    near(calculate("compound", {"principal": "100", "annual_rate": "10", "years": "1", "compounds_per_year": "1"}), 110)
    near(calculate("cagr", {"start_value": "100", "end_value": "121", "years": "2"}), 10)


def test_history_csv(tmp_path):
    file = tmp_path / "nested" / "log.csv"
    record_history(file, "pv", {"future_value": "110"}, Decimal("100"))
    record_history(file, "pv", {"future_value": "121"}, Decimal("110"))
    import csv
    with file.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["result"] == "100"


def test_command_line_compound(capsys):
    code = main(["compound", "--principal", "1000", "--annual-rate", "12", "--years", "1"])
    assert code == 0
    assert "1,126.83" in capsys.readouterr().out


def test_command_line_schedule(tmp_path):
    output = tmp_path / "schedule.csv"
    assert main(["schedule", "--principal", "1200", "--annual-rate", "0", "--years", "1", "--output", str(output)]) == 0
    assert len(output.read_text().splitlines()) == 13


def test_command_line_invalid(capsys):
    assert main(["emi", "--principal", "-10", "--annual-rate", "10", "--years", "1"]) == 2
    assert "Error" in capsys.readouterr().err


def test_interactive_exit(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "0")
    assert main([]) == 0
    assert "Goodbye" in capsys.readouterr().out
