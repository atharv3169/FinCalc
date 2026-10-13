# FinCalc

**Video Demo:** [YouTube link to be added]

## About

FinCalc is a small Python financial calculator that runs in the terminal. It handles four common calculations: compound interest, loan EMI, investment CAGR, and present value. There's also a loan repayment summary, with the option to export a monthly payment schedule to CSV.

I wanted to keep the program straightforward to use. You select an option from the menu, enter the amounts and rates, and see the result. It also checks for invalid inputs, such as negative loan amounts or text where a number is expected.

## Files

- **project.py** — The calculator itself: menu, formulas, input checks, command-line options, and CSV exports.
- **test_project.py** — Pytest tests for the formulas, invalid inputs, and file output.
- **requirements.txt** — Lists pytest, which is only needed for running tests.
- **.gitignore** — Keeps temporary Python files and generated CSV files out of Git.

## Running it

Use Python 3.10 or newer. Open a terminal in the project folder and run:

```bash
python project.py
```

Choose a calculation from the menu and follow the prompts. Rates are entered as percentages, so type `12` for 12%, not `0.12`.

You can also run calculations directly. For example:

```bash
python project.py compound --principal 1000 --annual-rate 12 --years 1
```

For a loan repayment schedule:

```bash
python project.py schedule --principal 1200 --annual-rate 0 --years 1 --output schedule.csv
```

## How it works

The calculations are separate functions so they can be tested without running the menu. I used Python's `Decimal` type for the amounts to avoid some of the rounding issues that come with ordinary floating-point numbers. Results are displayed to two decimal places. The CSV export is useful if someone wants to inspect the payment schedule in Excel.

The calculator makes a few simplifying assumptions: interest rates stay fixed, payments are monthly for loans, and it doesn't account for fees, taxes, or deposits and withdrawals during an investment period.

## Tests

Install pytest and run the test suite:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

The 30 tests cover the main calculations, input validation, loan schedules, and command-line use.
