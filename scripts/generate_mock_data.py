"""Generate the Next.js UI's mock JSON from the committed sample Excel data.

BUILD-TIME ONLY, MANUAL. This is the single sanctioned place where the frontend's
mock data is produced. The Next.js app itself must never import from `sample_data/`
or `src/` at runtime — it reads the committed JSON emitted here into `lib/mock-data/`.

This script loads `sample_data/*.xlsx` through each business module's own `load_*`
helper and runs the real `validate_orders` -> `allocate_inventory` ->
`calculate_payment_aging` -> `report_export` pipeline, the same code path a real
upload would exercise. Because of that, a failure here is a genuine compatibility
signal, not just a data-generation bug: it means the committed sample Excel files
no longer match what the Python loaders/business modules expect (e.g. a required
column was renamed, or `src/sample_data.py` was regenerated with a shape those
modules can no longer parse). Treat a failure here as you would a failing
`tests/test_sample_data.py` compatibility assertion, not as noise to route around.

`tests/contract_fixtures.py` is unrelated to this script — it stays a small,
single-row, contract-shape source used only by `tests/test_contracts.py` and
`tests/test_report_export.py`.

`sample_data/sample_customers.xlsx` is intentionally never read here — it is
optional/reference-only and no Python business module consumes it (see
`sample_data/README_sample_data.md`).

Run from the repo root:

    uv run python scripts/generate_mock_data.py

or:

    npm run mock-data

Re-run whenever `sample_data/*.xlsx` changes so the mock JSON stays in sync. Never
hand-edit `lib/mock-data/*.json` directly.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.inventory_allocation import allocate_inventory, load_inventory  # noqa: E402
from src.order_validation import load_orders, load_product_master, validate_orders  # noqa: E402
from src.payment_aging import calculate_payment_aging, load_invoices  # noqa: E402
from src.report_export import (  # noqa: E402
    export_inventory_allocation_report,
    export_order_validation_report,
    export_payment_aging_report,
)

SAMPLE_DATA_DIR = ROOT / "sample_data"
OUT_DIR = ROOT / "lib" / "mock-data"

# Fixed so the committed JSON (aging buckets/priorities, report_id/generated_at) is
# deterministic across re-runs. Must match sample_data/README_sample_data.md's
# stated "Generated on" date — update both together if the sample data's own
# reference_date ever moves.
MOCK_AS_OF_DATE = date(2026, 7, 10)
MOCK_GENERATED_AT = datetime(2026, 7, 10, 9, 0, 0)


def build_payloads() -> dict[str, object]:
    """Run the real business-rule pipeline against sample_data/*.xlsx and assemble
    the three result envelopes plus the reports manifest list.

    Each envelope mirrors the local *Result types in types/index.ts, which in turn
    mirror the business-module return shapes. Row counts now reflect the real
    sample dataset, not single-row stand-ins.
    """
    product_master_df = load_product_master(SAMPLE_DATA_DIR / "sample_product_master.xlsx")
    orders_df = load_orders(SAMPLE_DATA_DIR / "sample_orders.xlsx")
    inventory_df = load_inventory(SAMPLE_DATA_DIR / "sample_inventory.xlsx")
    invoices_df = load_invoices(SAMPLE_DATA_DIR / "sample_invoices.xlsx")

    order_validation = validate_orders(orders_df, product_master_df)

    valid_orders_df = pd.DataFrame(order_validation["valid_orders"])
    inventory_allocation = allocate_inventory(valid_orders_df, inventory_df)

    payment_aging = calculate_payment_aging(invoices_df, as_of_date=MOCK_AS_OF_DATE)

    _, order_validation_manifest = export_order_validation_report(
        order_validation, original_orders_df=orders_df, generated_at=MOCK_GENERATED_AT
    )
    _, inventory_allocation_manifest = export_inventory_allocation_report(
        inventory_allocation, generated_at=MOCK_GENERATED_AT
    )
    _, payment_aging_manifest = export_payment_aging_report(
        payment_aging, generated_at=MOCK_GENERATED_AT
    )

    return {
        "order-validation": order_validation,
        "inventory-allocation": inventory_allocation,
        "payment-aging": payment_aging,
        "reports": [order_validation_manifest, inventory_allocation_manifest, payment_aging_manifest],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, payload in build_payloads().items():
        path = OUT_DIR / f"{name}.json"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)
            fh.write("\n")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
