# 05 — State Management and Data Flow

## Purpose

This file explains how state and data flow could work if the project uses React / Next.js.

## Core state types

The app has four major state areas:

1. Uploaded files
2. Processing state
3. Result data
4. Report download state

## Simple V1 state model

For a small app, local component state may be enough.

Example state:

```ts
const [orderFile, setOrderFile] = useState<File | null>(null);
const [inventoryFile, setInventoryFile] = useState<File | null>(null);
const [invoiceFile, setInvoiceFile] = useState<File | null>(null);
const [isProcessing, setIsProcessing] = useState(false);
const [validationResults, setValidationResults] = useState(null);
const [allocationResults, setAllocationResults] = useState(null);
const [paymentResults, setPaymentResults] = useState(null);
```

## Recommended V2 state tools

### TanStack Query

Best for:

- API fetching
- upload mutation
- caching result data
- loading/error states
- retry behavior

Use if frontend talks to FastAPI.

### Zustand

Best for:

- simple global UI state
- selected workflow step
- uploaded file metadata
- cross-page demo state

### Redux Toolkit

Use only if:

- following the original inventory dashboard tutorial closely
- wanting to demonstrate Redux/RTK Query
- app complexity grows

For this project, Redux is probably not necessary in V1.

## Recommended data flow with FastAPI

### Order validation

```text
User uploads orders.xlsx
→ frontend sends file to POST /api/orders/validate
→ FastAPI saves or processes file in memory
→ Python validation module checks rules
→ backend returns validation summary + table data
→ frontend renders KPI cards + error table
→ user downloads validation report
```

### Inventory allocation

```text
User uploads valid orders + inventory file
→ frontend sends files to POST /api/inventory/allocate
→ backend runs allocation logic
→ backend returns allocation results, backorders, remaining inventory
→ frontend renders status cards + tables
→ user downloads allocation report
```

### Payment aging

```text
User uploads invoices.xlsx
→ frontend sends file to POST /api/payments/aging
→ backend calculates aging buckets
→ frontend renders overdue amount, aging chart, follow-up table
→ user downloads payment report
```

## Suggested API response shape

```json
{
  "summary": {
    "total_rows": 120,
    "valid_rows": 108,
    "error_rows": 12
  },
  "results": [],
  "errors": [],
  "report_id": "validation_2026_07_09_001"
}
```

## UI state checklist

Every processing action should handle:

- idle
- file selected
- processing
- success
- validation warning
- error
- report ready

## Error handling principle

Show user-friendly business messages.

Bad:

```text
KeyError: 'sku'
```

Good:

```text
The uploaded order file is missing the required column: SKU.
Please use the sample template and try again.
```

## State management recommendation

For coding agents, ask them to implement state in this order:

1. Local state first
2. TanStack Query when API integration begins
3. Zustand only if cross-page workflow state becomes messy
4. Avoid Redux unless there is a strong reason
