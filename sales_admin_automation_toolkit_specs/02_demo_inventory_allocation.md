# Demo 2 — Inventory Allocation Mini Engine

## 1. Summary

The **Inventory Allocation Mini Engine** reads validated sales orders and available inventory, then decides which orders can be fully allocated, partially allocated, or backordered.

This demo directly maps to supply chain and operations work because it shows the logic behind allocating the right items to the right orders at the right time.

## 2. Business problem

When stock is limited, operations staff need to decide how inventory should be allocated. Manual checking with Excel formulas can cause mistakes, especially when there are many SKUs, warehouses, priorities, and delivery dates.

A small allocation engine can help by:

- sorting orders by priority and delivery date,
- checking available inventory by SKU and warehouse,
- allocating available stock,
- flagging shortages,
- producing backorder and supplier follow-up lists.

## 3. User story

As an operations or sales admin staff member, I want to upload validated orders and inventory data, then automatically generate an allocation report, so that I can see which orders can be fulfilled and which require follow-up.

## 4. Input files

### File 1

`valid_orders.xlsx`

This can come from Demo 1.

Required columns:

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
| priority | string | Yes | High |
| payment_terms | string | Yes | 30 days |

### File 2

`inventory.xlsx`

Required columns:

| Column | Type | Required | Example |
|---|---:|---:|---|
| sku | string | Yes | MED-LENS-001 |
| warehouse | string | Yes | HK Warehouse |
| available_qty | integer | Yes | 25 |
| reserved_qty | integer | Optional | 0 |
| reorder_point | integer | Optional | 5 |
| supplier_name | string | Optional | Supplier A |
| lead_time_days | integer | Optional | 14 |

## 5. Allocation rules

### Rule IA-001 — Sort order priority

Orders should be allocated in this order:

1. Priority: High before Normal before Low
2. Earlier requested delivery date first
3. Earlier order date first
4. Lower order ID alphabetically as tie-breaker

### Rule IA-002 — Available quantity

Available stock for allocation is:

```text
allocatable_qty = available_qty - reserved_qty
```

If `reserved_qty` is missing, treat it as 0.

### Rule IA-003 — Full allocation

If `allocatable_qty >= order quantity`, allocate full quantity and reduce inventory.

### Rule IA-004 — Partial allocation

If `allocatable_qty > 0` but less than order quantity, allocate the available amount and backorder the remaining quantity.

### Rule IA-005 — Backorder

If `allocatable_qty <= 0`, allocate 0 and mark the order as backordered.

### Rule IA-006 — Inventory must not go negative

After allocation, remaining inventory must never be negative.

### Rule IA-007 — Warehouse choice

V1 simple rule:

- Allocate from the warehouse with the highest available quantity for that SKU.

Optional V2 rule:

- Prefer warehouse matching customer region.

### Rule IA-008 — Reorder alert

If remaining stock after allocation is below `reorder_point`, flag the SKU for supplier follow-up.

## 6. Output

### Screen output

The app should display:

- total order lines,
- fully allocated count,
- partially allocated count,
- backordered count,
- low-stock SKU count,
- allocation result table,
- supplier follow-up table.

### Downloadable output

`inventory_allocation_report.xlsx`

Suggested sheets:

1. `Allocation Summary`
2. `Allocation Results`
3. `Backorders`
4. `Remaining Inventory`
5. `Supplier Follow-up`

### Allocation result columns

| Column | Description |
|---|---|
| order_id | Sales order ID |
| customer_name | Customer name |
| sku | SKU |
| product_name | Product name |
| requested_qty | Original order quantity |
| allocated_qty | Quantity allocated |
| backorder_qty | Quantity not allocated |
| warehouse | Allocating warehouse |
| status | Fully Allocated / Partially Allocated / Backordered |
| priority | Order priority |
| requested_delivery_date | Requested delivery date |

### Remaining inventory columns

| Column | Description |
|---|---|
| sku | SKU |
| warehouse | Warehouse |
| starting_available_qty | Original available quantity |
| allocated_qty | Total allocated quantity |
| remaining_qty | Remaining quantity |
| reorder_point | Reorder point |
| reorder_alert | Yes / No |

## 7. Status definitions

| Status | Meaning |
|---|---|
| Fully Allocated | requested quantity fully allocated |
| Partially Allocated | some quantity allocated, remaining quantity backordered |
| Backordered | no stock available for this order line |

## 8. UI requirements

### Page title

`Inventory Allocation`

### UI elements

- File uploader for validated orders
- File uploader for inventory
- Button: `Run Allocation`
- KPI cards:
  - Total Order Lines
  - Fully Allocated
  - Partial
  - Backordered
  - Low Stock SKUs
- Allocation result table
- Backorder table
- Supplier follow-up table
- Download report button

### Empty state

Show:

> Upload validated orders and inventory files to run allocation.

### Processing message

Show:

> Allocating inventory by priority, delivery date, and stock availability...

## 9. Suggested Python modules

```text
src/
  inventory_allocation.py
  excel_io.py
  report_export.py
```

## 10. Suggested functions

```python
def prepare_orders_for_allocation(valid_orders_df: pd.DataFrame) -> pd.DataFrame:
    """Sort valid orders by allocation priority."""


def calculate_allocatable_inventory(inventory_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate allocatable quantity for each SKU/warehouse."""


def allocate_inventory(valid_orders_df: pd.DataFrame, inventory_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return allocation_results_df, remaining_inventory_df, supplier_follow_up_df."""


def export_inventory_allocation_report(allocation_results_df, remaining_inventory_df, supplier_follow_up_df) -> bytes:
    """Return Excel report as bytes."""
```

## 11. Test cases

| Test case | Input | Expected output |
|---|---|---|
| Enough stock | order 10, stock 20 | Fully Allocated, remaining 10 |
| Partial stock | order 10, stock 6 | Partially Allocated, backorder 4 |
| No stock | order 10, stock 0 | Backordered, backorder 10 |
| High priority first | high and normal compete for stock | high allocated first |
| Earlier delivery first | same priority, different dates | earlier date allocated first |
| Reserved stock | available 20, reserved 5 | only 15 allocatable |
| No negative inventory | multiple orders exceed stock | remaining never below 0 |
| Reorder alert | remaining below reorder point | supplier follow-up flag Yes |

## 12. Interview explanation

> This module shows how Python can support inventory allocation decisions. It sorts orders by priority and delivery date, checks stock by SKU and warehouse, allocates available stock, creates backorders, and flags low-stock items for supplier follow-up. It is intentionally simple, but it demonstrates the core operational logic behind order fulfillment.
