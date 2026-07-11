import io

import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app
from tests.backend_test_helpers import SAMPLE_DATA_DIR, XLSX_MEDIA_TYPE, upload_file

client = TestClient(app)


def _all_invalid_orders_xlsx() -> io.BytesIO:
    """One order row with a blank customer_name -- OV-001 fails it, so
    validate_orders() produces zero valid_orders and allocate_inventory()
    receives an empty (columnless) DataFrame."""
    orders_df = pd.DataFrame(
        [
            {
                "order_id": "SO-BAD-001",
                "order_date": "2026-01-01",
                "customer_name": "",
                "customer_region": "HK",
                "sku": "PART-BULB-013",
                "quantity": 1,
                "requested_delivery_date": "2026-01-10",
                "priority": "Normal",
                "payment_terms": "30 days",
            }
        ]
    )
    buffer = io.BytesIO()
    orders_df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


def _post(path: str):
    with (
        (SAMPLE_DATA_DIR / "sample_orders.xlsx").open("rb") as orders,
        (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master,
        (SAMPLE_DATA_DIR / "sample_inventory.xlsx").open("rb") as inventory,
    ):
        return client.post(
            path,
            files={
                "orders_file": upload_file("sample_orders.xlsx", orders),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
                "inventory_file": upload_file("sample_inventory.xlsx", inventory),
            },
        )


def test_allocate_inventory_happy_path_runs_full_chain():
    response = _post("/api/inventory/allocate")

    assert response.status_code == 200
    body = response.json()
    # 28 valid order lines from the real validate_orders -> allocate_inventory chain.
    assert body["summary"]["total_order_lines"] == 28
    assert len(body["allocation_results"]) == 28


def test_allocate_inventory_report_returns_xlsx_with_headers():
    response = _post("/api/inventory/allocate/report")

    assert response.status_code == 200
    assert response.headers["content-type"] == XLSX_MEDIA_TYPE
    assert "inventory_allocation_report.xlsx" in response.headers["content-disposition"]
    assert response.headers["x-report-id"].startswith("rpt-inventory_allocation-")
    assert len(response.content) > 0


def test_allocate_inventory_missing_inventory_file_returns_400():
    with (
        (SAMPLE_DATA_DIR / "sample_orders.xlsx").open("rb") as orders,
        (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master,
    ):
        response = client.post(
            "/api/inventory/allocate",
            files={
                "orders_file": upload_file("sample_orders.xlsx", orders),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
            },
        )

    assert response.status_code == 400
    assert isinstance(response.json()["detail"], str)


def test_allocate_inventory_zero_valid_orders_returns_400_not_500():
    bad_orders = _all_invalid_orders_xlsx()
    with (
        (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master,
        (SAMPLE_DATA_DIR / "sample_inventory.xlsx").open("rb") as inventory,
    ):
        response = client.post(
            "/api/inventory/allocate",
            files={
                "orders_file": ("orders.xlsx", bad_orders, XLSX_MEDIA_TYPE),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
                "inventory_file": upload_file("sample_inventory.xlsx", inventory),
            },
        )

    assert response.status_code == 400
    assert isinstance(response.json()["detail"], str)


def test_allocate_inventory_report_zero_valid_orders_returns_400_not_500():
    bad_orders = _all_invalid_orders_xlsx()
    with (
        (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master,
        (SAMPLE_DATA_DIR / "sample_inventory.xlsx").open("rb") as inventory,
    ):
        response = client.post(
            "/api/inventory/allocate/report",
            files={
                "orders_file": ("orders.xlsx", bad_orders, XLSX_MEDIA_TYPE),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
                "inventory_file": upload_file("sample_inventory.xlsx", inventory),
            },
        )

    assert response.status_code == 400
    assert isinstance(response.json()["detail"], str)


def test_allocate_inventory_wrong_extension_returns_400():
    bad_file = io.BytesIO(b"not an excel file")
    with (
        (SAMPLE_DATA_DIR / "sample_orders.xlsx").open("rb") as orders,
        (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master,
    ):
        response = client.post(
            "/api/inventory/allocate",
            files={
                "orders_file": upload_file("sample_orders.xlsx", orders),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
                "inventory_file": ("inventory.txt", bad_file, "text/plain"),
            },
        )

    assert response.status_code == 400
    assert "inventory file" in response.json()["detail"]
