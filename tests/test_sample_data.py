from datetime import date, timedelta

from src.excel_io import load_excel, validate_required_columns
from src.sample_data import (
    generate_customers,
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
CUSTOMER_REQUIRED_COLUMNS = ["customer_id", "customer_name", "customer_region", "customer_type", "payment_terms", "credit_status"]


def test_generate_product_master_has_required_columns_and_two_inactive_skus():
    df = generate_product_master()

    validate_required_columns(df, PRODUCT_MASTER_REQUIRED_COLUMNS, "product master file")
    assert (~df["active"]).sum() == 2


def test_generate_product_master_skus_are_unique():
    df = generate_product_master()

    assert df["sku"].is_unique


def test_generate_orders_has_required_columns():
    df = generate_orders(generate_product_master())

    validate_required_columns(df, ORDER_REQUIRED_COLUMNS, "orders file")


def test_generate_orders_has_exactly_one_duplicate_order_id():
    df = generate_orders(generate_product_master())

    duplicate_mask = df["order_id"].duplicated(keep=False)
    duplicated_ids = set(df.loc[duplicate_mask, "order_id"])

    assert duplicated_ids == {"SO-2026-010"}
    assert duplicate_mask.sum() == 2


def test_generate_orders_has_exactly_one_unknown_sku():
    product_master_df = generate_product_master()
    orders_df = generate_orders(product_master_df)

    known_skus = set(product_master_df["sku"])
    unknown_sku_rows = orders_df[orders_df["sku"].notna() & ~orders_df["sku"].isin(known_skus)]

    assert len(unknown_sku_rows) == 1
    assert unknown_sku_rows.iloc[0]["order_id"] == "SO-2026-030"


def test_generate_orders_has_exactly_one_inactive_sku_reference():
    product_master_df = generate_product_master()
    orders_df = generate_orders(product_master_df)

    inactive_skus = set(product_master_df.loc[~product_master_df["active"], "sku"])
    inactive_sku_rows = orders_df[orders_df["sku"].isin(inactive_skus)]

    assert len(inactive_sku_rows) == 1
    assert inactive_sku_rows.iloc[0]["order_id"] == "SO-2026-031"


def test_generate_orders_has_exactly_one_missing_sku_row():
    df = generate_orders(generate_product_master())

    missing_sku_rows = df[df["sku"].isna()]

    assert len(missing_sku_rows) == 1
    assert missing_sku_rows.iloc[0]["order_id"] == "SO-2026-032"


def test_generate_orders_has_exactly_one_blank_payment_terms_row():
    df = generate_orders(generate_product_master())

    blank_terms_rows = df[df["payment_terms"].isna()]

    assert len(blank_terms_rows) == 1
    assert blank_terms_rows.iloc[0]["order_id"] == "SO-2026-032"


def test_generate_orders_has_exactly_one_zero_quantity_row():
    df = generate_orders(generate_product_master())

    zero_qty_rows = df[df["quantity"] == 0]

    assert len(zero_qty_rows) == 1
    assert zero_qty_rows.iloc[0]["order_id"] == "SO-2026-033"


def test_generate_orders_has_exactly_one_missing_requested_delivery_date_row():
    df = generate_orders(generate_product_master())

    missing_delivery_rows = df[df["requested_delivery_date"].isna()]

    assert len(missing_delivery_rows) == 1
    assert missing_delivery_rows.iloc[0]["order_id"] == "SO-2026-033"


def test_generate_orders_has_exactly_one_negative_quantity_row():
    df = generate_orders(generate_product_master())

    negative_qty_rows = df[df["quantity"] < 0]

    assert len(negative_qty_rows) == 1
    assert negative_qty_rows.iloc[0]["order_id"] == "SO-2026-034"


def test_generate_orders_has_exactly_one_invalid_priority_row():
    df = generate_orders(generate_product_master())

    invalid_priority_rows = df[~df["priority"].isin(["High", "Normal", "Low"])]

    assert len(invalid_priority_rows) == 1
    assert invalid_priority_rows.iloc[0]["order_id"] == "SO-2026-034"


def test_generate_orders_has_exactly_one_non_whole_quantity_row():
    df = generate_orders(generate_product_master())

    non_whole_qty_rows = df[df["quantity"] % 1 != 0]

    assert len(non_whole_qty_rows) == 1
    assert non_whole_qty_rows.iloc[0]["order_id"] == "SO-2026-035"


def test_generate_orders_has_exactly_one_delivery_before_order_date_row():
    df = generate_orders(generate_product_master())

    dated_rows = df[df["requested_delivery_date"].notna()]
    before_order_rows = dated_rows[dated_rows["requested_delivery_date"] < dated_rows["order_date"]]

    assert len(before_order_rows) == 1
    assert before_order_rows.iloc[0]["order_id"] == "SO-2026-035"


def test_generate_orders_row_count_and_issue_ratio_stay_moderate():
    df = generate_orders(generate_product_master())

    assert 30 <= len(df) <= 40

    # Rows carrying at least one intentional issue, identified by order_id
    # (the duplicate row is the second SO-2026-010 occurrence).
    issue_order_ids = {
        "SO-2026-030",
        "SO-2026-031",
        "SO-2026-032",
        "SO-2026-033",
        "SO-2026-034",
        "SO-2026-035",
    }
    issue_row_count = df["order_id"].isin(issue_order_ids).sum() + 1  # +1 for the duplicate row

    ratio = issue_row_count / len(df)
    assert 0.15 <= ratio <= 0.25


def test_generate_inventory_has_required_columns():
    df = generate_inventory(generate_product_master())

    validate_required_columns(df, INVENTORY_REQUIRED_COLUMNS, "inventory file")


def test_generate_inventory_only_references_known_active_skus():
    product_master_df = generate_product_master()
    inventory_df = generate_inventory(product_master_df)

    known_skus = set(product_master_df["sku"])

    assert set(inventory_df["sku"]) <= known_skus


def test_generate_inventory_has_at_least_one_sku_below_reorder_point():
    df = generate_inventory(generate_product_master())

    allocatable = df["available_qty"] - df["reserved_qty"].fillna(0)
    below_reorder = df[allocatable < df["reorder_point"]]

    assert len(below_reorder) >= 1


def test_generate_inventory_has_no_negative_starting_quantities():
    df = generate_inventory(generate_product_master())

    assert (df["available_qty"] >= 0).all()
    assert (df["reserved_qty"].fillna(0) >= 0).all()


def test_generate_inventory_has_at_least_one_sku_with_no_stock_at_all():
    # Guarantees at least one valid order fully backorders: an active,
    # orderable SKU with zero inventory rows anywhere.
    product_master_df = generate_product_master()
    inventory_df = generate_inventory(product_master_df)

    active_skus = set(product_master_df.loc[product_master_df["active"], "sku"])
    stocked_skus = set(inventory_df["sku"])

    assert "PART-CAL-015" in active_skus
    assert "PART-CAL-015" not in stocked_skus


def test_generate_invoices_has_required_columns():
    df = generate_invoices(reference_date=date(2026, 7, 9))

    validate_required_columns(df, INVOICE_REQUIRED_COLUMNS, "invoices file")


def test_generate_invoices_row_count_stays_moderate():
    df = generate_invoices(reference_date=date(2026, 7, 9))

    assert 25 <= len(df) <= 30


def test_generate_invoices_has_exactly_one_missing_due_date_row():
    df = generate_invoices(reference_date=date(2026, 7, 9))

    assert df["due_date"].isna().sum() == 1
    assert df.loc[df["due_date"].isna(), "invoice_id"].iloc[0] == "INV-2026-024"


def test_generate_invoices_has_exactly_one_invalid_amount_row():
    df = generate_invoices(reference_date=date(2026, 7, 9))

    invalid_amount_rows = df[df["invoice_amount"] < 0]

    assert len(invalid_amount_rows) == 1
    assert invalid_amount_rows.iloc[0]["invoice_id"] == "INV-2026-025"


def test_generate_invoices_has_exactly_one_deliberate_overpayment_row():
    df = generate_invoices(reference_date=date(2026, 7, 9))

    # Excludes the invalid-amount row: a negative invoice_amount trivially makes
    # paid_amount (0) look like an "overpayment", which isn't the intentional case.
    valid_amount_rows = df[df["invoice_amount"] >= 0]
    overpaid_rows = valid_amount_rows[valid_amount_rows["paid_amount"] > valid_amount_rows["invoice_amount"]]

    assert len(overpaid_rows) == 1
    assert overpaid_rows.iloc[0]["invoice_id"] == "INV-2026-026"


def test_generate_invoices_high_priority_example_is_unambiguously_overdue():
    # Data-shape assertion only: confirms the due-date offset for the designated
    # high-priority example is >60 days before reference_date and the outstanding
    # amount is >= 50000. Does not compute days_overdue/aging_bucket/
    # follow_up_priority — those rules belong to payment_aging.py, not this generator.
    reference_date = date(2026, 7, 9)
    df = generate_invoices(reference_date=reference_date)

    row = df[df["invoice_id"] == "INV-2026-001"].iloc[0]
    days_before_reference = (reference_date - row["due_date"]).days
    outstanding = row["invoice_amount"] - row["paid_amount"]

    assert days_before_reference > 60
    assert outstanding >= 50000


def test_generate_invoices_span_every_aging_bucket_range():
    # Data-shape assertion only: confirms due-date offsets exist within each of
    # the 5 aging-bucket day ranges (Current/1-30/31-60/61-90/90+). Does not
    # compute aging_bucket itself — that rule belongs to payment_aging.py.
    reference_date = date(2026, 7, 9)
    df = generate_invoices(reference_date=reference_date)
    dated = df[df["due_date"].notna()].copy()
    dated["days_overdue"] = dated["due_date"].apply(lambda due: (reference_date - due).days)

    assert (dated["days_overdue"] <= 0).any()
    assert ((dated["days_overdue"] >= 1) & (dated["days_overdue"] <= 30)).any()
    assert ((dated["days_overdue"] >= 31) & (dated["days_overdue"] <= 60)).any()
    assert ((dated["days_overdue"] >= 61) & (dated["days_overdue"] <= 90)).any()
    assert (dated["days_overdue"] > 90).any()


def test_generate_invoices_dates_shift_with_reference_date():
    reference_a = date(2026, 7, 9)
    reference_b = reference_a + timedelta(days=10)

    row_a = generate_invoices(reference_date=reference_a)
    row_a = row_a[row_a["invoice_id"] == "INV-2026-001"].iloc[0]
    row_b = generate_invoices(reference_date=reference_b)
    row_b = row_b[row_b["invoice_id"] == "INV-2026-001"].iloc[0]

    assert row_b["due_date"] == row_a["due_date"] + timedelta(days=10)
    assert row_b["invoice_date"] == row_a["invoice_date"] + timedelta(days=10)


def test_generate_customers_has_required_columns():
    df = generate_customers()

    validate_required_columns(df, CUSTOMER_REQUIRED_COLUMNS, "customers file")


def test_generate_customers_ids_are_unique():
    df = generate_customers()

    assert df["customer_id"].is_unique


def test_generate_customers_names_mostly_match_orders_and_invoices():
    customers_df = generate_customers()
    orders_df = generate_orders(generate_product_master())
    invoices_df = generate_invoices(reference_date=date(2026, 7, 9))

    order_names = set(orders_df["customer_name"].dropna())
    invoice_names = set(invoices_df["customer_name"].dropna())

    assert set(customers_df["customer_name"]) <= order_names
    assert set(customers_df["customer_name"]) <= invoice_names


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

    customers_df = load_excel(tmp_path / "sample_customers.xlsx")
    validate_required_columns(customers_df, CUSTOMER_REQUIRED_COLUMNS, "customers file")
