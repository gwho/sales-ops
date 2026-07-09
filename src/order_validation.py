"""Order validation rules and validation output (Phase 3 — sales_admin_automation_toolkit_specs/01_demo_order_validation.md)."""

from __future__ import annotations

from typing import TypedDict

import pandas as pd

from src.contracts import ValidationErrorRow, ValidationSummary, ValidOrderRow
from src.excel_io import load_excel, validate_required_columns

ORDERS_REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_name",
    "customer_region",
    "sku",
    "quantity",
    "requested_delivery_date",
    "priority",
    "payment_terms",
]

PRODUCT_MASTER_REQUIRED_COLUMNS = ["sku", "product_name", "active"]

# OV-001 required fields in fixed column order. payment_terms is intentionally
# excluded — a blank payment_terms is exclusively an OV-007 Warning, not an
# OV-001 Error (the spec's own required-fields list and its OV-007 rule
# conflict on this field; resolved in favor of OV-007 so "Warning never
# disqualifies a row" stays internally consistent).
OV001_REQUIRED_FIELDS = [
    ("order_id", "Order ID"),
    ("order_date", "Order date"),
    ("customer_name", "Customer name"),
    ("customer_region", "Customer region"),
    ("sku", "SKU"),
    ("quantity", "Quantity"),
    ("requested_delivery_date", "Requested delivery date"),
    ("priority", "Priority"),
]

VALID_PRIORITIES = {"High", "Normal", "Low"}

_ACTIVE_TRUE_STRINGS = {"true", "yes", "y", "1"}
_ACTIVE_FALSE_STRINGS = {"false", "no", "n", "0"}

# Fixed rule ordering used to sort the final error list deterministically.
_RULE_ORDER = {
    "OV-001": 0,
    "OV-002": 1,
    "OV-003-UNKNOWN_SKU": 2,
    "OV-003-INACTIVE_SKU": 2,
    "OV-003-INVALID_ACTIVE_FLAG": 2,
    "OV-004": 3,
    "OV-005-INVALID_ORDER_DATE": 4,
    "OV-005-INVALID_DELIVERY_DATE": 4,
    "OV-005-DELIVERY_BEFORE_ORDER": 4,
    "OV-006": 5,
    "OV-007": 6,
}

_OV001_FIELD_ORDER = {field: index for index, (field, _label) in enumerate(OV001_REQUIRED_FIELDS)}


class OrderValidationResult(TypedDict):
    summary: ValidationSummary
    valid_orders: list[ValidOrderRow]
    errors: list[ValidationErrorRow]


def load_orders(file) -> pd.DataFrame:
    """Load orders.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, ORDERS_REQUIRED_COLUMNS, "orders file")
    return df


def load_product_master(file) -> pd.DataFrame:
    """Load product_master.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, PRODUCT_MASTER_REQUIRED_COLUMNS, "product master file")
    return df


