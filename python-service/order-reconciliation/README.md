# Order & Payment Reconciliation — Tested Python + Excel Demo

**Independent demonstration.** All customer names, order IDs and amounts are invented. This was not a paid assignment.

## The buyer problem
Two exports disagree: some completed orders have no matching settlement, some have incorrect amounts, others appear twice, and invalid rows must not disappear silently. A user needs a repeatable reconciliation and auditable exception report.

## What it does
- Reads order and settlement CSV exports; validates headers, statuses and currency.
- Matches by normalized order ID and compares amounts using decimal arithmetic rather than binary floating point.
- Separately identifies duplicate order IDs, duplicate settlement IDs, missing settlements, amount mismatches, unmatched payments and unexpected payments against pending orders.
- Outputs matched.csv, exceptions.csv, rejected_rows.csv, summary.json and a five-tab Excel reconciliation.xlsx.
- Preserves source row numbers for invalid input; no hidden credentials or third-party APIs.

## Run
Python 3.10+ recommended.

Install dependencies:
    python -m pip install -r requirements.txt

Execute on sample data:
    python reconcile.py --orders sample_input/orders.csv --payments sample_input/payments.csv --out output

Run automated tests:
    python -m unittest discover -s tests -v

For development on the original PC only, dependencies were installed in the local uncommitted vendor directory on D:. A normal environment can install via requirements.txt.

## Synthetic test-case expected results
- 2 matched order IDs
- 1 amount mismatch
- 1 missing payment
- 1 payment without a valid matching order
- 1 duplicate order ID
- 1 duplicate settlement ID
- 1 pending order excluded
- 2 rejected source rows with reasons
- 8 unique valid IDs inspected including payment-only IDs

These are counts on synthetic inputs, not claims about a real business or time savings.

## Deliverables and scope
This shows a bounded local reconciliation workflow: validated input, explicit exceptions, Excel summary and reproducible automated tests. Real implementation requires client-specific sample headers, business rules (refunds, partial payments, multiple currencies, etc.) and agreed acceptance tests. It is not a production financial control or an assurance opinion.

## Repository hygiene
Publish source, README, synthetic inputs, tests and sanitized sample outputs. Exclude vendor/, .venv/, __pycache__/ and credentials. Never describe this self-directed demo as paid client work.
