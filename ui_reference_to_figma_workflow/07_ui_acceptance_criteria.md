# 07 — UI Acceptance Criteria

## Global UI

- The app uses a clean professional B2B dashboard style.
- Navigation is clear and limited to core workflows.
- Tables are readable and not overcrowded.
- Status badges are consistent across pages.
- Primary actions are visually obvious.
- The app should not look like a generic AI-generated dashboard.

## Overview Dashboard

- Shows at least 5 KPI cards.
- Shows a workflow summary: Upload → Validate → Allocate → Review Payments → Export.
- Shows recent issues requiring follow-up.
- Shows at least one chart or visual summary.
- Makes the business value clear within 10 seconds.

## Order Validation

- Shows upload panel with accepted file type.
- Shows required columns checklist.
- Shows validation summary after upload.
- Shows error table with row number, issue type, and suggested action.
- Shows valid orders preview.
- Export button is disabled until validation is complete.

## Inventory Allocation

- Shows allocation rules clearly.
- Shows allocation results table.
- Uses consistent status badges.
- Shows remaining inventory.
- Shows backorder/supplier follow-up list.
- Export button is disabled until allocation is complete.

## Payment Aging

- Shows aging bucket summary.
- Shows overdue invoice table.
- Shows high-priority follow-up badge.
- Shows draft follow-up reminder or suggested action.
- Export button is disabled until report is generated.

## Reports

- Shows report cards for each available report.
- Each card explains what is included.
- Download buttons are clear.
- Shows generated time or report status.

## Empty States

- Empty pages explain what the user should do next.
- No page should look broken before file upload.

## Loading States

- Upload and processing actions show progress or loading feedback.
- Buttons should not allow duplicate processing while loading.

## Error States

- Error messages use business language.
- Avoid raw Python/JavaScript stack traces in UI.
- Error state should suggest a next action.

## Responsive Behavior

- Desktop layout is primary.
- Tablet layout should remain usable.
- Mobile can be simplified, but should not break.
