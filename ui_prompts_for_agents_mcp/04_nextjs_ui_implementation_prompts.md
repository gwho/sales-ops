# 04 — Next.js UI Implementation Prompts

Use these prompts after the design direction is approved.

---

## Next.js Frontend Scaffold Prompt

```text
Create a Next.js frontend scaffold for Sales Admin Automation Toolkit.

Use:
- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts
- TanStack Table or MUI Data Grid
- mock data first

Pages:
1. /dashboard
2. /order-validation
3. /inventory-allocation
4. /payment-aging
5. /reports

Global layout:
- left sidebar navigation
- top header
- responsive main content area
- light theme first

Do not connect to backend yet. Use local mock data and static interactions first.
```

---

## Component Implementation Prompt

```text
Implement reusable UI components for Sales Admin Automation Toolkit.

Components:
- AppShell
- SidebarNav
- TopHeader
- MetricCard
- StatusBadge
- WorkflowStepper
- UploadPanel
- DataTable
- FilterBar
- AlertPanel
- ReportCard
- ExportButton
- EmptyState
- LoadingState
- ErrorState

Each component should be reusable, typed with TypeScript, and styled with Tailwind/shadcn conventions.
Use realistic business labels and avoid generic placeholder text.
```

---

## Mock Data Prompt

```text
Create realistic mock data for the Sales Admin Automation Toolkit UI.

Mock data should include:
- sales orders with valid and invalid entries
- product/SKU master
- inventory by warehouse
- allocation results
- backorders
- supplier follow-up items
- invoices and payment aging buckets
- report export history

Use fictional company/customer/supplier names only.
Data should support the dashboard cards, charts, tables, and status badges.
```

---

## UI-to-Python Integration Planning Prompt

```text
The UI currently uses mock data.

Please prepare a future integration plan for connecting it to Python logic or FastAPI endpoints.

For each page, define:
- current mock data source
- future API endpoint or Python function
- request shape
- response shape
- loading state
- error handling
- export/download behavior

Do not implement backend integration yet unless I ask.
```

---

## Streamlit vs Next.js Decision Prompt

```text
Compare two UI implementation paths for Sales Admin Automation Toolkit:

A. Streamlit + Python only
B. Next.js + Python/FastAPI backend

Evaluate by:
- speed to finish
- visual polish
- hiring manager impression
- coding-agent friendliness
- future portfolio value
- complexity risk
- how easy it is to connect Excel workflows

Recommend what to build as V1 and what to postpone to V2.
```
