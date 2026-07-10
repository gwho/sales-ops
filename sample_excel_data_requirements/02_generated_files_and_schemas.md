# Generated Excel Files and Current Python Schemas

This document is the schema source for the sample-data generator. It is aligned to the current Python business layer and should be treated as stricter than the earlier draft prompts.

Do not use alternate names such as `is_active`, `available_stock`, `reserved_stock`, `invoice_no`, `payment_term_days`, or priority `Standard`. Those names do not match the current code.

## 1. `sample_product_master.xlsx`

Purpose: reference file for valid SKUs and product information used by Order Validation.

Current required columns:

```text
sku
product_name
active
```

Recommended optional columns:

```text
category
unit_price
default_supplier
reorder_point
```

Rules:

- `sku` values must be unique.
- Most SKUs should have `active = True`.
- Include a small number of inactive SKUs to exercise `OV-003-INACTIVE_SKU`.
- `active` must be boolean-like (`True`/`False`, `yes`/`no`, etc.) and should usually be real booleans in generated files.
- Optional prices and reorder points must be plausible and positive when present.

## 2. `sample_orders.xlsx`

Purpose: input file for Order Validation; valid rows then feed Inventory Allocation.

Current required columns:

```text
order_id
order_date
customer_name
customer_region
sku
quantity
requested_delivery_date
priority
payment_terms
```

Recommended optional columns:

```text
product_name
sales_owner
```

Controlled values:

```text
priority = High | Normal | Low
```

Rules:

- Most orders should reference valid active SKUs.
- Include duplicate `order_id` values intentionally.
- Include a small number of unknown SKUs intentionally.
- Include a small number of inactive SKUs intentionally.
- Include a small number of missing required fields intentionally.
- Include invalid quantities intentionally (`0`, negative, non-whole-number, or non-numeric values).
- Requested delivery dates should usually be after order dates.
- Include at least one requested delivery date before the order date.
- Blank `payment_terms` is a warning-only case in the current Python layer, not a disqualifying required-field error.

## 3. `sample_inventory.xlsx`

Purpose: stock availability and warehouse allocation input.

Current required columns:

```text
sku
warehouse
available_qty
```

Recommended optional columns already supported by the current allocation logic:

```text
reserved_qty
reorder_point
supplier_name
lead_time_days
```

Rules:

- SKUs should reference `sample_product_master.xlsx`.
- The same SKU may appear in multiple warehouses.
- Include enough stock for many orders.
- Include limited-stock cases that create partial allocations.
- Include at least one fully backordered case when valid orders are allocated.
- Include at least one SKU/warehouse where remaining stock falls below `reorder_point`.
- `available_qty`, `reserved_qty`, `reorder_point`, and `lead_time_days` must not be negative when present.
- `reserved_qty` reduces allocatable quantity but does not reduce the reported starting available quantity.

## 4. `sample_invoices.xlsx`

Purpose: input file for Payment Aging.

Current required columns:

```text
invoice_id
customer_name
invoice_date
due_date
invoice_amount
```

Recommended optional columns:

```text
paid_amount
currency
payment_status
sales_owner
remarks
order_id
```

Rules:

- Include invoices in every aging bucket:
  - `Current`
  - `1-30 Days`
  - `31-60 Days`
  - `61-90 Days`
  - `90+ Days`
- Include paid invoices where `paid_amount >= invoice_amount`.
- Include partially paid invoices.
- Include high-priority examples where `days_overdue > 60` or `outstanding_amount >= 50000`.
- Include exactly controlled data issues:
  - missing `due_date`
  - invalid or negative `invoice_amount`
- `paid_amount` may be blank; the current Python layer treats missing or invalid paid amounts as `0`.
- `paid_amount` should usually not exceed `invoice_amount`, except if a deliberate overpayment example is explicitly documented.

## 5. Optional `sample_customers.xlsx`

Purpose: reference-only context for realism. The current Python business layer does not consume this file.

Suggested columns:

```text
customer_id
customer_name
customer_region
customer_type
contact_person
email
phone
payment_terms
credit_status
```

Rules:

- Customer names must be fictional.
- `customer_name` should match names used in orders and invoices where practical.
- Payment terms may be `15 days`, `30 days`, `45 days`, or `60 days`.
- Some customers can have a warning credit status, but current V1 logic must not validate or act on credit status.

## 6. `README_sample_data.md`

Purpose: explain the generated sample files.

Must include:

- fictional-data disclosure
- generation date
- random seed used
- file descriptions
- intended demo workflows
- exact required columns per upload file
- known intentional data issues
- note that `sample_customers.xlsx`, if generated, is reference-only in the current app
