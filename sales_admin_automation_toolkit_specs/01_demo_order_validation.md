# Demo 1 — Order Entry Validation Tool

## 1. Summary

The **Order Entry Validation Tool** checks Excel-based sales order files before they are processed. It identifies missing fields, invalid SKUs, duplicate order numbers, invalid quantities, and incomplete delivery/payment information.

This is the safest and most directly useful demo for sales admin and operations roles because order accuracy is a common daily responsibility.

## 2. Business problem

Sales/admin teams often receive order information from customers, salespeople, or internal teams in inconsistent Excel formats. Common problems include:

- missing customer name,
- duplicate order number,
- invalid SKU,
- incorrect quantity,
- missing requested delivery date,
- missing payment terms,
- incomplete contact information.

These mistakes cause delays, wrong deliveries, stock allocation errors, and extra back-and-forth communication.

## 3. User story

As a sales admin / operations staff member, I want to upload a daily sales order file and automatically check for common errors, so that I can fix issues before sending the order to warehouse, supplier, or internal processing teams.

## 4. Input file

### File name

`orders.xlsx`

### Required columns

| Column | Type | Required | Example |
|---|---:|---:|---|
| order_id | string | Yes | SO-2026-001 |
| order_date | date | Yes | 2026-07-10 |
| customer_name | string | Yes | Bright Medical Trading Ltd |
| customer_region | string | Yes | Hong Kong |
| sku | string | Yes | MED-LENS-001 |
| product_name | string | Optional | Optical Lens Kit |
| quantity | integer | Yes | 10 |
| requested_delivery_date | date | Yes | 2026-07-15 |
| priority | string | Yes | High / Normal / Low |
| payment_terms | string | Yes | 30 days |
| sales_owner | string | Optional | Jesse |

## 5. Reference file

### File name

`product_master.xlsx`

### Required columns

| Column | Type | Required | Example |
|---|---:|---:|---|
| sku | string | Yes | MED-LENS-001 |
| product_name | string | Yes | Optical Lens Kit |
| category | string | Optional | Medical Device |
| active | boolean/string | Yes | TRUE |

## 6. Validation rules

### Rule OV-001 — Required fields

The following fields must not be empty:

- `order_id`
- `order_date`
- `customer_name`
- `customer_region`
- `sku`
- `quantity`
- `requested_delivery_date`
- `priority`
- `payment_terms`

### Rule OV-002 — Duplicate order ID

If the same `order_id` appears more than once, flag it as a duplicate.

### Rule OV-003 — Valid SKU

The `sku` must exist in `product_master.xlsx` and must be active.

### Rule OV-004 — Quantity must be positive

The `quantity` must be greater than 0 and must be a whole number.

### Rule OV-005 — Delivery date must not be earlier than order date

If `requested_delivery_date < order_date`, flag as invalid.

### Rule OV-006 — Priority must be controlled value

Allowed values:

- High
- Normal
- Low

### Rule OV-007 — Payment terms must be provided

Payment terms should not be blank. V1 does not need to validate complex payment terms, but missing values should be flagged.

## 7. Output

### Screen output

The app should display:

- total orders uploaded,
- valid order count,
- invalid order count,
- duplicate order count,
- invalid SKU count,
- missing field count,
- a table of validation errors.

### Downloadable output

`order_validation_report.xlsx`

Suggested sheets:

1. `Summary`
2. `Valid Orders`
3. `Validation Errors`
4. `Original Orders`

### Validation error table columns

| Column | Description |
|---|---|
| row_number | Excel row number or internal row index |
| order_id | Order ID if available |
| sku | SKU if available |
| error_code | Example: OV-003 |
| error_message | Human-readable error |
| severity | Error / Warning |

## 8. Example errors

| error_code | error_message | severity |
|---|---|---|
| OV-001 | Customer name is missing | Error |
| OV-002 | Duplicate order ID found | Error |
| OV-003 | SKU does not exist in product master | Error |
| OV-004 | Quantity must be greater than zero | Error |
| OV-005 | Requested delivery date is earlier than order date | Error |
| OV-006 | Priority must be High, Normal, or Low | Error |
| OV-007 | Payment terms are missing | Warning |

## 9. UI requirements

### Page title

`Order Entry Validation`

### UI elements

- File uploader for `orders.xlsx`
- File uploader for `product_master.xlsx`
- Button: `Run Validation`
- KPI cards:
  - Total Orders
  - Valid Orders
  - Invalid Orders
  - Duplicate Orders
  - Invalid SKUs
- Validation error table
- Download button for Excel report

### Empty state

Show:

> Upload an orders file and product master file to begin validation.

### Error state

If the file is missing required columns, show:

> The uploaded file is missing required columns: [column list]. Please check the sample template.

## 10. Suggested Python modules

```text
src/
  order_validation.py
  excel_io.py
  report_export.py
```

## 11. Suggested functions

```python
def load_orders(file) -> pd.DataFrame:
    """Load orders Excel file into a DataFrame."""


def load_product_master(file) -> pd.DataFrame:
    """Load product master Excel file into a DataFrame."""


def validate_orders(orders_df: pd.DataFrame, product_master_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return valid_orders_df and validation_errors_df."""


def export_order_validation_report(valid_orders_df, validation_errors_df, original_orders_df) -> bytes:
    """Return Excel report as bytes."""
```

## 12. Test cases

| Test case | Input | Expected output |
|---|---|---|
| Missing customer name | customer_name blank | OV-001 error |
| Duplicate order ID | same order_id twice | OV-002 error |
| Invalid SKU | SKU not in master | OV-003 error |
| Zero quantity | quantity = 0 | OV-004 error |
| Negative quantity | quantity = -3 | OV-004 error |
| Delivery before order | requested_delivery_date earlier | OV-005 error |
| Invalid priority | priority = Urgent | OV-006 error |
| Clean order | all fields valid | appears in Valid Orders |

## 13. Interview explanation

> This module reflects a common sales admin problem: order data often arrives in Excel and must be checked before processing. I built a validation tool that catches missing fields, duplicate order numbers, invalid SKUs, and quantity/date issues before they affect inventory allocation or delivery coordination.
