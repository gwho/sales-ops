# Sample Excel Data Generation Requirements

This folder contains agent-facing requirements for improving the synthetic Excel sample data for the **Sales Admin Automation Toolkit**.

The requirements are now aligned to the current Python business layer. Do not rename columns or add required workflow inputs unless an ADR explicitly changes the contracts.

## Current Scope

In scope:

- Order Entry Validation
- Inventory Allocation
- Payment Aging
- Excel report export support
- Sample files that a user can upload in Phase 10 once the FastAPI layer is wired

Out of scope:

- Forecasting
- demand planning models
- customer master validation
- credit-control rules
- production planning rules
- new output contracts
- new UI tables or workflow pages

## Active Scenario

Use one scenario consistently:

> A Hong Kong-based sales admin / sales operations team supports a fictional international medical device and healthcare equipment business. The team validates regional order spreadsheets, allocates available inventory by SKU and warehouse, flags low-stock / backorder situations, and follows up overdue invoices.

All names, SKUs, suppliers, customers, orders, invoices, prices, and dates must be fictional.

## Files To Generate

Required for the current three workflow pages:

```text
sample_product_master.xlsx
sample_orders.xlsx
sample_inventory.xlsx
sample_invoices.xlsx
README_sample_data.md
```

Optional reference-only file:

```text
sample_customers.xlsx
```

`sample_customers.xlsx` may help the data feel credible, but the current Python business layer does **not** consume it. Do not make customer master upload required in Phase 10 without a separate planning decision.

## Main Principle

Do not ask an LLM to manually invent spreadsheet rows. Build a deterministic Python generator with fixed seeds and explicit scenario lists.

Generated data should be:

- fictional
- repeatable
- business-plausible
- internally consistent
- small enough for a live demo
- intentionally imperfect enough to exercise the current validation, allocation, and payment-aging rules
- compatible with the exact Python schemas documented in [02_generated_files_and_schemas.md](./02_generated_files_and_schemas.md)

## Agent Workflow

Before implementation, invoke the skills and instructions in [08_agent_instructions_with_skills.md](./08_agent_instructions_with_skills.md).
