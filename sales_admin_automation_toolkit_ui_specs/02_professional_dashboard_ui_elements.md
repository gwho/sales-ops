# 02 — Professional Dashboard UI Elements

## Design direction

The UI should look like a clean internal B2B operations tool.

Suggested style:

- light theme first
- white / slate / neutral background
- blue accent color
- clear tables
- subtle status badges
- restrained charts
- professional spacing
- no flashy consumer-app style
- no crypto-dashboard visual noise

## Core UI elements

### 1. Top summary KPI cards

Display at the top of the dashboard.

Recommended cards:

- Total Orders Uploaded
- Valid Orders
- Orders With Errors
- Fully Allocated Orders
- Backordered Quantity
- Overdue Invoice Amount
- High Priority Follow-ups

Each card should include:

- label
- main value
- small helper text
- status icon or trend indicator

Example:

```text
Orders With Errors
12
Need review before processing
```

### 2. Workflow stepper

Shows where the user is in the process.

Steps:

1. Upload files
2. Validate orders
3. Allocate inventory
4. Review payment aging
5. Export report

This helps the hiring manager understand the demo flow immediately.

### 3. Upload panel

Professional upload area with:

- drag-and-drop area
- accepted file type note
- sample template download link
- selected filename display
- file validation message

Suggested text:

```text
Upload daily order Excel file
Accepted format: .xlsx
Required columns: order_id, customer_name, sku, quantity, requested_delivery_date, priority
```

### 4. Status badges

Use consistent badges across the app.

Recommended statuses:

Order validation:

- Valid
- Missing Data
- Invalid SKU
- Duplicate Order
- Invalid Quantity

Inventory allocation:

- Fully Allocated
- Partially Allocated
- Backordered
- Stockout

Payment aging:

- Current
- Due Soon
- Overdue
- High Risk

Visual tone:

- green for good
- amber for warning
- red for urgent
- blue/slate for neutral

### 5. Data tables

Tables are the most important UI element because sales admin and operations work is table-heavy.

Table features:

- sortable columns
- filter/search input
- pagination
- sticky header if possible
- row status badges
- compact but readable spacing
- export selected/all rows

Important tables:

- Order validation results
- Inventory allocation results
- Backorder list
- Payment aging report
- Follow-up priority list

### 6. Alert banners

Use business-readable alerts.

Examples:

```text
12 orders require review before allocation.
```

```text
3 SKUs do not have enough stock. Supplier follow-up is recommended.
```

```text
HKD 42,300 is overdue for more than 60 days.
```

Avoid technical messages such as:

```text
ValueError: column not found
```

### 7. Report download section

A clear final step:

- Download Validation Report
- Download Allocation Report
- Download Payment Aging Report
- Download Full Operations Report

Add a short explanation:

```text
Reports are exported in Excel format for daily team follow-up.
```

### 8. Charts

Keep charts simple.

Useful charts:

- order status breakdown
- allocation status breakdown
- overdue amount by aging bucket
- backordered quantity by SKU
- follow-up priority count

Avoid too many charts. The app should feel like an operations tool, not a BI art project.

### 9. Empty states

Every page should explain what to do before data exists.

Example:

```text
No order file uploaded yet.
Upload a sample order file to run validation and see results here.
```

### 10. Loading states

When processing Excel files:

- show spinner or progress text
- disable action button while processing
- show success/failure feedback

Example:

```text
Processing order file and checking validation rules...
```

### 11. Business rule summary panel

A small side panel can show the rules being applied.

Example:

```text
Allocation rules:
1. High priority orders first
2. Earlier delivery date first
3. Partial allocation allowed
4. Remaining quantity becomes backorder
```

This is impressive in interviews because it shows your logic clearly.

### 12. Demo mode banner

Because this is a portfolio project, add a small banner:

```text
Demo mode: uses fictional sample data only.
```

This signals privacy awareness.
