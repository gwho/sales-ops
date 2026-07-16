# Sales Admin Automation Toolkit Glossary

This file is the domain glossary for the active project. It contains business terms only, not implementation details.

## Terms

### Sales Admin Automation Toolkit

A portfolio demo for Excel-based sales administration and operations workflows. It focuses on order validation, inventory allocation, payment aging, and report export.

### Order

A customer request to purchase one or more products. In this project, orders are represented as spreadsheet rows for demonstration purposes.

### Order Line

One row in an order file representing one SKU and requested quantity for a customer order. The project treats allocation and validation at order-line level.

### Product Master

The reference list of valid SKUs and product names. Order validation uses it to identify invalid or inactive SKUs.

### SKU

Stock keeping unit. The product identifier used to match order lines against product master and inventory records.

### Validation Error

A business-readable issue found in an order file, such as a missing customer name, duplicate order ID, invalid SKU, invalid quantity, or invalid requested delivery date.

### Valid Order

An order line that passes the required validation rules and can proceed to inventory allocation.

### Inventory Record

A row describing available stock for a SKU in a warehouse, including available quantity, reserved quantity, reorder point, and supplier information when present.

### Allocatable Quantity

The quantity available for allocation after reserved stock is removed from available stock.

### Allocation Result

The outcome of applying inventory to an order line. It records requested quantity, allocated quantity, backorder quantity, warehouse, and allocation status.

### Fully Allocated

An allocation status where the requested quantity is completely covered by available stock.

### Partially Allocated

An allocation status where some stock is allocated but the remaining quantity becomes a backorder.

### Backorder

The unfulfilled quantity for an order line when available stock cannot cover the full request.

### Supplier Follow-up

An operational follow-up item created when stock is low, backordered, or below reorder point.

### Invoice

A billing record for a customer, including invoice amount, paid amount, due date, and payment status.

### Outstanding Amount

The unpaid amount on an invoice after subtracting paid amount from invoice amount.

### Payment Aging

The process of grouping unpaid invoices by how long they have been overdue.

### Aging Bucket

A label that groups invoices by due-date status: Current, 1-30 Days, 31-60 Days, 61-90 Days, or 90+ Days.

### Follow-up Priority

The priority assigned to a payment follow-up item. V1 labels are High, Medium, Low, Watch, and None.

### Draft Reminder

A suggested customer follow-up message for overdue invoices. In V1 it is sample/demo content, not an automated email.

### Report Pack

An Excel workbook or set of downloadable reports that summarize validation, allocation, backorder, supplier follow-up, payment aging, and draft reminder outputs.

### Output Contract

A stable, spec-derived field shape for a workflow output. It is defined once in the shared Python contract layer, populated by Python modules, and later reused as the API/frontend data shape.

### Contract Fixture

A realistic example value for an Output Contract. Contract Fixtures prove the shape can hold believable demo data; they are distinct from small pytest fixtures whose job is isolated rule coverage.

### Field Scope Boundary

The rule that an Output Contract may contain only fields explicitly defined by its originating workflow spec. Cross-module symmetry alone is not enough reason to add a field.

### V1

The active portfolio build scope: order validation, inventory allocation, payment aging, and report export using fictional Excel data, with a polished dashboard later as a presentation layer.

### V2

Postponed expansion work. A V2 label means the idea is explicitly not part of the active V1 build unless a new ADR reopens scope.

### Scope Gate

The rule that only V1 or unlabeled items from in-scope specs may be implemented. Optional, V1.5, V2, or CRM Cleaner work requires a new ADR before implementation.

### Demo Mode

The portfolio state where all records are fictional and the UI demonstrates workflow behavior without processing real business data.

### Workflow Request

A single API request that submits uploaded source file(s) and parameters for one business workflow (order validation, inventory allocation, or payment aging). The server always processes it against the corresponding tested Python module and returns its result the same way regardless of session identity — computation itself remains stateless and pure. As of Phase 12, if the request carries a valid Anonymous Session ID, the server also makes a best-effort attempt to persist the result as that session's Saved Workflow Result, reported via the `X-Persisted` header — a side effect, not a change to how the result is computed or returned.
_Avoid_: Workflow Run, Run, Job — these imply a persisted, trackable, or resumable entity; Phase 12 introduces only a single best-effort latest-result save, never a history, retry queue, or resumable job.

