# 08 — Figma MCP Design-to-Code Requirements

Status: **Draft / not final**. Use this file to discuss and refine the workflow with coding agents before implementation.

## Purpose

This project may use **Figma Make / Figma design files + Figma MCP** to help coding agents transform approved UI designs into frontend code.

The goal is not to blindly convert a screenshot into code. The goal is to give the coding agent structured design context so it can generate a more professional UI for the **Sales Admin Automation Toolkit**.

Target project UI:

- Overview Dashboard
- Order Validation
- Inventory Allocation
- Payment Aging
- Reports / Export Center

Target frontend stack, if using the polished V2 path:

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui or MUI Data Grid
- TanStack Table or MUI Data Grid
- Recharts
- FastAPI backend later, or mock data first

## Why Figma MCP is useful

Figma MCP can help coding agents access structured design context from Figma files, such as components, variables, layout data, and design details. This should produce more design-informed code than asking an agent to recreate a UI from a screenshot alone.

However, MCP is an aid, not a replacement for product decisions. The coding agent must still confirm:

- which screen is being implemented
- which components are reusable
- which parts are static mock data
- which parts connect to backend APIs later
- whether the generated code matches the project’s business workflow

## Key rule

Do not let the agent implement the design blindly.

Before coding, the agent must first produce:

1. screen inventory
2. component inventory
3. component-to-code mapping
4. data requirements
5. interaction list
6. implementation plan
7. risks / missing design details

Only after review should it generate code.

## Required MCP / agent preparation

Ask the coding agent to confirm:

- whether it has access to the Figma MCP server
- whether it can read the specific Figma file or Figma Make output
- whether it can access frames, components, variables, colors, spacing, and layout metadata
- whether it can use any project-specific coding skills or MCP tools
- whether it can inspect the existing codebase before generating UI code
- whether it should use screenshot interpretation, Figma MCP, or both

## Required coding-agent instruction

Use this instruction when handing off a Figma design:

```text
You have access to a Figma design or Figma Make output for the Sales Admin Automation Toolkit.

Do not immediately generate code.

First inspect the design and produce:
1. list of screens/frames found
2. list of reusable UI components
3. mapping from Figma components to React components
4. design tokens detected or recommended
5. data needed by each screen
6. interactions needed by each screen
7. responsive layout assumptions
8. accessibility concerns
9. missing design details or ambiguities
10. recommended implementation sequence

After I approve the plan, implement the UI using Next.js, TypeScript, Tailwind CSS, and shadcn/ui or MUI Data Grid.
```

## Component mapping requirements

The agent should map Figma UI elements into code components like this:

| Figma / UI Element | Suggested React Component |
|---|---|
| Sidebar navigation | `SidebarNav` |
| Top header | `TopHeader` |
| KPI card | `MetricCard` |
| Upload area | `UploadPanel` |
| Workflow stepper | `WorkflowStepper` |
| Status badge | `StatusBadge` |
| Data table | `DataTable` / `ValidationErrorTable` / `AllocationTable` / `PaymentAgingTable` |
| Chart card | `ChartCard` |
| Alert panel | `FollowUpAlertPanel` |
| Report card | `ReportCard` |
| Empty state | `EmptyState` |
| Loading state | `LoadingState` |
| Error message | `BusinessErrorMessage` |

## Screen requirements

### Overview Dashboard

Must include:

- KPI cards
- order status chart
- payment aging chart
- follow-up alerts
- recent report/export status

### Order Validation

Must include:

- Excel upload panel
- required columns checklist
- validation summary
- error table
- export validation report button

### Inventory Allocation

Must include:

- allocation KPI cards
- filters
- allocation result table
- remaining inventory table
- supplier follow-up panel

### Payment Aging

Must include:

- upload/payment data area
- aging bucket cards
- overdue invoice table
- priority badges
- draft reminder preview

### Reports / Export Center

Must include:

- report cards
- recent export history
- download full operations report button

## Design-to-code acceptance criteria

The generated UI should:

- preserve the professional B2B SaaS look
- use consistent spacing and typography
- use reusable components, not one giant page file
- use realistic mock data before backend integration
- use business-readable labels and messages
- avoid random AI-generated text or unrealistic metrics
- support empty, loading, success, warning, and error states
- be responsive enough for desktop and tablet
- be easy to connect to Python/FastAPI endpoints later

## Things the agent must not do

- Do not copy random screenshot text that is irrelevant to this project.
- Do not create crypto-style, neon, consumer-app, or overly flashy UI.
- Do not add login, permissions, or complex ERP features in V1.
- Do not connect to real customer/order data.
- Do not claim production readiness.
- Do not build backend logic before confirming the UI/API data contract.

## Recommended implementation sequence

1. Inspect Figma / MCP context.
2. Extract screen list and component list.
3. Create UI implementation plan.
4. Implement static mock-data frontend.
5. Add responsive layout and states.
6. Add table sorting/filtering if simple.
7. Connect to local mock JSON or simple API adapter.
8. Later connect to Python/FastAPI backend.
9. Add screenshots to README.
10. Add interview/demo notes.
