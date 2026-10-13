"""FinCalc: an educational command-line financial mathematics calculator.

All rates are annual percentages unless documented otherwise.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path


MONEY = Decimal("0.01")
PERCENT = Decimal("0.01")


class FinancialInputError(ValueError):
    """Raised when a financial calculation receives an invalid input."""


def to_decimal(value: object, *, label: str) -> Decimal:
    """Convert textual or numeric input to a finite Decimal."""
    if isinstance(value, bool):
        raise FinancialInputError(f"{label} must be numeric.")
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        raise FinancialInputError(f"{label} must be numeric.") from None
    if not number.is_finite():
        raise FinancialInputError(f"{label} must be finite.")
    return number


def require_positive(value: Decimal, label: str, *, allow_zero: bool = False) -> Decimal:
    if value < 0 or (value == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "greater than zero"
        raise FinancialInputError(f"{label} must be {qualifier}.")
    return value


def money(value: Decimal) -> str:
    return f"{value.quantize(MONEY, rounding=ROUND_HALF_UP):,.2f}"


def compound_interest(principal: object, annual_rate: object, years: object, compounds_per_year: int = 12) -> Decimal:
    """Future value after periodic compounding; annual_rate is percent."""
    p = require_positive(to_decimal(principal, label="Principal"), "Principal", allow_zero=True)
    rate = to_decimal(annual_rate, label="Annual rate") / Decimal(100)
    t = require_positive(to_decimal(years, label="Years"), "Years", allow_zero=True)
    if isinstance(compounds_per_year, bool) or not isinstance(compounds_per_year, int) or compounds_per_year < 1:
        raise FinancialInputError("Compounds per year must be a positive integer.")
    periods = t * compounds_per_year
    if periods != periods.to_integral_value():
        raise FinancialInputError("Years must result in a whole number of compounding periods.")
    base = Decimal(1) + rate / compounds_per_year
    if base <= 0:
        raise FinancialInputError("Rate is too negative for the selected compounding frequency.")
    with localcontext() as ctx:
        ctx.prec = 36
        return +(p * (base ** int(periods)))


def loan_emi(principal: object, annual_rate: object, years: object) -> Decimal:
    """Equal monthly installment for a loan with nominal annual interest percent."""
    p = require_positive(to_decimal(principal, label="Principal"), "Principal")
    rate = require_positive(to_decimal(annual_rate, label="Annual rate"), "Annual rate", allow_zero=True) / Decimal(1200)
    years_dec = require_positive(to_decimal(years, label="Years"), "Years")
    months = years_dec * 12
    if months != months.to_integral_value():
        raise FinancialInputError("Loan duration must contain a whole number of months.")
    n = int(months)
    if rate == 0:
        return p / n
    with localcontext() as ctx:
        ctx.prec = 36
        factor = (1 + rate) ** n
        return +(p * rate * factor / (factor - 1))


def investment_cagr(start_value: object, end_value: object, years: object) -> Decimal:
    """Annualized compounded growth rate as a percentage."""
    begin = require_positive(to_decimal(start_value, label="Beginning value"), "Beginning value")
    end = require_positive(to_decimal(end_value, label="Ending value"), "Ending value")
    t = require_positive(to_decimal(years, label="Years"), "Years")
    with localcontext() as ctx:
        ctx.prec = 36
        return +(((end / begin) ** (Decimal(1) / t) - 1) * 100)


def present_value(future_value: object, discount_rate: object, years: object) -> Decimal:
    """Value today of one future amount, discounted annually."""
    future = require_positive(to_decimal(future_value, label="Future value"), "Future value", allow_zero=True)
    rate = to_decimal(discount_rate, label="Discount rate") / Decimal(100)
    t = require_positive(to_decimal(years, label="Years"), "Years", allow_zero=True)
    if rate <= -1:
        raise FinancialInputError("Discount rate must exceed -100%.")
    with localcontext() as ctx:
        ctx.prec = 36
        return +(future / ((Decimal(1) + rate) ** t))


def amortization_schedule(principal: object, annual_rate: object, years: object) -> list[dict[str, Decimal | int]]:
    """Monthly payment detail; retains full precision until amounts are displayed."""
    p = require_positive(to_decimal(principal, label="Principal"), "Principal")
    annual = require_positive(to_decimal(annual_rate, label="Annual rate"), "Annual rate", allow_zero=True)
    duration = require_positive(to_decimal(years, label="Years"), "Years")
    count = duration * 12
    if count != count.to_integral_value():
        raise FinancialInputError("Loan duration must contain a whole number of months.")
    payment = loan_emi(p, annual, duration)
    monthly_rate = annual / 1200
    remaining = p
    rows: list[dict[str, Decimal | int]] = []
    with localcontext() as ctx:
        ctx.prec = 36
        for month in range(1, int(count) + 1):
            interest = remaining * monthly_rate
            principal_paid = min(remaining, payment - interest)
            if month == int(count):
                principal_paid = remaining
            this_payment = interest + principal_paid
            remaining -= principal_paid
            if remaining < Decimal("0.00000001"):
                remaining = Decimal(0)
            rows.append({"month": month, "payment": +this_payment, "principal": +principal_paid,
                         "interest": +interest, "balance": +remaining})
    return rows


def record_history(path: Path, tool: str, inputs: dict[str, str], result: Decimal) -> None:
    """Append a CSV history entry, creating headers for a new file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(["timestamp_utc", "calculator", "inputs", "result"])
        writer.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"), tool,
                         "; ".join(f"{key}={value}" for key, value in inputs.items()), str(result)])