### Workflow Result

The JSON result returned by a Workflow Request, matching the corresponding Python module's Output Contract.

### Current Result

The most recent Workflow Result held in client-side page state. It exists only in the browser and is discarded on navigation or reload — the server retains no copy of it. Independent from this, Phase 12 may also produce a Saved Workflow Result for the same request — a separate, best-effort, server-side latest-result cache for dashboard display. It does not change what Current Result means: purely client-side, ephemeral, discarded on navigation.

### Anonymous Session ID

A UUID generated once in the browser via `crypto.randomUUID()` and stored in `localStorage`, sent as the `X-Session-Id` header on Workflow Requests and Report Export Requests. It identifies a browser profile only — no authentication, no user account, nothing server-side treats it as a login. Clearing browser storage creates a new, unrelated Anonymous Session ID.
_Avoid_: User ID, Account ID — these imply authenticated identity, which this project does not have.

### Saved Workflow Result

The most recent Workflow Result for a given Anonymous Session ID and workflow type, persisted to Postgres as a best-effort side effect of a Workflow Request. Saving a new one for the same session and workflow type overwrites the previous one — there is no history, only the latest.
_Avoid_: Workflow Run, Run History — these imply a persisted, browsable sequence of past requests, which this project does not keep.

### Workflow Results Store

The single Postgres table (`workflow_results`) holding every session's Saved Workflow Results, keyed by (Anonymous Session ID, workflow type). Unlike the Demo Reporting Database, it is not rebuilt from `sample_data/*.xlsx` on startup — it holds real, session-specific results from real Workflow Requests, and is the first genuinely persistent, non-disposable data store in this project.
_Avoid_: Demo Reporting Database — that term names a different, disposable, SQLite-based concept from the paused Phase 11 SQL-reporting design, not this one.

### Persistence Outcome

The `X-Persisted` response header on a Workflow Request, reporting whether the Workflow Result was saved as that session's Saved Workflow Result: `true` (saved), `false` (a valid Anonymous Session ID was supplied but the save failed — a transient infrastructure issue, not a data problem), or `skipped` (no Anonymous Session ID was supplied — standalone API use). It never appears on Report Export Request responses, which never persist.

### Dashboard Latest Results

The response shape of `GET /api/dashboard`: one field per workflow type, each either that session's Saved Workflow Result or `null` if none exists, is TTL-expired, or is Result Schema Version-incompatible. A dashboard-module aggregate type, not an Output Contract — it lives in the backend's dashboard module, not `src/contracts.py`, since Field Scope Boundary governs spec-derived contracts, not read-side aggregates over them.

### Result Schema Version

An integer stored alongside every Saved Workflow Result, identifying which version of its workflow type's Output Contract shape it was saved under. Bumped whenever a persisted Output Contract's fields change — the same mental checklist as editing `src/contracts.py` itself. `GET /api/dashboard` treats a stored result with a non-current version as unusable, the same as if it didn't exist.

### Display Expiry

The rule that a Saved Workflow Result older than a fixed TTL (default 30 days) is treated as unusable by `GET /api/dashboard` — the same as a missing or Result Schema Version-incompatible result — even though the row is not physically deleted. A visibility rule, not a data-deletion guarantee; physical cleanup is deferred out of Phase 12 scope.

### Report Export Request

A request to generate a downloadable Report Artifact for a workflow. It resubmits the same source file(s)/parameters as the corresponding Workflow Request and recomputes the result server-side before building the report — it never accepts a Current Result as authoritative report input, so an artifact can't be produced from client-edited data.

### Report Artifact

The `.xlsx` file returned directly in response to a Report Export Request. It is not stored server-side or retrievable later by an identifier — each request regenerates it fresh.

### Sample File

One of the committed `sample_data/*.xlsx` demo workbooks, made available for download alongside its corresponding upload step. It is realistic fictional demo data carrying the same intentional data-quality issues as the rest of the demo, not a blank or minimal starting template.
_Avoid_: Sample Template, Template — these imply a clean starting point, which is not what's served.

### Business Error

A business-readable failure describing a known, user-actionable problem with a Workflow Request or Report Export Request (missing columns, invalid data, malformed upload). Distinct from an unexpected technical failure, which the API converts into a generic message rather than exposing directly.
