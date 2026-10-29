import test from "node:test";
import assert from "node:assert/strict";
import {
  FinancialInputError, number, compoundInterest, loanEmi,
  amortizationSchedule, investmentCagr, presentValue,
  scheduleCsv, csv, format,
} from "./core.mjs";

const near = (actual, expected, tolerance = 0.011) =>
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} != ${expected}`);
test("compound interest matches the original Python example", () => {
  near(compoundInterest({ principal: 1000, annualRate: 12, years: 1,
    compoundsPerYear: 12 }).futureValue, 1126.83);
});
test("compound interest: zero rate and duration, negative rate", () => {
  near(compoundInterest({ principal: 500, annualRate: 0, years: 5 }).futureValue, 500);
  near(compoundInterest({ principal: 500, annualRate: 6, years: 0 }).futureValue, 500);
  near(compoundInterest({ principal: 100, annualRate: -5, years: 1,
    compoundsPerYear: 1 }).futureValue, 95);
});
test("compound interest rejects invalid compounding periods", () => {
  assert.throws(() => compoundInterest({ principal: 100, annualRate: 5,
    years: 0.1, compoundsPerYear: 12 }), FinancialInputError);
  assert.throws(() => compoundInterest({ principal: 100, annualRate: -101,
    years: 1, compoundsPerYear: 1 }), FinancialInputError);
  assert.throws(() => compoundInterest({ principal: 100, annualRate: 5,
    years: 1, compoundsPerYear: 2.5 }), FinancialInputError);
});
test("loan EMI matches source, including zero interest", () => {
  near(loanEmi({ principal: 100000, annualRate: 12, years: 1 }).payment, 8884.88);
  near(loanEmi({ principal: 1200, annualRate: 0, years: 1 }).payment, 100);
});
test("amortization schedule clears principal and has expected rows", () => {
  const a = amortizationSchedule({ principal: 1200, annualRate: 0, years: 1 });
  assert.equal(a.rows.length, 12);
  near(a.rows[0].payment, 100);
  near(a.rows[11].balance, 0);
  near(a.totalInterest, 0);
  const b = amortizationSchedule({ principal: 100000, annualRate: 12, years: 1 });
  assert.equal(b.rows.at(-1).balance, 0);
  near(b.rows.reduce((sum, row) => sum + row.principal, 0), 100000, 0.00001);
  near(b.rows.reduce((sum, row) => sum + row.interest, 0), b.totalInterest, 0.00001);
});
test("loan rejects negative rates, zero principal, and fractional months", () => {
  for (const values of [
    { principal: 0, annualRate: 4, years: 1 },
    { principal: 1000, annualRate: -1, years: 1 },
    { principal: 1000, annualRate: 5, years: 0.15 },
  ]) assert.throws(() => loanEmi(values), FinancialInputError);
});
test("CAGR covers positive and negative growth", () => {
  near(investmentCagr({ startValue: 100, endValue: 121, years: 2 }).cagr, 10);
  near(investmentCagr({ startValue: 100, endValue: 81, years: 2 }).cagr, -10);
  near(investmentCagr({ startValue: 50, endValue: 50, years: 3 }).cagr, 0);
});
test("CAGR rejects zero and negative values", () => {
  for (const values of [
    { startValue: 0, endValue: 100, years: 2 },
    { startValue: 100, endValue: 0, years: 2 },
    { startValue: 100, endValue: 200, years: 0 },
  ]) assert.throws(() => investmentCagr(values), FinancialInputError);
});
test("PV supports zero value and annual discounting", () => {
  near(presentValue({ futureValue: 110, discountRate: 10, years: 1 }).presentValue, 100);
  near(presentValue({ futureValue: 500, discountRate: 0, years: 10 }).presentValue, 500);
  near(presentValue({ futureValue: 0, discountRate: 4, years: 2 }).presentValue, 0);
});
test("PV rejects discount rates at or under -100%", () => {
  assert.throws(() => presentValue({ futureValue: 100, discountRate: -100, years: 1 }),
    FinancialInputError);
});
test("number validation rejects unsafe input", () => {
  for (const value of ["", "NaN", "Infinity", "abc", "1e99", "1,000", "1+2", null, true, "  "]) {
    assert.throws(() => number(value, "Amount"), FinancialInputError);
  }
});
test("limits reject calculation overflow and excessive schedules", () => {
  assert.throws(() => compoundInterest({ principal: "1000000000000",
    annualRate: "100000", years: "100", compoundsPerYear: 12 }), FinancialInputError);
  assert.throws(() => loanEmi({ principal: 1000, annualRate: 1, years: 101 }),
    FinancialInputError);
});
test("currency and percentage formatting", () => {
  assert.equal(format(1234.565), "1,234.57");
  assert.equal(format(-10, true), "-10.00%");
});
test("amortization CSV preserves headers and rows", () => {
  const r = amortizationSchedule({ principal: 1200, annualRate: 0, years: 1 });
  const text = scheduleCsv(r.rows);
  assert.ok(text.startsWith('"month","payment","principal","interest","balance"\r\n'));
  assert.equal(text.trim().split("\r\n").length, 13);
  assert.match(text, /"12","100.00","100.00","0.00","0.00"/);
});
test("history CSV escapes quotes and commas", () => {
  const text = csv([{ timestamp_utc: "2026-10-29", calculator: 'PV "test"', inputs: '{"value":"3,4"}',
    result: "100.00" }], ["timestamp_utc", "calculator", "inputs", "result"]);
  assert.ok(text.includes('"PV ""test"""'));
  assert.ok(text.includes('"{""value"":""3,4""}"'));
});
