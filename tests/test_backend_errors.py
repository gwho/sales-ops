"""Exercises backend/errors.py's two handlers directly: FastAPI's own list-shaped
validation errors get normalized to a single string, and unexpected exceptions
never leak their message/traceback to the client.
"""

from fastapi.testclient import TestClient

from backend.main import app
from tests.backend_test_helpers import SAMPLE_DATA_DIR, upload_file

client = TestClient(app)


def test_completely_missing_multipart_body_returns_normalized_string_detail():
    response = client.post("/api/orders/validate")

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "upload the required files" in detail


def test_unexpected_exception_returns_generic_500_without_leaking_message(monkeypatch):
    def _boom(*args, **kwargs):
        raise RuntimeError("super secret internal stack trace detail")

    monkeypatch.setattr("backend.routers.orders.validate_orders", _boom)

    # raise_server_exceptions=False: exercise the registered Exception handler's
    # actual response instead of TestClient's default debugging behavior of
    # re-raising unhandled exceptions straight into the test.
    error_client = TestClient(app, raise_server_exceptions=False)

    with (
        (SAMPLE_DATA_DIR / "sample_orders.xlsx").open("rb") as orders,
        (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master,
    ):
        response = error_client.post(
            "/api/orders/validate",
            files={
                "orders_file": upload_file("sample_orders.xlsx", orders),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
            },
        )

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert "super secret internal stack trace detail" not in detail
    assert detail == "Something went wrong processing this request. Please try again."
