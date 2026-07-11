# Architecture

## Current Target

The active architecture is **Python business logic first, polished Next.js dashboard second**.

The repo is currently a planning/spec workspace. The next implementation should create the Python package, sample data, and tests before scaffolding the Next.js UI.

## Stack

| Layer | Tool | Purpose |
| --- | --- | --- |
| Business logic | Python | Order validation, inventory allocation, payment aging |
| Tabular data | pandas | Spreadsheet-like transformations and calculations |
| Excel I/O | openpyxl | Read/write `.xlsx` reports where pandas alone is insufficient |
| Tests | pytest | Business-rule regression coverage |
| Future API | FastAPI | Thin HTTP wrapper around tested Python modules |
| Future frontend | Next.js App Router | Polished portfolio dashboard |
| Future UI language | TypeScript strict | Typed UI contracts and components |
| Future styling | Tailwind CSS 3.4 | Token-based styling |
| Future components | shadcn/ui | Dashboard primitives where useful |
| Future tables/charts | TanStack Table, Recharts | Operations tables and simple business charts |

## First Scaffold Shape

```text
/
├── src/
│   ├── __init__.py
│   ├── excel_io.py
│   ├── order_validation.py
│   ├── inventory_allocation.py
│   ├── payment_aging.py
│   ├── report_export.py
│   └── sample_data.py
├── tests/
│   ├── test_order_validation.py
│   ├── test_inventory_allocation.py
│   ├── test_payment_aging.py
│   └── test_report_export.py
├── sample_data/
│   ├── sample_orders.xlsx
│   ├── sample_product_master.xlsx
│   ├── sample_inventory.xlsx
│   └── sample_invoices.xlsx
├── docs/
└── context/
```

## Future Frontend Shape

Plan this after Phase 2 contract fixtures are stable. Build it only after Phases 3-6 pass their test gates:

```text
/
├── app/
│   ├── dashboard/page.tsx
│   ├── order-validation/page.tsx
│   ├── inventory-allocation/page.tsx
│   ├── payment-aging/page.tsx
│   └── reports/page.tsx
├── components/
│   ├── layout/
│   ├── workflow/
│   ├── tables/
│   ├── feedback/
│   └── ui/
├── lib/
│   ├── api-client.ts
│   ├── mock-data.ts
│   └── formatters.ts
└── types/
    └── index.ts
```

## System Boundaries

| Area | Owns | Must not own |
| --- | --- | --- |
| `src/order_validation.py` | Order validation rules and validation result output | UI labels beyond business-readable messages |
| `src/inventory_allocation.py` | Allocation sorting, stock depletion, backorder and supplier follow-up outputs | Excel formatting or React concerns |
| `src/payment_aging.py` | Outstanding amount, aging buckets, follow-up priority, draft reminders | Email sending or accounting-system behavior |
| `src/report_export.py` | Excel workbook generation from result data | Business-rule calculations |
| `src/excel_io.py` | Loading and required-column validation helpers | Workflow-specific rules |
| `tests/` | Regression coverage for business rules | Snapshotting UI |
| `backend/` | FastAPI orchestration over tested modules | Duplicated business logic |
| Future `app/` and `components/` | UI composition and reusable dashboard components | Spreadsheet parsing or business-rule calculations |

## Python Output Contracts

The Python modules should return JSON-serializable structures that can later map cleanly to TypeScript.

Required output families:

- `ValidationSummary`
- `ValidationErrorRow`
- `ValidOrderRow`
- `AllocationSummary`
- `AllocationResultRow`
- `BackorderRow`
- `RemainingInventoryRow`
- `SupplierFollowUpRow`
- `PaymentAgingSummary`
- `PaymentAgingRow`
- `PaymentDataIssueRow` (added by `docs/adr/0005-payment-data-issue-row-contract.md` — the payment-aging Data Issues sheet required by `03_demo_payment_aging.md` PA-006/PA-007 had no matching contract)
- `DraftMessageRow`
- `ReportManifest`

Use snake_case keys in Python. Future TypeScript can either preserve API snake_case or map at the adapter boundary. Do not decide that mapping inside Python modules.

### Field scope boundary

Python owns fields explicitly specified by each workflow spec in `sales_admin_automation_toolkit_specs/`. UI may derive display copy from existing fields, but must not invent new business outcomes. Contracts are allowed to be asymmetric across output families when their specs are asymmetric.

