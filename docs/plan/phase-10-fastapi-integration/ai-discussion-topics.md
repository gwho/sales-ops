# AI Discussion Topics — Feature phase-10-fastapi-integration: FastAPI Integration

## Data Flow & Contracts

1. Walk through exactly what happens between clicking "Run Validation" and the KPI tiles updating — every function call, every state transition, in order.
2. Why does `FormData`'s field names (`orders_file`, `product_master_file`) have to match the backend's `Annotated[UploadFile, File()]` parameter names exactly? What actually connects them?
3. What would happen if the frontend sent `orders_file` as a JSON string field instead of a real file in the `FormData`? Where would that fail, and with what error?
4. `OrderValidationResult` is a `TypedDict`, not a `BaseModel`. What's the actual mechanism (in Pydantic v2) that lets FastAPI serialize it correctly without a `BaseModel`?

## Statelessness & Recomputation

5. Why does `POST /api/inventory/allocate/report` re-run `validate_orders` internally instead of accepting the already-known valid orders from a prior `/api/inventory/allocate` call?
6. If a report endpoint accepted a client-supplied `currentResult` instead of raw files, what specific attack would become possible? Walk through it concretely.
7. What would have to change in this codebase to support "download the report I just generated 5 minutes ago" without re-uploading? What's the minimum viable version of that?

## Testing Gotchas

8. Why did `TestClient`'s default `raise_server_exceptions=True` cause the generic-500-handler test to fail with an uncaught exception instead of a clean assertion failure? What is that setting actually for?
9. If `raise_server_exceptions=False` had been the *default* client used throughout `tests/test_backend_orders.py`, would any of the happy-path tests behave differently? Why or why not?
10. The `read_xlsx_upload(file, label, loader)` design takes a business-module function as a parameter. What testing benefit (if any) does this give beyond the DRY argument in the explanation?

## Frontend State & Timing

11. Explain precisely why `setOrdersFile(file); runValidation(ordersFile, productMasterFile);` (reading state right after setting it) would be a bug, using React's actual state-update semantics.
12. The fix was extracting `runValidation(orders, productMaster)` to take explicit parameters. What's a different fix that *wouldn't* have worked, and why?
13. Why did `currentResult?.errors ?? []` trigger an ESLint warning but not a runtime bug? What's the difference between "wrong value" and "wrong reference" in this context?

## CORS & Cross-Origin Mechanics

14. What's the difference between what `allow_origins` controls and what `expose_headers` controls? Could a request succeed (status 200, correct body) while still "failing" from the frontend's perspective because of a header-exposure gap?
15. Why does a plain `<a href download>` element never need CORS configuration, while `fetch()` to the same URL does?

## Verification & Tooling

16. Why couldn't the Playwright driver script simply live in the scratchpad directory? What's the actual difference between Node's CommonJS `require` and ESM `import` resolution that caused this?
17. The verification script had one flaky assertion (`getByRole("alert").innerText()` returning empty despite the screenshot showing the correct content). What would you check first to determine whether that's a script timing bug versus a real intermittent product bug?
18. What's the argument for generating a permanent project run-skill now, versus repeating the ad-hoc `npm install --no-save playwright` setup next time verification is needed?

## Wording & Domain Consistency

19. Why did "sample template" → "sample file" need to change inside `src/excel_io.py`'s Python exception message, not just in the UI's button label? What would a user actually experience if only the UI copy had been fixed?
