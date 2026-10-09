"""Reconcile synthetic order and settlement exports with auditable exceptions.

Independent demonstration project; no client or employer data.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    # Keep locally installed dependencies on D: during isolated development.
    sys.path.insert(0, str(Path(__file__).parent / "vendor"))
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment


ORDER_FIELDS = {"order_id", "customer", "expected_amount", "status"}
PAYMENT_FIELDS = {"order_id", "received_amount", "reference"}
RESULT_FIELDS = ["order_id", "customer", "expected_amount", "received_amount",
                 "difference", "status", "reason"]
ERROR_FIELDS = ["dataset", "source_row", "order_id", "reason"]
CATEGORIES = ("matched", "amount_mismatch", "missing_payment", "orphan_payment",
              "duplicate_order", "duplicate_payment", "pending_excluded",
              "unexpected_pending_payment")


def currency(raw: str) -> Decimal:
    """Parse positive currency as cents exactly; reject unrecognized inputs."""
    text = str(raw or "").strip().replace(",", "").replace("$", "")
    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError("invalid currency amount") from exc
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise ValueError("amount must be a nonnegative value with at most two decimals")
    return amount.quantize(Decimal("0.01"))


def money(value: Decimal | None) -> str:
    return "" if value is None else f"{value:.2f}"


def input_rows(path: Path, expected: set[str]):
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = set(reader.fieldnames or [])
        missing = expected - headers
        if missing:
            raise ValueError(f"{path.name}: missing required columns: {', '.join(sorted(missing))}")
        for n, row in enumerate(reader, start=2):
            yield n, row


def parse(path: Path, kind: str):
    records = defaultdict(list)
    rejects = []
    fields = ORDER_FIELDS if kind == "orders" else PAYMENT_FIELDS
    for row_n, row in input_rows(path, fields):
        oid = (row.get("order_id") or "").strip().upper()
        try:
            if not oid:
                raise ValueError("missing order ID")
            key = "expected_amount" if kind == "orders" else "received_amount"
            amount = currency(row.get(key, ""))
            if kind == "orders":
                status = (row.get("status") or "").strip().lower()
                if status not in {"completed", "pending"}:
                    raise ValueError("status must be completed or pending")
                record = {"id": oid, "customer": (row.get("customer") or "").strip(),
                          "amount": amount, "status": status}
            else:
                record = {"id": oid, "amount": amount,
                          "reference": (row.get("reference") or "").strip()}
            records[oid].append(record)
        except ValueError as exc:
            rejects.append({"dataset": kind, "source_row": row_n,
                            "order_id": oid, "reason": str(exc)})
    return records, rejects


def reconcile(orders_path: Path, payments_path: Path):
    orders, order_rejects = parse(orders_path, "orders")
    payments, payment_rejects = parse(payments_path, "payments")
    output = []
    counts = {name: 0 for name in CATEGORIES}
    for oid in sorted(orders.keys() | payments.keys()):
        obs = orders.get(oid, [])
        pays = payments.get(oid, [])
        order = obs[0] if obs else None
        customer = order["customer"] if order else ""
        expected = order["amount"] if order else None
        received = pays[0]["amount"] if len(pays) == 1 else None
        difference = received - expected if expected is not None and received is not None else None

        if len(obs) > 1:
            status, reason = "duplicate_order", f"{len(obs)} valid order records with same ID"
        elif len(pays) > 1:
            status, reason = "duplicate_payment", f"{len(pays)} valid payment records with same ID"
        elif order is None:
            status, reason = "orphan_payment", "payment ID not present in valid orders"
        elif order["status"] == "pending" and pays:
            status, reason = "unexpected_pending_payment", "payment against pending order"
        elif order["status"] == "pending":
            status, reason = "pending_excluded", "pending order not due for settlement"
        elif not pays:
            status, reason = "missing_payment", "completed order has no payment"
        elif expected != received:
            status, reason = "amount_mismatch", "received and expected amounts differ"
        else:
            status, reason = "matched", "settlement amount matches order"

        counts[status] += 1
        output.append({"order_id": oid, "customer": customer,
                       "expected_amount": money(expected),
                       "received_amount": money(received), "difference": money(difference),
                       "status": status, "reason": reason})
    return output, order_rejects + payment_rejects, counts


def spreadsheet_safe_text(value):
    """Prevent text fields beginning with spreadsheet formula markers becoming formulas."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def write_csv(path: Path, columns: list[str], data: list[dict]):
    text_cols = {"order_id", "customer", "reason"}
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for record in data:
            w.writerow({k: spreadsheet_safe_text(record.get(k, "")) if k in text_cols
                        else record.get(k, "") for k in columns})


def make_workbook(path: Path, rows: list[dict], rejects: list[dict], counts: dict):
    wb = Workbook()
    overview = wb.active
    overview.title = "Overview"
    overview.append(["Reconciliation outcome", "Count"])
    for key, value in counts.items():
        overview.append([key.replace("_", " ").title(), value])
    overview.append(["Rejected input rows", len(rejects)])
    overview.append(["Unique IDs inspected", len(rows)])

    def tab(title: str, fields: list[str], entries: list[dict]):
        ws = wb.create_sheet(title)
        ws.append(fields)
        for entry in entries:
            ws.append([spreadsheet_safe_text(entry.get(f, "")) if f in {"order_id", "customer", "reason"} else entry.get(f, "") for f in fields])
        return ws

    tab("Matches", RESULT_FIELDS, [r for r in rows if r["status"] == "matched"])
    tab("Exceptions", RESULT_FIELDS,
        [r for r in rows if r["status"] not in {"matched", "pending_excluded"}])
    tab("Pending", RESULT_FIELDS, [r for r in rows if r["status"] == "pending_excluded"])
    tab("Rejected Rows", ERROR_FIELDS, rejects)

    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="183247")
            cell.alignment = Alignment(vertical="center")
        ws.row_dimensions[1].height = 23
        for col in ws.columns:
            letter = col[0].column_letter
            width = max(len(str(c.value or "")) for c in col) + 3
            ws.column_dimensions[letter].width = min(max(14, width), 62)
    wb.save(path)


def run(orders_path: Path, payments_path: Path, out_dir: Path):
    rows, rejects, counts = reconcile(orders_path, payments_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "matched.csv", RESULT_FIELDS,
              [r for r in rows if r["status"] == "matched"])
    write_csv(out_dir / "exceptions.csv", RESULT_FIELDS,
              [r for r in rows if r["status"] not in {"matched", "pending_excluded"}])
    write_csv(out_dir / "rejected_rows.csv", ERROR_FIELDS, rejects)
    summary = {"counts": counts, "rejected_input_rows": len(rejects),
               "unique_order_ids_inspected": len(rows)}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    make_workbook(out_dir / "reconciliation.xlsx", rows, rejects, counts)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Order-payment reconciliation demo")
    parser.add_argument("--orders", type=Path, required=True)
    parser.add_argument("--payments", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        summary = run(args.orders, args.payments, args.out)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Input error: {exc}\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
