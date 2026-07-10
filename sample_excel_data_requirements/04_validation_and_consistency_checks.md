# Validation and Consistency Checks

Generated sample data must be tested before being used by the demo app.

## Required Checks

Coding agents should implement automated checks such as:

```text
[ ] All expected Excel files are created
[ ] Product master contains sku, product_name, active
[ ] Orders contain current required order-validation columns
[ ] Inventory contains sku, warehouse, available_qty
[ ] Invoices contain invoice_id, customer_name, invoice_date, due_date, invoice_amount
[ ] Product SKUs are unique in product master
[ ] Most product SKUs are active
[ ] At least one inactive SKU exists
[ ] Most order SKUs exist in product master
[ ] Intentional unknown SKUs exist for validation demo
[ ] Intentional inactive-SKU order rows exist
[ ] Duplicate order IDs exist intentionally
[ ] Some orders have invalid quantities intentionally
[ ] Some orders have warning-only blank payment_terms intentionally
[ ] Inventory mostly references known SKUs
[ ] Some inventory items are below reorder point after allocation
[ ] Some valid orders cannot be fully allocated
[ ] Invoices include every aging bucket
[ ] At least one invoice triggers missing due_date data issue
[ ] At least one invoice triggers invalid invoice_amount data issue
[ ] Paid amount usually does not exceed invoice amount
[ ] No real company/client/supplier names are used
```

## Suggested Automated Test File

Use or extend:

```text
tests/test_sample_data.py
```

Only create `tests/test_sample_data_generation.py` if `/architect` decides to move generator code out of `src/sample_data.py` into a separate generation package.

## Relationship Checks

Examples:

```text
orders.sku should mostly match product_master.sku
inventory.sku should match product_master.sku
invoices.customer_name should mostly match orders.customer_name or optional customers.customer_name
invoices.order_id, if present, should mostly reference orders.order_id
customers.customer_name, if sample_customers.xlsx exists, should mostly match orders and invoices
```

Use "mostly" only where the mismatch is intentionally generated for validation demonstration. Every intentional mismatch should be documented in `README_sample_data.md`.

## End-to-End Compatibility Checks

Before declaring the sample data ready, agents should prove:

```text
load_orders(sample_orders.xlsx) succeeds on required columns
load_product_master(sample_product_master.xlsx) succeeds on required columns
validate_orders(...) returns both valid rows and validation errors
allocate_inventory(valid_orders, sample_inventory.xlsx) returns full, partial, and backorder outcomes
calculate_payment_aging(sample_invoices.xlsx) returns aging rows, data issues, and draft messages
report_export can export reports from the generated outputs
```

## Documentation Requirement

`README_sample_data.md` must state clearly:

```text
This sample data is fictional and generated for portfolio demonstration purposes.
It intentionally contains some errors and edge cases to demonstrate validation, allocation, and payment aging logic.
```
