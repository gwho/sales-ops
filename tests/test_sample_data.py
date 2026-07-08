from datetime import date, timedelta

from src.excel_io import load_excel, validate_required_columns
from src.sample_data import (
    generate_inventory,
    generate_invoices,
    generate_orders,
    generate_product_master,
    write_sample_workbooks,
)

ORDER_REQUIRED_COLUMNS = [
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
INVENTORY_REQUIRED_COLUMNS = ["sku", "warehouse", "available_qty"]
INVOICE_REQUIRED_COLUMNS = ["invoice_id", "customer_name", "invoice_date", "due_date", "invoice_amount"]


def test_generate_product_master_has_required_columns_and_one_inactive_sku():
    df = generate_product_master()

    validate_required_columns(df, PRODUCT_MASTER_REQUIRED_COLUMNS, "product master file")
    assert (~df["active"]).sum() == 1


def test_generate_orders_has_required_columns():
    df = generate_orders(generate_product_master())

    validate_required_columns(df, ORDER_REQUIRED_COLUMNS, "orders file")


def test_generate_orders_has_exactly_one_duplicate_order_id():
    df = generate_orders(generate_product_master())

    duplicate_mask = df["order_id"].duplicated(keep=False)
    duplicated_ids = set(df.loc[duplicate_mask, "order_id"])

    assert duplicated_ids == {"SO-2026-005"}
    assert duplicate_mask.sum() == 2


def test_generate_orders_has_exactly_one_unknown_sku():
    product_master_df = generate_product_master()
    orders_df = generate_orders(product_master_df)

    known_skus = set(product_master_df["sku"])
    unknown_sku_rows = orders_df[~orders_df["sku"].isin(known_skus)]

    assert len(unknown_sku_rows) == 1
    assert unknown_sku_rows.iloc[0]["order_id"] == "SO-2026-009"


def test_generate_inventory_has_required_columns():
    df = generate_inventory(generate_product_master())

    validate_required_columns(df, INVENTORY_REQUIRED_COLUMNS, "inventory file")


def test_generate_inventory_only_references_known_skus():
    product_master_df = generate_product_master()
    inventory_df = generate_inventory(product_master_df)

    known_skus = set(product_master_df["sku"])

    assert set(inventory_df["sku"]) <= known_skus


def test_generate_inventory_has_at_least_one_sku_below_reorder_point():
    df = generate_inventory(generate_product_master())

    allocatable = df["available_qty"] - df["reserved_qty"].fillna(0)
    below_reorder = df[allocatable < df["reorder_point"]]

    assert len(below_reorder) >= 1


def test_generate_invoices_has_required_columns():
    df = generate_invoices(reference_date=date(2026, 7, 9))

    validate_required_columns(df, INVOICE_REQUIRED_COLUMNS, "invoices file")


def test_generate_invoices_has_exactly_one_missing_due_date_row():
    df = generate_invoices(reference_date=date(2026, 7, 9))

    assert df["due_date"].isna().sum() == 1
    assert df.loc[df["due_date"].isna(), "invoice_id"].iloc[0] == "INV-2026-009"


def test_generate_invoices_high_priority_example_is_unambiguously_overdue():
    # Data-shape assertion only: confirms the due-date offset for the designated
    # high-priority example is >60 days before reference_date and the outstanding
    # amount is >= 50000. Does not compute days_overdue/aging_bucket/
    # follow_up_priority — those rules belong to Phase 5, not this generator.
    reference_date = date(2026, 7, 9)
    df = generate_invoices(reference_date=reference_date)

    row = df[df["invoice_id"] == "INV-2026-001"].iloc[0]
    days_before_reference = (reference_date - row["due_date"]).days
    outstanding = row["invoice_amount"] - row["paid_amount"]

    assert days_before_reference > 60
    assert outstanding >= 50000


def test_generate_invoices_dates_shift_with_reference_date():
    reference_a = date(2026, 7, 9)
    reference_b = reference_a + timedelta(days=10)

    row_a = generate_invoices(reference_date=reference_a)
    row_a = row_a[row_a["invoice_id"] == "INV-2026-001"].iloc[0]
    row_b = generate_invoices(reference_date=reference_b)
    row_b = row_b[row_b["invoice_id"] == "INV-2026-001"].iloc[0]

    assert row_b["due_date"] == row_a["due_date"] + timedelta(days=10)
    assert row_b["invoice_date"] == row_a["invoice_date"] + timedelta(days=10)


def test_write_sample_workbooks_round_trips_through_excel(tmp_path):
    write_sample_workbooks(output_dir=tmp_path, reference_date=date(2026, 7, 9))

    orders_df = load_excel(tmp_path / "sample_orders.xlsx")
    validate_required_columns(orders_df, ORDER_REQUIRED_COLUMNS, "orders file")

    product_master_df = load_excel(tmp_path / "sample_product_master.xlsx")
    validate_required_columns(product_master_df, PRODUCT_MASTER_REQUIRED_COLUMNS, "product master file")

    inventory_df = load_excel(tmp_path / "sample_inventory.xlsx")
    validate_required_columns(inventory_df, INVENTORY_REQUIRED_COLUMNS, "inventory file")

    invoices_df = load_excel(tmp_path / "sample_invoices.xlsx")
    validate_required_columns(invoices_df, INVOICE_REQUIRED_COLUMNS, "invoices file")
