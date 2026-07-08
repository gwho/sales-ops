# 02 — Figma Reference Board Workflow

## Goal

Use Figma as a lightweight visual thinking board, not as a full design system.

## Can I just paste screenshots into Figma?

Yes, but with an important limitation: a pasted screenshot is usually just a static image. It does not automatically become a clean editable wireframe.

To make it useful, you should annotate it and extract the design pattern manually or with AI help.

## Figma file structure

Create one Figma file named:

```text
Sales Admin Automation Toolkit UI Planning
```

Create these pages:

```text
01_UI_References
02_Annotated_References
03_Low_Fidelity_Wireframes
04_Component_Sheet
05_Final_UI_Direction
06_Coding_Agent_Handoff
```

## Page 1: UI References

Paste the 5 best screenshots.

Group them by purpose:

```text
Dashboard overview
Upload / import flow
Data table style
Status badges
Reports / export center
```

## Page 2: Annotated References

Next to each screenshot, add notes:

```text
What I like:
- compact KPI card layout
- clear sidebar navigation
- good table spacing
- readable status badges
- professional light theme

What I do not want:
- too many gradients
- too many decorative charts
- unclear buttons
- generic AI dashboard look
```

## Page 3: Low-Fidelity Wireframes

Create simple gray-box wireframes for:

1. Overview Dashboard
2. Order Validation
3. Inventory Allocation
4. Payment Aging
5. Reports / Export Center

Use rectangles, text labels, and simple table placeholders. Do not worry about perfect design.

## Page 4: Component Sheet

Create a simple component inventory:

```text
SidebarNav
TopBar
KpiCard
UploadPanel
WorkflowStepper
StatusBadge
DataTable
ErrorSummaryCard
AllocationResultTable
PaymentAgingTable
ReportExportCard
EmptyState
LoadingState
```

## Page 5: Final UI Direction

Write a short design brief:

```text
The app should look like a clean B2B internal operations dashboard.
It should feel suitable for sales admin, supply chain, trading, and IT consulting workflows.
The design should be practical, table-heavy, and business-readable.
```

## Page 6: Coding Agent Handoff

Put final screenshots or wireframes here with notes such as:

```text
Implement this as Next.js + Tailwind + shadcn/ui.
Use this layout as inspiration only.
Do not copy exact visual assets.
Prioritize clarity, readable tables, and business workflow.
```

## Final deliverable from this step

A Figma reference board that can be shared with a coding agent as visual context.
