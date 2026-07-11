# ADR 0006 - Stateless FastAPI Workflow and Report Endpoints

## Status

Accepted

## Context

`context/build-plan.md`'s Phase 10 section documented this endpoint list:

```text
POST /api/orders/validate
POST /api/inventory/allocate
POST /api/payments/aging
GET  /api/reports/{report_id}
```

`GET /api/reports/{report_id}` implies a two-phase flow: generate a report, hand back an ID, retrieve the file later by that ID. That shape requires persisting either the generated `.xlsx` bytes or enough state to regenerate them on demand, and an identity (a "Workflow Run") to key that storage by.

None of the business modules this API wraps have any side effects or storage today. `validate_orders`, `allocate_inventory`, `calculate_payment_aging`, and the three `export_*_report` functions in `src/report_export.py` are pure functions over DataFrames — input in, an `Output Contract`-shaped result or workbook bytes out, nothing written to disk, no IDs generated (the existing `report_id` in `ReportManifest` is a deterministic string derived from `report_type` + timestamp, not a lookup key into anything stored). Introducing persistence for Phase 10 would mean adding a job store or file store that nothing else in this project's architecture currently needs.

This was surfaced and resolved in a `/grilling` planning session before Phase 10 implementation began.

## Decision

Phase 10 introduces no persisted workflow-run identity, job store, or stored report artifact. The backend is stateless: each request is processed and forgotten once the response is sent.

- **Workflow endpoints** (`POST /api/orders/validate`, `POST /api/inventory/allocate`, `POST /api/payments/aging`) are request/response only. The client uploads source file(s) and parameters in one request; the server parses them, calls the corresponding tested Python module, and returns the JSON `Workflow Result`. Nothing is retained server-side after the response. The client may hold the result as a `Current Result` in its own page state, but the server has no concept of a "run" to revisit, cancel, or expire.
- `GET /api/reports/{report_id}` is replaced with three per-workflow **`POST .../report`** endpoints:
  ```text
  POST /api/orders/validate/report
  POST /api/inventory/allocate/report
  POST /api/payments/aging/report
  ```
  Each re-accepts the same source file(s)/parameters as its corresponding workflow endpoint and **recomputes the result server-side** — it never accepts a client-supplied `Workflow Result`/`Current Result` as authoritative report input, so a client can't hand-craft or edit JSON and get the server to notarize it into an official-looking workbook. The response is the `.xlsx` bytes directly (a `Report Artifact`), with practical download metadata (`Content-Disposition`, `X-Report-Id`, `X-Generated-At`) in headers, not a location to fetch it from later.

## Consequences

- Downloading a report after already viewing its `Workflow Result` on screen means resubmitting the source file(s) a second time — a deliberate duplicate-upload cost, acceptable at this project's demo scale (small fictional `.xlsx` files, not a high-volume production system).
- There is no way to revisit, share a link to, cancel, or audit a past run. Adding any of that later (persisted uploads/results, signed report requests, a job queue) is a new architectural decision, not an extension of this one.
- The server remains the sole source of truth for every artifact it produces — recomputing from source on every report request means a generated `.xlsx` can never diverge from what the tested Python module actually computed.
- `context/build-plan.md`'s Phase 10 endpoint list is corrected to match this decision as part of the same planning pass.
