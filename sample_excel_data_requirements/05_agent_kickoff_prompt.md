# Coding Agent Kickoff Prompt

Use this prompt when asking an agent to plan or implement the current-schema-aligned sample-data generator.

```text
I am building a portfolio project called Sales Admin Automation Toolkit.

Current scope:
- Order Entry Validation
- Inventory Allocation
- Payment Aging
- Excel report export
- Phase 10 will let users upload their own Excel files through the app

Forecasting, customer-master validation, credit-control rules, and production/demand-planning logic are not in scope.

I need synthetic but business-realistic Excel sample data for the demo. Do not manually invent random spreadsheet rows. Create or refine a deterministic Python data generator with fixed seeds.

Generate these files:
1. sample_product_master.xlsx
2. sample_orders.xlsx
3. sample_inventory.xlsx
4. sample_invoices.xlsx
5. README_sample_data.md

Optional reference-only file:
6. sample_customers.xlsx

The optional customer file must not become a required upload or Python business dependency unless a separate ADR approves that scope expansion.

Business scenario:
A Hong Kong-based sales admin / sales operations team supports a fictional international medical device and healthcare equipment business. The team validates regional order spreadsheets, allocates available inventory by SKU and warehouse, flags low-stock / backorder situations, and follows up overdue invoices.

Schema constraints:
- Use current Python column names exactly.
- Product master required columns: sku, product_name, active.
- Orders required columns: order_id, order_date, customer_name, customer_region, sku, quantity, requested_delivery_date, priority, payment_terms.
- Inventory required columns: sku, warehouse, available_qty.
- Invoices required columns: invoice_id, customer_name, invoice_date, due_date, invoice_amount.
- Priority values are High, Normal, Low. Do not use Standard.
- Inventory uses available_qty and reserved_qty. Do not use available_stock or reserved_stock.
- Product master uses active. Do not use is_active.
- Payment aging uses invoice_id. Do not use invoice_no.

Requirements:
- data must be fictional
- no real employer, client, supplier, product, order, invoice, or pricing data
- use fixed seeds
- SKUs must be mostly consistent across product, inventory, and order files
- include intentional order-entry issues for validation demo
- include inventory shortage, partial allocation, backorder, and low-stock cases
- include invoice aging cases: Current, 1-30 Days, 31-60 Days, 61-90 Days, 90+ Days
- include payment data issues: missing due_date and invalid invoice_amount
- keep file sizes small enough for a live demo
- include tests that verify generated files, columns, relationships, and business-rule coverage
- write README_sample_data.md explaining generated data and intentional issues

Before writing code, first produce:
1. final file list
2. exact schemas
3. generation rules
4. intentional error design
5. validation checks
6. implementation plan
7. risks and simplifications
8. list of things explicitly out of scope
```

## Required Skills To Invoke

Before implementation:

```text
/architect
```

Use `/architect` to confirm the final schemas, intentional issue design, and whether `sample_customers.xlsx` remains reference-only.

If the plan changes domain vocabulary or product scope:

```text
/grill-with-docs
```

Use `/grill-with-docs` only when discussing a real scope change such as customer-master validation or lead-time review outputs.

After implementation:

```text
/feature-docs
/project-review
```

Use `/feature-docs` to document what changed. Use `/project-review` to verify schema alignment, architecture boundaries, tests, and UI readiness.

Only invoke `/imprint` if new reusable UI components are created.
