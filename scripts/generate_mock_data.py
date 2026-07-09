"""Generate Phase 8 mock JSON for the Next.js UI from the Python contract fixtures.

BUILD-TIME ONLY. This script is the single sanctioned place where the frontend's
mock data is derived from `tests/contract_fixtures.py`. The Next.js app itself
must never import from `tests/` at runtime — it reads the committed JSON emitted
here into `lib/mock-data/`.

Run from the repo root:

    uv run python scripts/generate_mock_data.py

Re-run whenever the contract fixtures change so the mock JSON stays in sync with
`src/contracts.py` (and, transitively, `types/index.ts`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.contract_fixtures import (  # noqa: E402  (path setup must precede import)
    ALLOCATION_RESULT_ROW_FIXTURE,
    ALLOCATION_SUMMARY_FIXTURE,
    BACKORDER_ROW_FIXTURE,
    DRAFT_MESSAGE_ROW_FIXTURE,
    PAYMENT_AGING_ROW_FIXTURE,
    PAYMENT_AGING_SUMMARY_FIXTURE,
    PAYMENT_DATA_ISSUE_ROW_FIXTURE,
    REMAINING_INVENTORY_ROW_FIXTURE,
    REPORT_MANIFEST_FIXTURES,
    SUPPLIER_FOLLOW_UP_ROW_FIXTURE,
    VALID_ORDER_ROW_FIXTURE,
    VALIDATION_ERROR_ROW_FIXTURE,
    VALIDATION_SUMMARY_FIXTURE,
)

OUT_DIR = ROOT / "lib" / "mock-data"


def build_payloads() -> dict[str, object]:
    """Assemble the three result envelopes + the report manifest list.

    Each envelope mirrors the local *Result types in types/index.ts, which in
    turn mirror the business-module return shapes. The fixtures are single-row
    examples, so these envelopes are intentionally small — enough to prove the
    shape end to end, not a full demo dataset.
    """
    order_validation = {
        "summary": VALIDATION_SUMMARY_FIXTURE,
        "valid_orders": [VALID_ORDER_ROW_FIXTURE],
        "errors": [VALIDATION_ERROR_ROW_FIXTURE],
    }

    inventory_allocation = {
        "summary": ALLOCATION_SUMMARY_FIXTURE,
        "allocation_results": [ALLOCATION_RESULT_ROW_FIXTURE, BACKORDER_ROW_FIXTURE],
        "backorders": [BACKORDER_ROW_FIXTURE],
        "remaining_inventory": [REMAINING_INVENTORY_ROW_FIXTURE],
        "supplier_follow_ups": [SUPPLIER_FOLLOW_UP_ROW_FIXTURE],
    }

    payment_aging = {
        "summary": PAYMENT_AGING_SUMMARY_FIXTURE,
        "aging_rows": [PAYMENT_AGING_ROW_FIXTURE],
        "data_issues": [PAYMENT_DATA_ISSUE_ROW_FIXTURE],
        "draft_messages": [DRAFT_MESSAGE_ROW_FIXTURE],
    }

    return {
        "order-validation": order_validation,
        "inventory-allocation": inventory_allocation,
        "payment-aging": payment_aging,
        "reports": REPORT_MANIFEST_FIXTURES,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, payload in build_payloads().items():
        path = OUT_DIR / f"{name}.json"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
