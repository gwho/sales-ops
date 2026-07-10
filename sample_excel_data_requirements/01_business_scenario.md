# Business Scenario for Synthetic Data

## Scenario

The demo represents a Hong Kong-based sales admin / sales operations team supporting a fictional international medical device and healthcare equipment business.

The HK office coordinates customer orders from Hong Kong, Macau, and Mainland China. Sales admins receive Excel files from sales colleagues, check order-entry accuracy, verify SKU and inventory availability, allocate stock across regional warehouses, flag backorders and low-stock situations, and follow up overdue payments.

The synthetic data should resemble a realistic B2B medical device / healthcare equipment sales coordination environment. It must remain fully fictional and must not use real employer, customer, product, supplier, pricing, order, invoice, or confidential data.

## Fictional Business Context

Company type:

```text
International medical device / healthcare equipment company with HK regional sales operations
```

Operating model:

```text
HK office receives order spreadsheets from regional sales teams.
Sales admins validate order-entry quality before allocation.
Inventory may be held in HK, China, or overseas replenishment locations.
Low-stock items require supplier follow-up.
Finance or sales admins review overdue invoices and draft follow-up messages.
```

Product categories:

```text
Medical Devices
Optical / Lens-related SKUs
Diagnostic Equipment
Clinical Consumables
Service Parts
Software Licenses
Maintenance / Service Packages
```

Example product types:

```text
Diagnostic imaging accessory
Optical lens set
Replacement lens component
Clinical consumable pack
Device calibration kit
Medical equipment spare part
Annual software license
Preventive maintenance service package
```

Warehouse / supply-location names:

```text
HK Warehouse
China Warehouse
Europe Warehouse
```

Customer regions:

```text
Hong Kong
Guangdong
Shanghai
Beijing
Other Mainland China
Macau
```

Customer types for fictional names:

```text
Public hospital
Private clinic group
Medical distributor
University / research lab
Optical clinic chain
Service partner
```

## Data Realism Goals

The data should include normal cases and realistic problems:

- most orders are valid
- some orders have missing fields
- some orders use invalid or inactive SKUs
- some orders request more stock than available
- some products are locally available
- some products have limited stock
- some SKUs are low-stock or out-of-stock
- some customers have overdue invoices
- some invoices are partially paid
- invoices cover every current aging bucket

Avoid generating perfect data only. The demo needs realistic errors so the automation has something useful to detect.

## Current Rule Boundary

The current Python business layer only implements the V1 rules already in `src/order_validation.py`, `src/inventory_allocation.py`, and `src/payment_aging.py`.

Allowed current-scope context fields:

```text
lead_time_days
supplier_name
sales_owner
currency
payment_status
remarks
```

These fields are either already consumed as optional context or ignored harmlessly by the current modules.

Do **not** introduce the following as current V1 rules:

```text
source_region
forecast_flag
production_status
preferred_supply_source
monthly_average_demand
lead-time review priority
production / demand planning follow-up
customer credit-status validation
customer master required upload
```

Those ideas may remain future-compatible notes, but they require a separate ADR before they change Python outputs or UI behavior.

## Demo Story

The generated data should support this 60-second story:

```text
A sales admin receives Excel files from regional sales teams.
The tool validates order-entry mistakes against the product master.
Valid orders flow into inventory allocation.
Limited stock creates partial allocations, backorders, and supplier follow-up.
The payment aging page identifies overdue invoices and prepares draft reminder messages.
Reports can be exported after the workflows run.
```
