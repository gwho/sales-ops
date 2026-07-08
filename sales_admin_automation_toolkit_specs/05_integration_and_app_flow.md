# Integration and App Flow

## 1. Portfolio name

Recommended name:

> **Sales Admin Automation Toolkit**

Alternative names:

- Sales & Inventory Operations Assistant
- Sales Operations Excel Automation Demo
- Sales Coordination Automation Toolkit
- Order-to-Cash Admin Assistant

## 2. Main concept

The toolkit contains three small, connected demos:

1. Order Entry Validation
2. Inventory Allocation
3. Payment Aging Report

Together, these represent a simplified sales admin / operations workflow:

```text
Customer Order Excel
  → validate order data
  → allocate available inventory
  → identify backorders and supplier follow-up
  → check outstanding payment/invoice status
  → export clean Excel reports
```

## 3. End-to-end workflow

### Step 1 — Validate orders

Input:

- `orders.xlsx`
- `product_master.xlsx`

Output:

- `valid_orders`
- `validation_errors`
- `order_validation_report.xlsx`

### Step 2 — Allocate inventory

Input:

- `valid_orders`
- `inventory.xlsx`

Output:

- `allocation_results`
- `backorders`
- `remaining_inventory`
- `supplier_follow_up`
- `inventory_allocation_report.xlsx`

### Step 3 — Generate payment aging report

Input:

- `invoices.xlsx`

Output:

- `aging_summary`
- `follow_up_list`
- `draft_messages`
- `payment_aging_report.xlsx`

### Optional Step 4 — Clean CRM data

Input:

- `customers.xlsx`

Output:

- `crm_issues`
- `possible_duplicates`
- `crm_cleaning_report.xlsx`

## 4. Suggested Streamlit page layout

```text
app.py

Sidebar:
- Overview
- Order Validation
- Inventory Allocation
- Payment Aging
- CRM Cleaner (Optional)
- Download Sample Files
- About Project
```

## 5. Overview page

The overview page should explain the purpose and show a simple process diagram.

Suggested content:

```text
This portfolio demo shows how Python and Excel automation can support daily sales admin and operations workflows.

Upload order, inventory, and invoice files to validate data, allocate stock, calculate payment aging, and export clean follow-up reports.
```

### Overview KPI cards

If files have been processed, show:

- total orders checked,
- validation errors found,
- fully allocated orders,
- backordered orders,
- overdue amount,
- high-priority payment follow-ups.

## 6. Download sample files page

Provide buttons to download sample templates:

- `sample_orders.xlsx`
- `sample_product_master.xlsx`
- `sample_inventory.xlsx`
- `sample_invoices.xlsx`
- `sample_customers.xlsx` optional

## 7. Combined report

Optional V1.5 feature:

Generate one combined Excel workbook:

`operations_follow_up_pack.xlsx`

Suggested sheets:

1. `Executive Summary`
2. `Order Validation Errors`
3. `Valid Orders`
4. `Allocation Results`
5. `Backorders`
6. `Supplier Follow-up`
7. `Payment Aging`
8. `Payment Follow-up Messages`
9. `CRM Data Issues` optional

## 8. Suggested folder structure

```text
sales-admin-automation-toolkit/
  README.md
  requirements.txt
  app.py
  src/
    __init__.py
    excel_io.py
    order_validation.py
    inventory_allocation.py
    payment_aging.py
    crm_cleaning.py
    report_export.py
    sample_data.py
  sample_data/
    sample_orders.xlsx
    sample_product_master.xlsx
    sample_inventory.xlsx
    sample_invoices.xlsx
    sample_customers.xlsx
  tests/
    test_order_validation.py
    test_inventory_allocation.py
    test_payment_aging.py
    test_crm_cleaning.py
  docs/
    project_brief.md
    business_rules.md
    demo_script.md
    screenshots.md
```

## 9. Recommended implementation order

Build in this order:

```text
1. Create sample data files
2. Build order validation logic
3. Add pytest tests for order validation
4. Build inventory allocation logic
5. Add pytest tests for allocation
6. Build payment aging logic
7. Add pytest tests for payment aging
8. Build Excel export functions
9. Build Streamlit UI
10. Add README and screenshots
11. Deploy to Streamlit Community Cloud
12. Prepare interview demo script
```

## 10. Coding agent instruction

Use this prompt with coding agents:

```text
We are building a small portfolio project called Sales Admin Automation Toolkit.

Do not build a full ERP system. Do not add authentication, complex database persistence, or enterprise workflows in V1.

Focus on three connected Python/Excel automation demos:
1. Order Entry Validation
2. Inventory Allocation
3. Payment Aging Report

Optional: CRM Data Cleaner.

Before writing code, first confirm:
- input Excel columns,
- business rules,
- expected outputs,
- test cases,
- Streamlit page layout.

Implement business logic in separate Python modules under src/.
Add pytest tests before building the Streamlit UI.
Use fictional sample data only.
```
