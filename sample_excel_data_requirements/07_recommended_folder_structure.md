# Recommended Folder Structure

The current project already has a working sample generator in `src/sample_data.py`. Prefer refining that module unless `/architect` identifies a concrete reason to move generation code elsewhere.

Recommended current structure:

```text
sales-ops/
  src/
    sample_data.py
    order_validation.py
    inventory_allocation.py
    payment_aging.py
    report_export.py

  sample_data/
    sample_product_master.xlsx
    sample_orders.xlsx
    sample_inventory.xlsx
    sample_invoices.xlsx
    README_sample_data.md
    sample_customers.xlsx          # optional reference-only file

  tests/
    test_sample_data.py
    test_order_validation.py
    test_inventory_allocation.py
    test_payment_aging.py
    test_report_export.py
```

Alternative structure, only if approved during `/architect`:

```text
sales-ops/
  data_generation/
    generate_sample_data.py
    scenario_config.py
    README.md

  src/
    sample_data.py                 # may become a thin wrapper, if kept for compatibility
```

Do not introduce a new folder just because it looks cleaner. The current module is already covered by tests and used by existing sample-data workflows.

## GitHub Recommendation

Commit small generated sample files to GitHub so hiring managers and coding agents can run the project easily.

Do not commit:

```text
large datasets
real company data
private files
secrets
API keys
```

## Phase 10 UI Relationship

Phase 10 should let users upload files matching these same schemas:

```text
Order Validation page:
- sample_orders.xlsx
- sample_product_master.xlsx

Inventory Allocation page:
- valid orders from order validation output, or an uploaded valid-orders file matching the current valid-order schema
- sample_inventory.xlsx

Payment Aging page:
- sample_invoices.xlsx
```

If the UI offers sample-template download buttons, those buttons should download the committed files in `sample_data/`.
