# 03 — Page-by-Page UI Specification

## Page 1 — Overview Dashboard

### Purpose

Give the hiring manager an instant understanding of what the toolkit does.

### Layout

- Page title: Sales Admin Automation Toolkit
- Subtitle: Python/Excel automation for order validation, inventory allocation, and payment aging
- KPI cards
- Workflow stepper
- Recent report summary
- Quick action buttons

### UI elements

- KPI card grid
- order status chart
- payment aging chart
- latest processing summary
- sample data download buttons

### Example KPIs

- Orders Processed
- Validation Errors
- Fully Allocated Orders
- Backorders
- Overdue Amount
- Follow-up Items

### Acceptance criteria

- User can understand the app purpose within 10 seconds.
- Dashboard shows summary results after a workflow is run.
- Empty state appears if no files are uploaded.

## Page 2 — Order Validation

### Purpose

Validate Excel-based sales orders before further processing.

### Layout

- Upload order file panel
- Required columns guide
- Run validation button
- Validation summary cards
- Error table
- Valid orders table
- Export validation report button

### Table columns

Error table:

- row_number
- order_id
- customer_name
- sku
- issue_type
- issue_message
- severity

Valid orders table:

- order_id
- customer_name
- sku
- quantity
- requested_delivery_date
- priority
- status

### UI details

- Highlight error rows clearly
- Show issue messages in plain English
- Allow filtering by issue type
- Show count by error type

### Acceptance criteria

- Missing required fields are shown clearly.
- Invalid SKUs are separated from missing data issues.
- Duplicate orders are easy to identify.
- User can download a validation report.

## Page 3 — Inventory Allocation

### Purpose

Allocate available inventory to valid orders and identify backorders.

### Layout

- Upload inventory file panel
- Allocation rules panel
- Run allocation button
- Allocation KPI cards
- Allocation result table
- Backorder table
- Remaining inventory table
- Export allocation report button

### Allocation KPI cards

- Fully Allocated Orders
- Partially Allocated Orders
- Backordered Orders
- Remaining Stock Items

### Allocation table columns

- order_id
- customer_name
- sku
- requested_quantity
- allocated_quantity
- backorder_quantity
- warehouse
- allocation_status
- priority

### Backorder table columns

- sku
- total_backorder_quantity
- affected_orders
- suggested_follow_up

### Acceptance criteria

- Allocation status is visually clear.
- User can see exactly what stock was allocated.
- Backorders are separated into a follow-up table.
- The business rules are visible on the page.

## Page 4 — Payment Aging

### Purpose

Generate a payment follow-up report from invoice data.

### Layout

- Upload invoice/payment file panel
- Aging rule summary
- Payment aging KPI cards
- Aging bucket chart
- Overdue invoice table
- Follow-up priority table
- Export payment aging report button

### KPI cards

- Total Invoice Amount
- Overdue Amount
- 60+ Days Overdue
- High Priority Follow-ups

### Table columns

- invoice_id
- customer_name
- invoice_date
- due_date
- amount
- days_overdue
- aging_bucket
- follow_up_priority
- suggested_action

### Acceptance criteria

- Aging buckets are correct and visible.
- High-risk follow-ups are easy to identify.
- User can download a payment aging report.

## Page 5 — Reports / Export Center

### Purpose

Central place for exporting all generated reports.

### Layout

- Report list cards
- Generated timestamp
- Download buttons
- Included sheets preview

### Report options

- Validation Report
- Allocation Report
- Payment Aging Report
- Full Operations Report

### Acceptance criteria

- User can download all reports from one page.
- Each report has a short explanation.
- Export buttons are disabled if reports are not generated yet.

## Optional Page 6 — CRM Cleaner

### Purpose

Detect duplicate or incomplete customer records.

### Layout

- Upload customer file panel
- CRM issue summary
- duplicate records table
- missing information table
- export CRM cleaning report button

### Table columns

- customer_id
- company_name
- contact_person
- email
- phone
- issue_type
- suggested_action

### Acceptance criteria

- Duplicate contacts are grouped clearly.
- Missing contact information is flagged.
- Output is useful for sales/admin follow-up.
