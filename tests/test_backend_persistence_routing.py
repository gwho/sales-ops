"""Route-orchestration tests for Phase 12 persistence.

Mocks the repository layer via app.dependency_overrides (never touches real
Postgres) and verifies control flow only: X-Persisted header values, 400 on
malformed X-Session-Id, and that a raising repository call still returns 200
with the full workflow result. See
docs/adr/0007-session-scoped-workflow-result-persistence.md.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.repositories.workflow_results import get_workflow_results_repository
from tests.backend_test_helpers import SAMPLE_DATA_DIR, upload_file

client = TestClient(app)

VALID_SESSION_ID = str(uuid.uuid4())
MALFORMED_SESSION_ID = "not-a-uuid"


class FakeRepository:
    """Configurable stand-in for WorkflowResultsRepository."""

    def __init__(self, save_result: bool = True, save_raises: bool = False, get_result=None):
        self._save_result = save_result
        self._save_raises = save_raises
        self._get_result = (
            get_result
            if get_result is not None
            else {"order_validation": None, "inventory_allocation": None, "payment_aging": None}
        )
        self.save_calls: list[tuple[uuid.UUID, str]] = []

    def save(self, session_id, workflow_type, result, schema_version):
        self.save_calls.append((session_id, workflow_type))
        if self._save_raises:
            raise RuntimeError("simulated repository failure")
        return self._save_result

    def get_latest(self, session_id):
        return self._get_result


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def _override_repo(fake: FakeRepository) -> None:
    app.dependency_overrides[get_workflow_results_repository] = lambda: fake


def _order_validation_files():
    return {
        "orders_file": upload_file("sample_orders.xlsx", (SAMPLE_DATA_DIR / "sample_orders.xlsx").open("rb")),
        "product_master_file": upload_file(
            "sample_product_master.xlsx",
            (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb"),
        ),
    }


def _inventory_allocation_files():
    files = _order_validation_files()
    files["inventory_file"] = upload_file(
        "sample_inventory.xlsx", (SAMPLE_DATA_DIR / "sample_inventory.xlsx").open("rb")
    )
    return files


# --- POST /api/orders/validate -----------------------------------------------


def test_validate_orders_no_session_id_returns_skipped_and_200():
    fake = FakeRepository()
    _override_repo(fake)

    response = client.post("/api/orders/validate", files=_order_validation_files())

    assert response.status_code == 200
    assert response.headers["x-persisted"] == "skipped"
    assert fake.save_calls == []


def test_validate_orders_malformed_session_id_returns_400_before_processing():
    fake = FakeRepository()
    _override_repo(fake)

    response = client.post(
        "/api/orders/validate",
        files=_order_validation_files(),
        headers={"X-Session-Id": MALFORMED_SESSION_ID},
    )

    assert response.status_code == 400
    assert "X-Session-Id" in response.json()["detail"]
    assert fake.save_calls == []


def test_validate_orders_valid_session_id_save_succeeds_returns_true():
    fake = FakeRepository(save_result=True)
    _override_repo(fake)

    response = client.post(
        "/api/orders/validate",
        files=_order_validation_files(),
        headers={"X-Session-Id": VALID_SESSION_ID},
    )

    assert response.status_code == 200
    assert response.headers["x-persisted"] == "true"
    assert fake.save_calls == [(uuid.UUID(VALID_SESSION_ID), "order_validation")]


def test_validate_orders_save_fails_still_returns_200_with_full_result():
    fake = FakeRepository(save_result=False)
    _override_repo(fake)

    response = client.post(
        "/api/orders/validate",
        files=_order_validation_files(),
        headers={"X-Session-Id": VALID_SESSION_ID},
    )

    assert response.status_code == 200
    assert response.headers["x-persisted"] == "false"
    assert response.json()["summary"]["total_orders"] == 36


def test_validate_orders_repository_raises_still_returns_200_with_false():
    fake = FakeRepository(save_raises=True)
    _override_repo(fake)

    response = client.post(
        "/api/orders/validate",
        files=_order_validation_files(),
        headers={"X-Session-Id": VALID_SESSION_ID},
    )

    assert response.status_code == 200
    assert response.headers["x-persisted"] == "false"
    assert response.json()["summary"]["total_orders"] == 36


# --- POST /api/inventory/allocate --------------------------------------------


def test_allocate_inventory_persists_only_inventory_allocation():
    fake = FakeRepository(save_result=True)
    _override_repo(fake)

    response = client.post(
        "/api/inventory/allocate",
        files=_inventory_allocation_files(),
        headers={"X-Session-Id": VALID_SESSION_ID},
    )

    assert response.status_code == 200
    assert response.headers["x-persisted"] == "true"
    # Exactly one save call, for inventory_allocation -- never order_validation,
    # even though the endpoint runs validate_orders() internally as a
    # dependency of allocation (ADR 0007's "Write path" section).
    assert fake.save_calls == [(uuid.UUID(VALID_SESSION_ID), "inventory_allocation")]


def test_allocate_inventory_no_session_id_returns_skipped():
    fake = FakeRepository()
    _override_repo(fake)

    response = client.post("/api/inventory/allocate", files=_inventory_allocation_files())

    assert response.status_code == 200
    assert response.headers["x-persisted"] == "skipped"


def test_allocate_inventory_malformed_session_id_returns_400():
    fake = FakeRepository()
    _override_repo(fake)

    response = client.post(
        "/api/inventory/allocate",
        files=_inventory_allocation_files(),
        headers={"X-Session-Id": MALFORMED_SESSION_ID},
    )

    assert response.status_code == 400
    assert fake.save_calls == []


# --- POST /api/payments/aging ------------------------------------------------


def test_calculate_payment_aging_valid_session_id_returns_true():
    fake = FakeRepository(save_result=True)
    _override_repo(fake)

    with (SAMPLE_DATA_DIR / "sample_invoices.xlsx").open("rb") as invoices:
        response = client.post(
            "/api/payments/aging",
            files={"invoices_file": upload_file("sample_invoices.xlsx", invoices)},
            data={"as_of_date": "2026-07-10"},
            headers={"X-Session-Id": VALID_SESSION_ID},
        )

    assert response.status_code == 200
    assert response.headers["x-persisted"] == "true"
    assert fake.save_calls == [(uuid.UUID(VALID_SESSION_ID), "payment_aging")]


def test_calculate_payment_aging_malformed_session_id_returns_400():
    fake = FakeRepository()
    _override_repo(fake)

    with (SAMPLE_DATA_DIR / "sample_invoices.xlsx").open("rb") as invoices:
        response = client.post(
            "/api/payments/aging",
            files={"invoices_file": upload_file("sample_invoices.xlsx", invoices)},
            data={"as_of_date": "2026-07-10"},
            headers={"X-Session-Id": MALFORMED_SESSION_ID},
        )

    assert response.status_code == 400
    assert fake.save_calls == []


# --- Report endpoints never persist -------------------------------------------


def test_validate_orders_report_endpoint_never_sets_x_persisted():
    fake = FakeRepository()
    _override_repo(fake)

    response = client.post(
        "/api/orders/validate/report",
        files=_order_validation_files(),
        headers={"X-Session-Id": VALID_SESSION_ID},
    )

    assert response.status_code == 200
    assert "x-persisted" not in response.headers
    assert fake.save_calls == []


# --- GET /api/dashboard -------------------------------------------------------


def test_get_dashboard_no_session_id_returns_all_null_without_querying_repo():
    fake = FakeRepository(get_result={"order_validation": {"unexpected": True}} )
    _override_repo(fake)

    response = client.get("/api/dashboard")

    assert response.status_code == 200
    assert response.json() == {
        "order_validation": None,
        "inventory_allocation": None,
        "payment_aging": None,
    }


def test_get_dashboard_malformed_session_id_returns_400():
    fake = FakeRepository()
    _override_repo(fake)

    response = client.get("/api/dashboard", headers={"X-Session-Id": MALFORMED_SESSION_ID})

    assert response.status_code == 400


def test_get_dashboard_valid_session_id_returns_repo_envelope():
    envelope = {
        "order_validation": {"summary": {"total_orders": 5}},
        "inventory_allocation": None,
        "payment_aging": None,
    }
    fake = FakeRepository(get_result=envelope)
    _override_repo(fake)

    response = client.get("/api/dashboard", headers={"X-Session-Id": VALID_SESSION_ID})

    assert response.status_code == 200
    assert response.json() == envelope


def test_get_dashboard_repo_unavailable_returns_503():
    fake = FakeRepository(get_result="unavailable")
    _override_repo(fake)

    response = client.get("/api/dashboard", headers={"X-Session-Id": VALID_SESSION_ID})

    assert response.status_code == 503
    assert isinstance(response.json()["detail"], str)
