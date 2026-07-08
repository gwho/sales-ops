# 06 — Coding Agent Handoff Template

Use this template when you are ready to ask a coding agent to build the UI.

---

# Project

Sales Admin Automation Toolkit

# Business Purpose

A portfolio demo showing how Python and Excel automation can support sales admin and operations workflows.

Core workflows:

1. Validate sales order Excel files
2. Allocate inventory by SKU and warehouse
3. Generate payment aging reports
4. Export clean follow-up reports

# UI Goal

The UI should look like a professional B2B internal operations dashboard, not a generic AI-generated dashboard.

# Visual Direction

- Light theme first
- White / slate / soft gray / blue palette
- Businesslike typography
- Compact cards
- Clear data tables
- Status badges
- Minimal charts
- Strong empty/loading/error states

# Screens

1. Overview Dashboard
2. Order Validation
3. Inventory Allocation
4. Payment Aging
5. Reports / Export Center

# Components

```text
SidebarNav
TopBar
KpiCard
WorkflowStepper
UploadPanel
RequiredColumnsChecklist
StatusBadge
DataTable
ValidationErrorTable
AllocationResultTable
PaymentAgingTable
ReportExportCard
EmptyState
LoadingState
ErrorState
ExportButton
```

# Implementation preference

## V1

Streamlit + Python business logic.

## V2

Next.js + TypeScript + Tailwind + shadcn/ui frontend, connected later to FastAPI backend.

# Important constraints

- Do not build a full ERP.
- Do not add authentication in V1.
- Do not overcomplicate database persistence in V1.
- Use mock/sample data first for UI.
- Keep business language clear for hiring managers.
- Prioritize order validation, allocation, payment aging, and report export.

# Output expected from coding agent

Before coding, produce:

1. Final UI component list
2. Route/page structure
3. Mock data schema
4. Page-by-page layout
5. UI acceptance criteria
6. Implementation tasks
7. What to build in V1 vs V2

After approval, generate code incrementally.