Example: `PaymentAgingRow` includes `suggested_action` because `03_demo_payment_aging.md` §6-7 explicitly defines it as a deterministic output of the aging/priority rules. `AllocationResultRow` does not include `suggested_action` because `02_demo_inventory_allocation.md` never specifies one — allocation's `status`, `backorder_qty`, `warehouse`, and supplier follow-up fields are sufficient, and the future UI can derive display copy from `status` without a new contract field. Do not add a field to a contract for cross-module consistency alone; add it only when the corresponding spec is amended.

## API Contract (Phase 10)

Resolved via a `/grilling` session and `/architect` session before implementation — see `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`, `docs/grilling/phase-10-fastapi-integration/`, `docs/architect/phase-10-fastapi-integration/`, and `context/library-docs.md`'s "Future FastAPI" section for full detail.

```text
POST /api/orders/validate
POST /api/orders/validate/report

POST /api/inventory/allocate
POST /api/inventory/allocate/report

POST /api/payments/aging
POST /api/payments/aging/report

GET  /api/templates/{template_name}
```

`GET /api/reports/{report_id}` was never implemented — it implied persisted report artifacts, which contradicts the stateless architecture below. Each `.../report` endpoint re-accepts its workflow's source file(s) and recomputes server-side rather than trusting a client-supplied result.

Backend behavior:

- Process uploaded Excel files in memory only (`backend/uploads.py`); nothing is written to disk or retained after the response.
- Call the tested Python modules in `src/`, never duplicating business rules in route handlers.
- Return JSON matching the stable output contracts for the three workflow endpoints; return `.xlsx` bytes directly for the three report endpoints.
- Convert technical exceptions into business-readable `{"detail": "string"}` responses at the `backend/` boundary — `src/` itself stays framework-free.

## UI Design Input Workflow

The folders `ui_reference_to_figma_workflow/` and `ui_prompts_for_agents_mcp/` are guidance inputs, not final product truth.

Use them during UI contract and wireframe planning. This planning may begin after Phase 2 and can run in parallel with Python business-rule implementation.

1. Inspect references or Figma frames through MCP when available.
2. Produce screen inventory, component mapping, data requirements, and scope-control notes.
3. Check that each UI table and KPI maps to a real Python output.
4. Implement polished UI only after all spec-listed Python tests and Excel report structure tests pass.

If Figma MCP is unavailable, use screenshots and written specs as fallback.

## Scope Gate

Use this mechanical rule before implementing any spec item:

- Implement only rules from in-scope spec files that are labeled V1 or not labeled with a version.
- Do not implement any rule explicitly marked `Optional`, `V1.5`, or `V2` without a new ADR reopening scope.
- Do not implement `sales_admin_automation_toolkit_specs/04_optional_crm_cleaner.md` without a new ADR. The whole CRM Cleaner module is outside the active build even though it has detailed specs.
- Do not implement adjacent enterprise features just because they are small or easy. Ease of implementation is not enough to move a feature into scope.

Concrete examples:

- `02_demo_inventory_allocation.md` Rule IA-007 V1 warehouse choice is in scope: allocate from the warehouse with the highest available quantity for that SKU.
- `02_demo_inventory_allocation.md` Rule IA-007 Optional V2 region-matching preference is out of scope until an ADR explicitly adds it.
- `04_optional_crm_cleaner.md` is out of scope in full until an ADR explicitly adds it.

## V1 vs V2

In this repo:

- **V1** means the active portfolio build: Python-first Excel automation for order validation, inventory allocation, payment aging, and report export, followed by a polished Next.js presentation layer only after test gates pass.
- **V1.5** means a small candidate extension that may be useful after V1 is complete, but is not part of the current build.
- **V2** means deliberately postponed expansion work. It may be reasonable later, but it must not be implemented during V1 without an ADR.

V1/V2 labels are still necessary because the specs intentionally contain future ideas beside current rules. The labels stop future agents from treating every nearby idea as approved scope.

## Non-Goals for V1

- Authentication or user accounts
- Database persistence
- Role-based permissions
- Production file storage
- Realtime collaboration
- AI forecasting or risk scoring
- Email sending
- Real customer, employer, supplier, order, invoice, or product data
- Full ERP/accounting/WMS/CRM replacement
