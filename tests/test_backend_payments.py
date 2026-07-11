import io

from fastapi.testclient import TestClient

from backend.main import app
from tests.backend_test_helpers import SAMPLE_DATA_DIR, XLSX_MEDIA_TYPE, upload_file

client = TestClient(app)


def test_calculate_payment_aging_happy_path():
    with (SAMPLE_DATA_DIR / "sample_invoices.xlsx").open("rb") as invoices:
        response = client.post(
            "/api/payments/aging",
            files={"invoices_file": upload_file("sample_invoices.xlsx", invoices)},
            data={"as_of_date": "2026-07-10"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["total_invoices"] == 27
    assert len(body["aging_rows"]) > 0


def test_calculate_payment_aging_report_returns_xlsx_with_headers():
    with (SAMPLE_DATA_DIR / "sample_invoices.xlsx").open("rb") as invoices:
        response = client.post(
            "/api/payments/aging/report",
            files={"invoices_file": upload_file("sample_invoices.xlsx", invoices)},
            data={"as_of_date": "2026-07-10"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == XLSX_MEDIA_TYPE
    assert "payment_aging_report.xlsx" in response.headers["content-disposition"]
    assert response.headers["x-report-id"].startswith("rpt-payment_aging-")


def test_calculate_payment_aging_different_as_of_dates_change_buckets():
    with (SAMPLE_DATA_DIR / "sample_invoices.xlsx").open("rb") as invoices:
        early = client.post(
            "/api/payments/aging",
            files={"invoices_file": upload_file("sample_invoices.xlsx", invoices)},
            data={"as_of_date": "2026-01-01"},
        )
    with (SAMPLE_DATA_DIR / "sample_invoices.xlsx").open("rb") as invoices:
        later = client.post(
            "/api/payments/aging",
            files={"invoices_file": upload_file("sample_invoices.xlsx", invoices)},
            data={"as_of_date": "2027-01-01"},
        )

    assert early.status_code == 200
    assert later.status_code == 200
    assert early.json()["summary"]["aging_bucket_counts"] != later.json()["summary"]["aging_bucket_counts"]


def test_calculate_payment_aging_missing_as_of_date_returns_400():
    with (SAMPLE_DATA_DIR / "sample_invoices.xlsx").open("rb") as invoices:
        response = client.post(
            "/api/payments/aging",
            files={"invoices_file": upload_file("sample_invoices.xlsx", invoices)},
        )

    assert response.status_code == 400
    assert isinstance(response.json()["detail"], str)


def test_calculate_payment_aging_malformed_as_of_date_returns_400():
    with (SAMPLE_DATA_DIR / "sample_invoices.xlsx").open("rb") as invoices:
        response = client.post(
            "/api/payments/aging",
            files={"invoices_file": upload_file("sample_invoices.xlsx", invoices)},
            data={"as_of_date": "not-a-date"},
        )

    assert response.status_code == 400
    assert "as-of date" in response.json()["detail"]


def test_calculate_payment_aging_wrong_extension_returns_400():
    bad_file = io.BytesIO(b"not an excel file")
    response = client.post(
        "/api/payments/aging",
        files={"invoices_file": ("invoices.csv", bad_file, "text/csv")},
        data={"as_of_date": "2026-07-10"},
    )

    assert response.status_code == 400
    assert "invoices file" in response.json()["detail"]