def _is_blank(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _to_trimmed_str(value: object) -> str:
    return str(value).strip()


def _parse_date(value: object) -> pd.Timestamp | None:
    """Return a normalized Timestamp, or None if value cannot be parsed as a date."""
    if isinstance(value, pd.Timestamp):
        return value
    try:
        parsed = pd.to_datetime(value)
    except (ValueError, TypeError):
        return None
    if pd.isna(parsed):
        return None
    return parsed


def _parse_quantity(value: object) -> tuple[int | None, str | None]:
    """Return (quantity, error_message). error_message is None when quantity is a valid positive whole number."""
    if isinstance(value, bool):
        return None, "Quantity must be a valid whole number."
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            return None, "Quantity must be a valid whole number."
        quantity = int(value)
        if quantity <= 0:
            return None, "Quantity must be greater than zero."
        return quantity, None
    try:
        numeric = float(str(value).strip())
    except (ValueError, TypeError):
        return None, "Quantity must be a valid whole number."
    if not numeric.is_integer():
        return None, "Quantity must be a valid whole number."
    quantity = int(numeric)
    if quantity <= 0:
        return None, "Quantity must be greater than zero."
    return quantity, None


def _normalize_active(value: object) -> bool | None:
    """Return True/False, or None if the active flag is unrecognized/blank."""
    if isinstance(value, bool):
        return value
    if _is_blank(value):
        return None
    text = str(value).strip().lower()
    if text in _ACTIVE_TRUE_STRINGS:
        return True
    if text in _ACTIVE_FALSE_STRINGS:
        return False
    return None


def _build_product_master_lookup(product_master_df: pd.DataFrame) -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    for _, row in product_master_df.iterrows():
        sku = _to_trimmed_str(row["sku"])
        lookup[sku] = {
            "product_name": row.get("product_name"),
            "active": row.get("active"),
        }
    return lookup


def _make_error(
    row_number: int,
    error_code: str,
    error_message: str,
    severity: str,
    order_id: object = None,
    sku: object = None,
) -> ValidationErrorRow:
    error: ValidationErrorRow = {
        "row_number": row_number,
        "error_code": error_code,
        "error_message": error_message,
        "severity": severity,
    }
    if order_id is not None and not _is_blank(order_id):
        error["order_id"] = _to_trimmed_str(order_id)
    if sku is not None and not _is_blank(sku):
        error["sku"] = _to_trimmed_str(sku)
    return error


def _find_duplicate_order_ids(orders_df: pd.DataFrame) -> set[str]:
    ids = [
        _to_trimmed_str(value)
        for value in orders_df["order_id"]
        if not _is_blank(value)
    ]
    counts: dict[str, int] = {}
    for order_id in ids:
        counts[order_id] = counts.get(order_id, 0) + 1
    return {order_id for order_id, count in counts.items() if count > 1}


def _validate_row(
    row: pd.Series,
    row_number: int,
    duplicate_order_ids: set[str],
    product_master_lookup: dict[str, dict],
) -> list[ValidationErrorRow]:
    errors: list[ValidationErrorRow] = []
    order_id = row.get("order_id")
    sku = row.get("sku")

    # OV-001 — required fields, one error per missing field, fixed field order.
    for field, label in OV001_REQUIRED_FIELDS:
        if _is_blank(row.get(field)):
            errors.append(
                _make_error(row_number, "OV-001", f"{label} is missing.", "Error", order_id, sku)
            )

    blank_order_id = _is_blank(order_id)
    blank_sku = _is_blank(sku)
    blank_quantity = _is_blank(row.get("quantity"))
    blank_order_date = _is_blank(row.get("order_date"))
    blank_delivery_date = _is_blank(row.get("requested_delivery_date"))
    blank_priority = _is_blank(row.get("priority"))

    # OV-002 — duplicate order ID (skipped when order_id itself is blank; OV-001 already covers that).
    if not blank_order_id and _to_trimmed_str(order_id) in duplicate_order_ids:
        errors.append(
            _make_error(row_number, "OV-002", "Duplicate order ID found.", "Error", order_id, sku)
        )

    # OV-003 — SKU existence/active checks (skipped when sku itself is blank).
    if not blank_sku:
        sku_key = _to_trimmed_str(sku)
        product = product_master_lookup.get(sku_key)
        if product is None:
            errors.append(
                _make_error(
                    row_number,
                    "OV-003-UNKNOWN_SKU",
                    "SKU does not exist in product master.",
                    "Error",
                    order_id,
                    sku,
                )
            )
        else:
            active = _normalize_active(product.get("active"))
            if active is None:
                errors.append(
                    _make_error(
                        row_number,
                        "OV-003-INVALID_ACTIVE_FLAG",
                        "SKU active status is not valid in product master.",
                        "Error",
                        order_id,
                        sku,
                    )
                )
            elif active is False:
                errors.append(
                    _make_error(
                        row_number,
                        "OV-003-INACTIVE_SKU",
                        "SKU exists but is marked inactive in product master.",
                        "Error",
                        order_id,
                        sku,
                    )
                )

    # OV-004 — quantity must be a positive whole number (skipped when blank; OV-001 already covers that).
    quantity_value = None
    if not blank_quantity:
        quantity_value, quantity_error = _parse_quantity(row.get("quantity"))
        if quantity_error is not None:
            errors.append(_make_error(row_number, "OV-004", quantity_error, "Error", order_id, sku))

    # OV-005 — date parseability and delivery-before-order (skipped per-field when that field is blank).
    order_date_value = None
    if not blank_order_date:
        order_date_value = _parse_date(row.get("order_date"))
        if order_date_value is None:
            errors.append(
                _make_error(
                    row_number,
                    "OV-005-INVALID_ORDER_DATE",
                    "Order date is not a valid date.",
                    "Error",
                    order_id,
                    sku,
                )
            )

    delivery_date_value = None
    if not blank_delivery_date:
        delivery_date_value = _parse_date(row.get("requested_delivery_date"))
        if delivery_date_value is None:
            errors.append(
                _make_error(
                    row_number,
                    "OV-005-INVALID_DELIVERY_DATE",
                    "Requested delivery date is not a valid date.",
                    "Error",
                    order_id,
                    sku,
                )
            )

    if order_date_value is not None and delivery_date_value is not None:
        if delivery_date_value < order_date_value:
            errors.append(
                _make_error(
                    row_number,
                    "OV-005-DELIVERY_BEFORE_ORDER",
                    "Requested delivery date is earlier than order date.",
                    "Error",
                    order_id,
                    sku,
                )
            )

    # OV-006 — controlled priority values (skipped when blank; OV-001 already covers that).
    if not blank_priority:
        priority_value = _to_trimmed_str(row.get("priority"))
        if priority_value not in VALID_PRIORITIES:
            errors.append(
                _make_error(
                    row_number,
                    "OV-006",
                    "Priority must be High, Normal, or Low.",
                    "Error",
                    order_id,
                    sku,
                )
            )

    # OV-007 — payment terms missing is a Warning only, and is the exclusive rule for this field.
    if _is_blank(row.get("payment_terms")):
        errors.append(
            _make_error(row_number, "OV-007", "Payment terms are missing.", "Warning", order_id, sku)
        )

    return errors


def _sort_key(error: ValidationErrorRow) -> tuple[int, int, int]:
    rule_rank = _RULE_ORDER.get(error["error_code"], len(_RULE_ORDER))
    field_rank = 0
    if error["error_code"] == "OV-001":
        field = next(
            (f for f, label in OV001_REQUIRED_FIELDS if error["error_message"].startswith(label)),
            None,
        )
        field_rank = _OV001_FIELD_ORDER.get(field, len(OV001_REQUIRED_FIELDS))
    return (error["row_number"], rule_rank, field_rank)


def _build_valid_order_row(
    row: pd.Series, product_master_lookup: dict[str, dict]
) -> ValidOrderRow:
    order_date = _parse_date(row.get("order_date"))
    delivery_date = _parse_date(row.get("requested_delivery_date"))
    quantity_value, _ = _parse_quantity(row.get("quantity"))

    product_name = row.get("product_name")
    if _is_blank(product_name):
        sku_key = _to_trimmed_str(row.get("sku"))
        product = product_master_lookup.get(sku_key)
        if product is not None and not _is_blank(product.get("product_name")):
            product_name = product["product_name"]

    payment_terms = row.get("payment_terms")
    payment_terms_str = "" if _is_blank(payment_terms) else _to_trimmed_str(payment_terms)

    valid_order: ValidOrderRow = {
        "order_id": _to_trimmed_str(row.get("order_id")),
        "order_date": order_date.date().isoformat() if order_date is not None else "",
        "customer_name": _to_trimmed_str(row.get("customer_name")),
        "customer_region": _to_trimmed_str(row.get("customer_region")),
        "sku": _to_trimmed_str(row.get("sku")),
        "quantity": quantity_value if quantity_value is not None else 0,
        "requested_delivery_date": delivery_date.date().isoformat() if delivery_date is not None else "",
        "priority": _to_trimmed_str(row.get("priority")),
        "payment_terms": payment_terms_str,
    }
    if not _is_blank(product_name):
        valid_order["product_name"] = _to_trimmed_str(product_name)
    sales_owner = row.get("sales_owner")
    if not _is_blank(sales_owner):
        valid_order["sales_owner"] = _to_trimmed_str(sales_owner)
    return valid_order


def validate_orders(orders_df: pd.DataFrame, product_master_df: pd.DataFrame) -> OrderValidationResult:
    """Validate order lines against every OV-001..OV-007 rule and return the full result envelope."""
    duplicate_order_ids = _find_duplicate_order_ids(orders_df)
    product_master_lookup = _build_product_master_lookup(product_master_df)

    all_errors: list[ValidationErrorRow] = []
    valid_orders: list[ValidOrderRow] = []
    invalid_row_numbers: set[int] = set()

    for position, (_, row) in enumerate(orders_df.iterrows()):
        row_number = position + 2
        row_errors = _validate_row(row, row_number, duplicate_order_ids, product_master_lookup)
        all_errors.extend(row_errors)

        has_error_severity = any(error["severity"] == "Error" for error in row_errors)
        if has_error_severity:
            invalid_row_numbers.add(row_number)
        else:
            valid_orders.append(_build_valid_order_row(row, product_master_lookup))

    all_errors.sort(key=_sort_key)

    total_orders = len(orders_df)
    invalid_orders = len(invalid_row_numbers)
    duplicate_orders = sum(1 for error in all_errors if error["error_code"] == "OV-002")
    invalid_skus = sum(1 for error in all_errors if error["error_code"].startswith("OV-003"))
    missing_field_count = sum(1 for error in all_errors if error["error_code"] == "OV-001")

    summary: ValidationSummary = {
        "total_orders": total_orders,
        "valid_orders": total_orders - invalid_orders,
        "invalid_orders": invalid_orders,
        "duplicate_orders": duplicate_orders,
        "invalid_skus": invalid_skus,
        "missing_field_count": missing_field_count,
    }

    return {"summary": summary, "valid_orders": valid_orders, "errors": all_errors}
