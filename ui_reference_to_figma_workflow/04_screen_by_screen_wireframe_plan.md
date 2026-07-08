# 04 — Screen-by-Screen Wireframe Plan

## Goal

Define the key screens that should be planned before implementation.

Only design the screens that matter for the demo.

---

# 1. Overview Dashboard

## Purpose

Give the hiring manager an immediate understanding of the tool's value.

## Layout

- Sidebar navigation
- Top header with project name and upload status
- KPI cards
- Main workflow progress
- Recent issues table
- Small charts
- Report export shortcut

## UI elements

```text
KPI cards:
- Orders Uploaded
- Validation Errors
- Fully Allocated Orders
- Backordered Quantity
- Overdue Amount

Charts:
- Order status breakdown
- Payment aging buckets
- Inventory shortage by category

Tables:
- Top issues requiring follow-up
```

## Hiring-manager impression

This screen should communicate:

```text
This person understands daily operations and can summarize messy Excel workflows clearly.
```

---

# 2. Order Validation Screen

## Purpose

Show how the tool catches order-entry mistakes.

## Layout

- Upload panel
- Required columns checklist
- Validation summary cards
- Error table
- Valid orders preview
- Export validation report button

## UI elements

```text
UploadPanel
RequiredColumnsChecklist
ValidationSummaryCard
ValidationErrorTable
ValidOrdersPreviewTable
ExportButton
```

## Table columns

```text
Row Number
Order ID
Customer
SKU
Issue Type
Issue Detail
Suggested Action
Severity
```

## Status badges

```text
Missing Field
Invalid SKU
Duplicate Order
Invalid Quantity
Missing Delivery Date
```

---

# 3. Inventory Allocation Screen

## Purpose

Show how available inventory is allocated to orders.

## Layout

- Input summary
- Allocation rules panel
- Allocation results table
- Remaining inventory table
- Backorder / supplier follow-up panel
- Export allocation report button

## UI elements

```text
AllocationRulesCard
AllocationResultTable
RemainingInventoryTable
BackorderSummaryPanel
SupplierFollowUpList
ExportButton
```

## Table columns

```text
Order ID
Customer
SKU
Requested Qty
Allocated Qty
Backorder Qty
Warehouse
Priority
Status
```

## Status badges

```text
Fully Allocated
Partially Allocated
Backordered
Invalid SKU
Insufficient Stock
```

---

# 4. Payment Aging Screen

## Purpose

Show overdue payment follow-up priorities.

## Layout

- Aging bucket cards
- Overdue invoice table
- Follow-up priority panel
- Draft reminder preview
- Export payment aging report button

## UI elements

```text
AgingBucketCards
OverdueInvoiceTable
PriorityBadge
ReminderPreviewCard
ExportButton
```

## Table columns

```text
Invoice Number
Customer
Invoice Amount
Due Date
Days Overdue
Aging Bucket
Priority
Suggested Action
```

## Status badges

```text
Current
1-30 Days
31-60 Days
61-90 Days
90+ Days
High Priority
```

---

# 5. Reports / Export Center

## Purpose

Make the app feel like a usable business tool.

## Layout

- Report cards
- Last generated time
- Included sheets
- Download buttons
- Full operations report option

## Report cards

```text
Validation Report
Allocation Report
Payment Aging Report
Full Operations Report
```

## UI elements

```text
ReportCard
DownloadButton
IncludedSheetsList
GeneratedTimeBadge
```
