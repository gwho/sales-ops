# Project Overview

## Product

**Sales Admin Automation Toolkit** is a portfolio project for Excel-based sales administration and operations workflows. It demonstrates how a focused internal tool can help a sales coordinator, sales administrator, operations executive, supply chain assistant, or trading/logistics coordinator review daily business files faster and with fewer manual mistakes.

The active implementation path is **Python business logic first, polished Next.js dashboard second**.

## Core Message

This is a practical portfolio demo inspired by sales admin and operations work. It validates order spreadsheets, allocates inventory, prioritizes payment follow-up, and exports clean report packs. It is not a full ERP, accounting system, warehouse system, CRM, or production workflow tool.

## Why Python First

The strongest proof in this project is the business-rule automation:

- Does the tool catch realistic order-entry errors?
- Does allocation behave correctly when stock is limited?
- Does payment aging produce useful follow-up priorities?
- Can the reports be exported in a format operations teams understand?

The UI should present these outputs clearly, but it should not define them. Build the tested Python outputs first, then design the dashboard around them.

## Primary Workflows

1. **Order Validation**
   - Read a daily sales order Excel file and product master.
   - Check missing fields, duplicate order IDs, invalid SKUs, invalid quantities, delivery-date errors, and missing payment terms.
   - Return validation KPIs, valid order rows, and business-readable validation errors.

2. **Inventory Allocation**
   - Use valid order lines and inventory records.
   - Allocate stock by priority, delivery date, SKU, and warehouse availability.
   - Return full allocations, partial allocations, backorders, remaining inventory, and supplier follow-up items.

3. **Payment Aging**
   - Read invoice/payment records.
   - Calculate outstanding amount, days overdue, aging bucket, and follow-up priority.
   - Return overdue invoices, high-priority follow-ups, and draft reminder messages.

4. **Reports and Export**
   - Generate Excel reports for validation, allocation, payment aging, and an optional full operations report pack.

## Future Dashboard Pages

```text
/dashboard              Overview dashboard
/order-validation       Order validation workflow
/inventory-allocation   Inventory allocation workflow
/payment-aging          Payment aging workflow
/reports                Reports and export center
```

These routes are planned for the Next.js phase after Python output contracts are stable.

CRM Cleaner is postponed unless added later.

## First Milestone

Build tested Python modules and fictional sample files.

Included:

- Python package structure
- sample Excel files
- order validation module and tests
- inventory allocation module and tests
- payment aging module and tests
- report export module and tests
- stable JSON-serializable output contracts

UI contract and wireframe planning can begin after the sample data and contract fixtures exist. Polished frontend implementation waits until the core rule tests and report export tests pass.

Excluded:

- Polished Next.js implementation
- FastAPI endpoints
- Authentication
- Database persistence
- Real customer/order/invoice data
- AI predictions or automation agents
- ERP/accounting/WMS/CRM production scope

## Future UI Goal

The eventual UI should be a polished Next.js dashboard with:

- Sidebar navigation
- KPI cards
- upload panels
- workflow steppers
- status badges
- readable operations tables
- simple business charts
- report cards
- empty/loading/error states

The UI design work may happen early at wireframe level, but final UI implementation should follow the Python output contracts.

## Target Audience

The demo should be understandable to a non-technical hiring manager while still showing good engineering habits to a technical reviewer.

Primary audiences:

- Sales Coordinator / Sales Administrator hiring managers
- Operations Executive / Supply Chain Assistant hiring managers
- IT consulting or trading company interviewers
- Technical reviewers evaluating business-rule tests and clean architecture

## Success Criteria

- Python tests prove every core validation, allocation, and aging rule.
- Sample files use fictional but realistic business records.
- Output contracts are stable enough for a frontend to consume.
- Reports contain business-readable sheet names and follow-up tables.
- If the project stops before Next.js, the Python modules, sample files, and generated Excel reports are still strong enough to demo.
- The future dashboard can map each KPI, table, chart, and status badge to real Python outputs.
- The project clearly avoids production ERP claims and real confidential data.

## Portfolio Positioning

Recommended project title:

> Sales Admin Automation Toolkit - Python / Excel / Next.js Dashboard

Recommended short description:

> A practical sales operations portfolio project that uses Python to validate order spreadsheets, allocate inventory, calculate payment aging, and export Excel report packs, with a polished Next.js dashboard planned on top of the tested business-rule outputs.
