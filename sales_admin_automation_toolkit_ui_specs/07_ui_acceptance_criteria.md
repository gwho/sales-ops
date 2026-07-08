# 07 — UI Acceptance Criteria

## Global UI criteria

- The app must look like a professional internal operations dashboard.
- The user should understand the app purpose within 10 seconds.
- The UI must use consistent spacing, typography, status badges, and table styling.
- The app must clearly show that it uses fictional sample data.
- All technical errors must be converted into business-readable messages.
- All pages must have empty states.
- All processing actions must have loading states.
- All generated reports must have clear download buttons.

## Navigation criteria

- Sidebar or top navigation must include:
  - Overview
  - Order Validation
  - Inventory Allocation
  - Payment Aging
  - Reports
  - Optional CRM Cleaner
- Current page must be visually highlighted.
- Navigation labels must use business language, not developer language.

## Dashboard criteria

- Dashboard must show at least 5 KPI cards.
- Dashboard must show a workflow stepper or process overview.
- Dashboard must show at least 1 chart after data is processed.
- Dashboard must have a clear empty state before upload.

## Upload criteria

- Upload panel must show accepted file type.
- Upload panel must show required columns.
- Upload panel must allow sample template download or reference.
- Upload button must be disabled while processing.
- Upload errors must be business-readable.

## Order validation criteria

- Validation result must show summary counts.
- Error rows must show issue type and issue message.
- Valid rows and invalid rows must be visually distinguishable.
- User must be able to download validation report.

## Inventory allocation criteria

- Allocation result must show fully allocated, partial, and backordered statuses.
- Backorders must be clearly separated.
- Remaining inventory must be visible or downloadable.
- Allocation rules must be visible on the page.

## Payment aging criteria

- Payment aging buckets must be visually clear.
- High-priority overdue invoices must be highlighted.
- User must see suggested follow-up action.
- User must be able to download payment aging report.

## Reports criteria

- Report center must show all available reports.
- Disabled download buttons must explain why they are disabled.
- Each report card must describe what the report contains.

## Accessibility criteria

- Text contrast must be readable.
- Buttons must have clear labels.
- Status cannot rely on color only; use text labels too.
- Tables must have visible column headers.
- Keyboard navigation should work for main actions where possible.

## Portfolio criteria

- README screenshots should include:
  - overview dashboard
  - validation result
  - allocation result
  - payment aging result
  - exported report example
- The app should include a short “About this demo” section.
- The app should not claim production use.
- The app should not use real employer/client data.
