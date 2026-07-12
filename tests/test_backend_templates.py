from fastapi.testclient import TestClient

from backend.main import app
from tests.backend_test_helpers import XLSX_MEDIA_TYPE

client = TestClient(app)


def test_download_orders_template_returns_real_sample_file():
    response = client.get("/api/templates/orders")

    assert response.status_code == 200
    assert response.headers["content-type"] == XLSX_MEDIA_TYPE
    assert "sample_orders.xlsx" in response.headers["content-disposition"]
    assert len(response.content) > 0


def test_download_each_allowlisted_template_succeeds():
    for name in ("orders", "product-master", "inventory", "invoices"):
        response = client.get(f"/api/templates/{name}")
        assert response.status_code == 200, name


def test_download_unknown_template_returns_400():
    response = client.get("/api/templates/does-not-exist")

    assert response.status_code == 400
    assert response.json()["detail"] == "The requested sample file is not available."


def test_sample_customers_is_not_exposed():
    response = client.get("/api/templates/customers")

    assert response.status_code == 400
