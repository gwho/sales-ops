# Data Generation Rules

## Core Instruction for Coding Agents

Create or refine a deterministic Python sample-data generator. Do not manually write arbitrary spreadsheet rows.

The generator should:

```text
1. define fictional products, customers, warehouses, suppliers, and sales owners
2. generate product master records using the current product-master schema
3. generate optional customer reference records
4. generate inventory records using available_qty / reserved_qty
5. generate order rows using the current order-validation schema
6. intentionally inject controlled order-entry issues
7. generate invoice rows using invoice_id and the current payment-aging schema
8. export Excel files
9. write README_sample_data.md
10. provide tests that prove schema compatibility and intentional issue coverage
```

## Deterministic Generation

Use fixed seeds so files can be regenerated consistently.

Example:

```python
RANDOM_SEED = 42
```

Dates that support aging should be generated relative to an explicit `reference_date: date | None = None`, resolved inside the function body. Do not use a literal date as a default argument.

## Suggested Scale

Keep the demo small enough to inspect manually but large enough to make tables, filters, and charts meaningful.

```text
30-50 products
20-40 customers
3 warehouses
80-150 order rows
50-120 invoice rows
```

If this scale makes the static UI too noisy, prefer smaller defaults with clearly documented constants.

## Current Schema Names

Agents must use these exact current column names for workflow files:

```text
Product master: sku, product_name, active
Orders: order_id, order_date, customer_name, customer_region, sku, quantity, requested_delivery_date, priority, payment_terms
Inventory: sku, warehouse, available_qty
Invoices: invoice_id, customer_name, invoice_date, due_date, invoice_amount
```

Use optional columns only where the current Python layer already tolerates or consumes them.

## Intentional Order Issues

Recommended issue ratio:

```text
80-85% normal rows
15-20% rows with intentional issues
```

Intentional issues should include a controlled mix of:

```text
missing customer_name
missing sku
unknown sku
inactive sku
duplicate order_id
quantity is zero
quantity is negative
quantity is non-whole-number
missing requested_delivery_date
requested_delivery_date before order_date
blank payment_terms warning
invalid priority outside High | Normal | Low
```

Do not overdo errors. The data should feel like a plausible operations day, not a disguised unit-test matrix.

## Allocation Cases

Generated orders and inventory should guarantee:

```text
some orders fully allocate
some orders partially allocate
at least one valid order backorders
at least one SKU/warehouse remains below reorder_point after allocation
inventory never starts with negative available_qty or reserved_qty
reserved_qty affects allocatable stock
```

Do not introduce lead-time review or production-planning outputs. `lead_time_days` is allowed as supplier-follow-up context only.

## Invoice Aging Cases

Generated invoices must cover:

```text
Current
1-30 Days
31-60 Days
61-90 Days
90+ Days
Paid
Unpaid
Partially paid
High priority by overdue age
High priority by outstanding amount
Missing due_date data issue
Invalid invoice_amount data issue
```

The current payment-aging logic derives status from dates and amounts. Do not rely on `payment_status` for business logic.

## No Forecasting Scope

Do not generate sales history or forecasting inputs for current V1.

Future-compatible fields can be discussed separately, but they must not change current Python outputs, report sheets, or UI tables without an ADR.
