import io

import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app
from tests.backend_test_helpers import SAMPLE_DATA_DIR, XLSX_MEDIA_TYPE, upload_file

client = TestClient(app)


def test_validate_orders_happy_path_matches_real_pipeline():
    with (
        (SAMPLE_DATA_DIR / "sample_orders.xlsx").open("rb") as orders,
        (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master,
    ):
        response = client.post(
            "/api/orders/validate",
            files={
                "orders_file": upload_file("sample_orders.xlsx", orders),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["total_orders"] == 36
    assert body["summary"]["valid_orders"] == 28
    assert len(body["valid_orders"]) == 28
    assert len(body["errors"]) > 0


def test_validate_orders_report_returns_xlsx_with_headers():
    with (
        (SAMPLE_DATA_DIR / "sample_orders.xlsx").open("rb") as orders,
        (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master,
    ):
        response = client.post(
            "/api/orders/validate/report",
            files={
                "orders_file": upload_file("sample_orders.xlsx", orders),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == XLSX_MEDIA_TYPE
    assert "order_validation_report.xlsx" in response.headers["content-disposition"]
    assert response.headers["x-report-id"].startswith("rpt-order_validation-")
    assert len(response.content) > 0


def test_validate_orders_missing_file_returns_400():
    with (SAMPLE_DATA_DIR / "sample_orders.xlsx").open("rb") as orders:
        response = client.post(
            "/api/orders/validate",
            files={"orders_file": upload_file("sample_orders.xlsx", orders)},
        )

    assert response.status_code == 400
    assert isinstance(response.json()["detail"], str)


def test_validate_orders_wrong_extension_returns_business_readable_400():
    bad_file = io.BytesIO(b"not an excel file")
    with (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master:
        response = client.post(
            "/api/orders/validate",
            files={
                "orders_file": ("orders.csv", bad_file, "text/csv"),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
            },
        )

    assert response.status_code == 400
    assert "orders file" in response.json()["detail"]
    assert ".xlsx" in response.json()["detail"]


def test_validate_orders_corrupt_xlsx_returns_400_not_500():
    corrupt_file = io.BytesIO(b"this is not a real xlsx workbook")
    with (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master:
        response = client.post(
            "/api/orders/validate",
            files={
                "orders_file": ("orders.xlsx", corrupt_file, XLSX_MEDIA_TYPE),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
            },
        )

    assert response.status_code == 400
    assert "could not be read as a valid .xlsx workbook" in response.json()["detail"]


def test_validate_orders_missing_required_columns_returns_400_with_column_names():
    incomplete_orders = pd.DataFrame({"order_id": ["SO-1"], "sku": ["ABC"]})
    buffer = io.BytesIO()
    incomplete_orders.to_excel(buffer, index=False)
    buffer.seek(0)

    with (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master:
        response = client.post(
            "/api/orders/validate",
            files={
                "orders_file": ("orders.xlsx", buffer, XLSX_MEDIA_TYPE),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
            },
        )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "missing required columns" in detail
    assert "order_date" in detail
