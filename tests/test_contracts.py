from src.contracts import (
    AllocationResultRow,
    BackorderRow,
    PaymentDataIssueRow,
    ValidationErrorRow,
    ValidOrderRow,
)
from tests.contract_fixtures import (
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


def test_validation_error_row_is_plain_dict_without_optional_fields():
    row: ValidationErrorRow = {
        "row_number": 3,
        "error_code": "OV-001",
        "error_message": "Customer name is missing",
        "severity": "Error",
    }

    assert isinstance(row, dict)
    assert "order_id" not in row
    assert "sku" not in row


def test_valid_order_row_accepts_optional_fields():
    row: ValidOrderRow = {
        "order_id": "SO-2026-001",
        "order_date": "2026-07-10",
        "customer_name": "Bright Medical Trading Ltd",
        "customer_region": "Hong Kong",
        "sku": "MED-LENS-001",
        "product_name": "Optical Lens Kit",
        "quantity": 10,
        "requested_delivery_date": "2026-07-15",
        "priority": "High",
        "payment_terms": "30 days",
        "sales_owner": "Jesse",
    }

    assert row["quantity"] == 10


def test_backorder_row_shares_allocation_result_row_shape():
    allocation_row: AllocationResultRow = {
        "order_id": "SO-2026-001",
        "customer_name": "Bright Medical Trading Ltd",
        "sku": "MED-LENS-001",
        "requested_qty": 10,
        "allocated_qty": 0,
        "backorder_qty": 10,
        "warehouse": "HK Warehouse",
        "status": "Backordered",
        "priority": "High",
        "requested_delivery_date": "2026-07-15",
    }
    backorder_row: BackorderRow = dict(allocation_row)

    assert backorder_row == allocation_row


def test_payment_data_issue_row_allows_missing_invoice_id():
    row: PaymentDataIssueRow = {
        "error_code": "PA-006",
        "error_message": "Due date is missing",
        "severity": "Error",
    }

    assert "invoice_id" not in row


def test_validation_summary_fixture_has_all_required_keys():
    assert isinstance(VALIDATION_SUMMARY_FIXTURE, dict)
    assert set(VALIDATION_SUMMARY_FIXTURE.keys()) == {
        "total_orders",
        "valid_orders",
        "invalid_orders",
        "duplicate_orders",
        "invalid_skus",
        "missing_field_count",
    }


def test_validation_error_row_fixture_has_required_keys():
    assert isinstance(VALIDATION_ERROR_ROW_FIXTURE, dict)
    assert {"row_number", "error_code", "error_message", "severity"} <= VALIDATION_ERROR_ROW_FIXTURE.keys()


def test_valid_order_row_fixture_has_required_keys():
    assert isinstance(VALID_ORDER_ROW_FIXTURE, dict)
    required = {
        "order_id",
        "order_date",
        "customer_name",
        "customer_region",
        "sku",
        "quantity",
        "requested_delivery_date",
        "priority",
        "payment_terms",
    }
    assert required <= VALID_ORDER_ROW_FIXTURE.keys()


def test_allocation_summary_fixture_has_all_required_keys():
    assert isinstance(ALLOCATION_SUMMARY_FIXTURE, dict)
    assert set(ALLOCATION_SUMMARY_FIXTURE.keys()) == {
        "total_order_lines",
        "fully_allocated_count",
        "partially_allocated_count",
        "backordered_count",
        "low_stock_sku_count",
    }


def test_allocation_result_row_fixture_has_required_keys():
    assert isinstance(ALLOCATION_RESULT_ROW_FIXTURE, dict)
    required = {
        "order_id",
        "customer_name",
        "sku",
        "requested_qty",
        "allocated_qty",
        "backorder_qty",
        "warehouse",
        "status",
        "priority",
        "requested_delivery_date",
    }
    assert required <= ALLOCATION_RESULT_ROW_FIXTURE.keys()


def test_backorder_row_fixture_has_status_backordered():
    assert isinstance(BACKORDER_ROW_FIXTURE, dict)
    assert BACKORDER_ROW_FIXTURE["status"] == "Backordered"
    assert BACKORDER_ROW_FIXTURE["allocated_qty"] == 0


def test_remaining_inventory_row_fixture_has_required_keys():
    assert isinstance(REMAINING_INVENTORY_ROW_FIXTURE, dict)
    required = {
        "sku",
        "warehouse",
        "starting_available_qty",
        "allocated_qty",
        "remaining_qty",
        "reorder_alert",
    }
    assert required <= REMAINING_INVENTORY_ROW_FIXTURE.keys()


def test_supplier_follow_up_row_fixture_has_required_keys():
    assert isinstance(SUPPLIER_FOLLOW_UP_ROW_FIXTURE, dict)
    required = {"sku", "warehouse", "remaining_qty", "reorder_point"}
    assert required <= SUPPLIER_FOLLOW_UP_ROW_FIXTURE.keys()


def test_payment_aging_summary_fixture_has_all_required_keys():
    assert isinstance(PAYMENT_AGING_SUMMARY_FIXTURE, dict)
    assert set(PAYMENT_AGING_SUMMARY_FIXTURE.keys()) == {
        "total_invoices",
        "total_outstanding_amount",
        "overdue_amount",
        "high_priority_count",
        "aging_bucket_counts",
    }
    assert isinstance(PAYMENT_AGING_SUMMARY_FIXTURE["aging_bucket_counts"], dict)


def test_payment_aging_row_fixture_has_all_required_keys():
    assert isinstance(PAYMENT_AGING_ROW_FIXTURE, dict)
    assert set(PAYMENT_AGING_ROW_FIXTURE.keys()) == {
        "invoice_id",
        "customer_name",
        "invoice_date",
        "due_date",
        "invoice_amount",
        "paid_amount",
        "outstanding_amount",
        "days_overdue",
        "aging_bucket",
        "follow_up_priority",
        "suggested_action",
    }


def test_payment_data_issue_row_fixture_has_required_keys():
    assert isinstance(PAYMENT_DATA_ISSUE_ROW_FIXTURE, dict)
    assert {"error_code", "error_message", "severity"} <= PAYMENT_DATA_ISSUE_ROW_FIXTURE.keys()


def test_draft_message_row_fixture_has_all_required_keys():
    assert isinstance(DRAFT_MESSAGE_ROW_FIXTURE, dict)
    assert set(DRAFT_MESSAGE_ROW_FIXTURE.keys()) == {
        "invoice_id",
        "customer_name",
        "outstanding_amount",
        "days_overdue",
        "message_text",
    }


def test_report_manifest_fixtures_cover_the_three_required_reports():
    assert isinstance(REPORT_MANIFEST_FIXTURES, list)
    report_types = {manifest["report_type"] for manifest in REPORT_MANIFEST_FIXTURES}
    assert report_types == {"order_validation", "inventory_allocation", "payment_aging"}
    for manifest in REPORT_MANIFEST_FIXTURES:
        assert set(manifest.keys()) == {
            "report_id",
            "report_type",
            "file_name",
            "generated_at",
            "sheet_names",
        }
        assert isinstance(manifest["sheet_names"], list)


def test_report_manifest_fixture_ids_match_exporter_format():
    for manifest in REPORT_MANIFEST_FIXTURES:
        timestamp = (
            manifest["generated_at"]
            .replace("-", "")
            .replace(":", "")
            .replace("T", "")
        )
        assert manifest["report_id"] == f"rpt-{manifest['report_type']}-{timestamp}"
