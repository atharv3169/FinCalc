# FinCalc browser edition

This directory is a **standalone, dependency-free browser edition** of the
Python calculations in `../project.py`. Its public page provides compound
interest, loan EMI and amortization CSV, investment CAGR, present value,
and in-tab calculation-history CSV. The original Python terminal version remains
unchanged.

## Preview

Open `web/index.html` with a static HTTP server (ES module imports need HTTP),
for example:

```sh
python -m http.server 8000
# Visit http://localhost:8000/web/
node --test web/core.test.mjs
```

## Hosting under FundLenz

The web application remains **source-controlled in the separate FinCalc
repository**. FundLenz can host a reviewed static copy under
`public/projects/fincalc/`. Its Next route at `/fincalc` displays this
same-origin browser application. No Python runtime, external API, external CDN,
Cloudflare token, separate Worker, or production financial dataset is required.

When modifying browser files here, sync `web/index.html`, `web/app.mjs`,
`web/core.mjs`, and `web/styles.css` into the matching FundLenz public
directory and run both repositories' tests before publishing. Avoid changing
the FundLenz finance engine or catalogue scripts when updating FinCalc.

## Methodology

The formulas are ported from the Python `Decimal` implementation. Browser
JavaScript operates on IEEE-754 numbers, which means extended precision is
different from the CLI. The displayed value and CSV exports are rounded to two
decimal places. Amounts are unit-neutral; no exchange rates or taxes are
estimated. Fixed nominal interest rates and level EMI installments are assumed.
History is held **only in memory** and is not uploaded or permanently saved.
This is an educational calculator, not investment or lending advice.
