# 01 — Figma AI / Figma Make UI Generation Prompts

Use these prompts inside Figma AI / Figma Make to generate initial dashboard screens and components.

---

## Master UI Generation Prompt

```text
Create a modern B2B SaaS dashboard UI for a portfolio project called “Sales Admin Automation Toolkit”.

The app helps sales admin and operations teams automate Excel-based workflows:
- upload sales order Excel files
- validate missing or incorrect order entries
- allocate inventory by SKU and warehouse
- flag backorders and supplier follow-up items
- generate payment aging reports
- export clean Excel reports

The visual style should be professional, clean, business-friendly, and suitable for an internal operations team. Use a light theme first, with white, slate, soft gray, and blue accents. Use amber for warnings, red for errors, green for completed items, and blue for primary actions.

The UI should not look like a crypto dashboard, consumer app, or generic AI app. It should feel like a reliable internal tool for sales coordinators, operations executives, and supply chain assistants.

Create these screens:
1. Overview Dashboard
2. Order Validation
3. Inventory Allocation
4. Payment Aging
5. Reports / Export Center

Use sidebar navigation, top header, KPI cards, data tables, status badges, upload panels, workflow stepper, alert panels, and export buttons.
```

---

## Overview Dashboard Prompt

```text
Design the Overview Dashboard screen for “Sales Admin Automation Toolkit”.

Purpose:
Give a hiring manager a quick view of how the tool supports daily sales admin and operations work.

Layout:
- left sidebar navigation
- top header with page title, search input, and “Upload Orders” button
- KPI card row
- main content area with charts and follow-up tables

KPI cards:
- Orders Uploaded
- Validation Errors
- Fully Allocated Orders
- Backordered Items
- Overdue Invoice Amount

Main panels:
1. Order Status Breakdown chart
2. Payment Aging Buckets chart
3. Inventory Shortage Alert panel
4. Top Follow-up Items table

Table columns for follow-up:
- Type
- Reference No.
- Customer / Supplier
- Issue
- Priority
- Suggested Action

Use professional spacing, compact cards, clear typography, and readable status badges.
```

---

## Order Validation Screen Prompt

```text
Design an Order Validation screen for “Sales Admin Automation Toolkit”.

This screen allows a sales admin user to upload an Excel order file and check for order-entry errors before processing.

UI elements:
- page title: Order Validation
- short helper text explaining the purpose
- workflow stepper: Upload → Validate → Review Errors → Export Report
- drag-and-drop Excel upload card
- sample template download link
- required columns checklist
- validation summary cards
- validation error table
- export validation report button

Required columns checklist:
- Order ID
- Customer Name
- SKU
- Quantity
- Requested Delivery Date
- Priority
- Payment Term

Validation summary cards:
- Total Rows
- Valid Orders
- Errors Found
- Duplicate Orders
- Invalid SKUs

Error table columns:
- Row No.
- Order ID
- Field
- Issue Type
- Current Value
- Suggested Fix
- Severity

Use status badges:
- Missing Field
- Invalid SKU
- Duplicate
- Invalid Quantity
- Warning
- Critical

The design should feel practical, not overdesigned. Make error messages business-readable, not technical.
```

---

## Inventory Allocation Screen Prompt

```text
Design an Inventory Allocation screen for “Sales Admin Automation Toolkit”.

This screen helps an operations user allocate available stock to sales orders.

Business logic:
- high-priority orders are allocated first
- earlier delivery dates are handled first
- stock is allocated by SKU and warehouse
- partial allocation is allowed
- remaining quantity becomes backorder

UI elements:
- page title: Inventory Allocation
- workflow stepper: Load Valid Orders → Match Inventory → Allocate Stock → Review Backorders
- filter bar for SKU, warehouse, customer, priority, and allocation status
- KPI cards
- allocation result table
- remaining inventory table
- supplier follow-up panel

KPI cards:
- Orders Ready for Allocation
- Fully Allocated
- Partially Allocated
- Backordered
- SKUs Below Reorder Point

Allocation table columns:
- Order ID
- Customer
- SKU
- Warehouse
- Requested Qty
- Allocated Qty
- Backorder Qty
- Priority
- Status
- Suggested Action

Status badges:
- Fully Allocated
- Partially Allocated
- Backordered
- Invalid SKU
- Supplier Follow-up

Supplier follow-up panel:
- SKU
- Shortage Qty
- Preferred Supplier
- Suggested Reorder Qty
- Follow-up Priority

Make the screen look like a serious internal operations dashboard used by sales coordinators and warehouse coordinators.
```

---

## Payment Aging Screen Prompt

```text
Design a Payment Aging screen for “Sales Admin Automation Toolkit”.

This screen helps sales admin staff identify overdue invoices and prioritize payment follow-up.

UI elements:
- page title: Payment Aging
- upload invoice/payment Excel file panel
- aging bucket cards
- overdue invoice table
- follow-up priority panel
- draft reminder preview card
- export payment aging report button

Aging bucket cards:
- Current
- 1–30 Days Overdue
- 31–60 Days Overdue
- 61–90 Days Overdue
- 90+ Days Overdue

Overdue invoice table columns:
- Invoice No.
- Customer
- Due Date
- Days Overdue
- Amount
- Aging Bucket
- Follow-up Priority
- Suggested Action

Priority rules shown in UI:
- High Priority: over 60 days overdue or high amount
- Medium Priority: 31–60 days overdue
- Low Priority: 1–30 days overdue

Draft reminder preview should look like a simple email card:
Subject, recipient, short message, copy button.

Style should be clean, finance-operations focused, and easy for non-technical users.
```

---

## Reports / Export Center Prompt

```text
Design a Reports / Export Center screen for “Sales Admin Automation Toolkit”.

This screen allows the user to download clean Excel reports generated by the toolkit.

UI elements:
- page title: Reports & Export
- report summary section
- report cards
- recent export history table
- final “Download Full Operations Report” button

Report cards:
1. Validation Error Report
2. Clean Orders Report
3. Inventory Allocation Report
4. Backorder & Supplier Follow-up Report
5. Payment Aging Report
6. Full Operations Report

Each report card should show:
- report name
- short description
- included sheets
- last generated time
- status
- download button

Recent export history table columns:
- Report Name
- Generated At
- File Type
- Rows Included
- Status
- Download

Use a professional report-center style. Make it feel like something an operations team can actually use after processing Excel files.
```

---

## Design System Prompt

```text
Create a lightweight design system for “Sales Admin Automation Toolkit”.

The design system should include:
- color palette
- typography
- spacing rules
- card style
- button styles
- table styles
- status badges
- upload panel
- alert panel
- KPI cards
- workflow stepper
- report cards

Visual direction:
- professional B2B SaaS
- internal operations dashboard
- light theme first
- clear, compact, readable
- suitable for sales admin, logistics, supply chain, and IT consulting workflows

Status badge categories:
- Success: Valid, Fully Allocated, Paid
- Warning: Partial, Needs Review, Due Soon
- Error: Invalid, Backordered, Overdue
- Neutral: Draft, Processing, Pending

Please create reusable components that could later map to React / Next.js components.
```
