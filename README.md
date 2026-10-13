# FinCalc — Financial Calculator

#### Video Demo: [Add your YouTube demonstration URL here before submitting]

#### Description:

FinCalc is a command-line financial calculator written in Python. It brings together several commonly used financial mathematics calculations in a single menu-driven application and also provides command-line commands for repeatable calculations. Its principal features are compound interest, loan EMI (equated monthly installment), investment compound annual growth rate (CAGR), present value, and loan amortization. It can optionally record successful calculations in a CSV history file, and it can export a detailed repayment schedule as a CSV file.

The compound-interest calculator estimates how much an initial amount will be worth after a specified number of years, given an annual percentage rate and a compounding frequency. The default frequency is monthly, but the application also accepts other positive integer frequencies. The EMI calculator estimates the fixed monthly installment for a loan using its principal, annual interest rate, and duration. CAGR expresses the annualized rate at which an investment grew (or declined) between two values. Present value discounts a future amount using a specified discount rate. These results are calculations based on user-provided assumptions, rather than financial advice or forecasts.

## Files

- **`project.py`** contains the program's `main()` entry point, the interactive menu, all financial formulas, input-validation helpers, output formatting, CSV history support, and amortization CSV export. Each main calculation is implemented as an independently callable Python function. The same module provides a command-line argument parser so users can automate calculations without opening the menu.
- **`test_project.py`** contains automated tests built with `pytest`. It verifies the calculations against known examples and checks exceptional inputs such as negative loan principal, invalid rates, non-numeric values, zero-length investment periods, and non-finite numeric inputs. Additional tests cover the CSV output and command-line behavior.
- **`requirements.txt`** declares `pytest` as a development and testing dependency. The financial calculator itself uses Python's standard library, so normal use does not require third-party packages.
- **`.gitignore`** excludes local Python caches, virtual environments, and generated CSV files from version control.

## Installation and usage

Use Python **3.10 or newer**. From the project directory, start the interactive menu with:

```bash
python project.py
```

The menu offers the four main calculators, a loan amortization summary, and an exit option. Enter numbers when prompted. Annual interest rates are percentages: an entry of `12` means twelve percent, not `0.12`. When choosing a duration, some calculations require a whole number of monthly or compounding periods. The application rejects inputs that do not meet these conditions and explains the problem rather than silently returning an invalid result.

For a command-line calculation, try:

```bash
python project.py compound --principal 1000 --annual-rate 12 --years 1
python project.py emi --principal 100000 --annual-rate 12 --years 1
python project.py cagr --start-value 100 --end-value 121 --years 2
python project.py pv --future-value 110 --discount-rate 10 --years 1
```

To export a repayment schedule to a file:

```bash
python project.py schedule --principal 1200 --annual-rate 0 --years 1 --output schedule.csv
```

To record calculations as CSV history, add the global `--history history.csv` option **before** a subcommand. For example:

```bash
python project.py --history history.csv pv --future-value 110 --discount-rate 10 --years 1
```

## Design decisions

The application uses Python's `Decimal` class for financial arithmetic rather than binary floating-point values. This reduces some rounding surprises associated with representing decimal amounts as floats. Calculations retain additional precision until amounts are displayed with two decimal places, using half-up rounding. Finance operations are kept separate from prompts and printing so they can be tested independently. The `argparse` interface complements the interactive menu, making it possible to use the calculator in scripts. A CSV format was chosen for history and amortization output because it is easy to inspect and open in spreadsheet applications without adding dependencies.

There are practical limitations. The model assumes constant rates, does not model taxes, fees, changing interest rates, irregular payment dates, or investment contributions and withdrawals, and cannot predict market returns. Loan EMI uses a fixed nominal annual rate divided into monthly periods. CAGR assumes only a beginning value, ending value, and elapsed time, so it does not account for intermediate cash flows.

## Testing

Install the testing dependency and run:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

The test suite checks numerical outputs, error handling, file export, and the command-line entry point. For a demonstration, show at least one successful calculation, one invalid-input example, and the automated test output. A video demonstration of no more than three minutes is required separately; replace the placeholder link at the top of this README with its published YouTube URL before any course submission.