TOOLS = {
    "compound": (compound_interest, ["principal", "annual_rate", "years", "compounds_per_year"]),
    "emi": (loan_emi, ["principal", "annual_rate", "years"]),
    "cagr": (investment_cagr, ["start_value", "end_value", "years"]),
    "pv": (present_value, ["future_value", "discount_rate", "years"]),
}

LABELS = {"compound": "Future value", "emi": "Monthly EMI", "cagr": "Annualized growth", "pv": "Present value"}
DISPLAY_NAMES = {"compound": "Compound interest", "emi": "Loan EMI", "cagr": "Investment CAGR", "pv": "Present value"}


def calculate(tool: str, values: dict[str, str]) -> Decimal:
    function, fields = TOOLS[tool]
    arguments: list[object] = [values[field] for field in fields if field in values]
    if tool == "compound" and "compounds_per_year" in values:
        try:
            periods = int(values["compounds_per_year"])
        except ValueError:
            raise FinancialInputError("Compounds per year must be an integer.") from None
        arguments[-1] = periods
    return function(*arguments)


def format_result(tool: str, result: Decimal) -> str:
    display = f"{result.quantize(PERCENT, rounding=ROUND_HALF_UP):,.2f}%" if tool == "cagr" else money(result)
    return f"{LABELS[tool]}: {display}"


def run_interactive(history: Path | None) -> int:
    options = [("1", "compound"), ("2", "emi"), ("3", "cagr"), ("4", "pv")]
    while True:
        print("\n=== FinCalc | Financial Calculator ===")
        for number, tool in options:
            print(f" {number}. {DISPLAY_NAMES[tool]}")
        print(" 5. Loan amortization summary\n 0. Exit")
        try:
            choice = input("Choose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0
        if choice == "0":
            print("Goodbye!")
            return 0
        if choice == "5":
            try:
                entries = {key: input(f"{key.replace('_', ' ').title()}: ").strip() for key in ["principal", "annual_rate", "years"]}
                schedule = amortization_schedule(**entries)
                total_interest = sum((row["interest"] for row in schedule), Decimal(0))
                print(f"Monthly EMI: {money(loan_emi(**entries))}\nTotal interest: {money(total_interest)}\nMonths: {len(schedule)}")
            except FinancialInputError as exc:
                print(f"Input error: {exc}")
            continue
        matching = dict(options).get(choice)
        if not matching:
            print("Invalid option. Enter a number from 0 to 5.")
            continue
        _, names = TOOLS[matching]
        try:
            values = {}
            for name in names:
                if name == "compounds_per_year":
                    typed = input("Compounds per year [12]: ").strip()
                    values[name] = typed or "12"
                else:
                    values[name] = input(f"{name.replace('_', ' ').title()}: ").strip()
            result = calculate(matching, values)
            print(format_result(matching, result))
            if history is not None:
                record_history(history, matching, values, result)
        except FinancialInputError as exc:
            print(f"Input error: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nReturning to menu.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FinCalc: educational financial mathematics calculator")
    parser.add_argument("--history", metavar="CSV", type=Path, help="Optional CSV file to record successful calculations")
    subs = parser.add_subparsers(dest="tool")
    for name, (_, fields) in TOOLS.items():
        sub = subs.add_parser(name, help=DISPLAY_NAMES[name])
        for field in fields:
            if field == "compounds_per_year":
                sub.add_argument("--compounds-per-year", default="12")
            else:
                sub.add_argument(f"--{field.replace('_', '-')}", required=True)
    schedule = subs.add_parser("schedule", help="Export a monthly loan amortization schedule")
    for field in ("principal", "annual_rate", "years"):
        schedule.add_argument(f"--{field.replace('_', '-')}", required=True)
    schedule.add_argument("--output", type=Path, required=True, help="Destination CSV file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.tool is None:
        return run_interactive(args.history)
    if args.tool == "schedule":
        try:
            rows = amortization_schedule(args.principal, args.annual_rate, args.years)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=["month", "payment", "principal", "interest", "balance"])
                writer.writeheader()
                for row in rows:
                    writer.writerow({key: money(value) if key != "month" else value for key, value in row.items()})
            print(f"Saved {len(rows)} monthly rows to {args.output}")
            return 0
        except (FinancialInputError, OSError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
    fields = TOOLS[args.tool][1]
    values = {field: str(getattr(args, field)) for field in fields}
    try:
        result = calculate(args.tool, values)
        print(format_result(args.tool, result))
        if args.history is not None:
            record_history(args.history, args.tool, values, result)
        return 0
    except (FinancialInputError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
