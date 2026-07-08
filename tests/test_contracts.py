from src.contracts import (
    AllocationResultRow,
    BackorderRow,
    PaymentDataIssueRow,
    ValidationErrorRow,
    ValidOrderRow,
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
