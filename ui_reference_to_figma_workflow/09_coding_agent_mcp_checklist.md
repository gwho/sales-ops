# 09 — Coding Agent MCP Checklist

Status: **Draft / not final**. Use this as a checklist before asking a coding agent to implement Figma-generated UI.

## 1. Access check

Ask the agent:

```text
Can you access the Figma design through Figma MCP or another design context tool?
If yes, tell me exactly what you can inspect: frames, components, colors, layout, variables, text, assets, or only screenshots.
If no, tell me what screenshots or exported assets you need.
```

## 2. Skill/tool check

Ask the agent:

```text
Before coding, confirm which tools or skills you can use:
- Figma MCP / design context access
- codebase search
- file editing
- terminal commands
- Next.js knowledge
- Tailwind/shadcn component generation
- TypeScript lint/build
- test runner

If a tool is unavailable, propose a fallback workflow.
```

## 3. Design extraction check

Ask:

```text
Inspect the Figma design and summarize:
1. all frames/screens
2. all reusable components
3. colors and typography
4. spacing/layout conventions
5. tables and columns
6. states: empty/loading/error/success
7. interactions
8. missing details

Do not write code yet.
```

## 4. Business fit check

Ask:

```text
Evaluate whether this Figma design fits the Sales Admin Automation Toolkit business workflow:
- order validation
- inventory allocation
- payment aging
- reports/export

Point out any UI elements that look generic, irrelevant, too complex, or disconnected from sales admin / operations work.
```

## 5. Component mapping check

Ask:

```text
Map the design into React components.
For each component, provide:
- component name
- props
- child components
- mock data needed
- which page uses it
- whether it should be reusable
```

Suggested component names:

```text
SidebarNav
TopHeader
MetricCard
WorkflowStepper
UploadPanel
StatusBadge
DataTable
ValidationErrorTable
AllocationResultTable
PaymentAgingTable
ReportCard
ExportButton
EmptyState
LoadingState
BusinessErrorMessage
```

## 6. Frontend stack decision

Ask:

```text
Given this design, should the UI be implemented first in:
A. Streamlit
B. Next.js + Tailwind + shadcn/ui
C. Next.js + MUI Data Grid
D. hybrid approach with Streamlit V1 and Next.js V2

Evaluate by speed, UI quality, difficulty, agent-friendliness, and interview value.
```

## 7. Data contract check

Ask:

```text
For each screen, define the data contract needed from the backend or mock data.
Use TypeScript interfaces first.
Do not assume backend implementation yet.
```

Example:

```ts
interface ValidationErrorRow {
  rowNumber: number;
  orderId: string;
  field: string;
  issueType: string;
  currentValue: string;
  suggestedFix: string;
  severity: 'warning' | 'critical';
}
```

## 8. Implementation sequencing check

Ask:

```text
Create a safe implementation sequence:
1. scaffold Next.js project
2. install UI dependencies
3. create layout shell
4. create reusable components
5. implement pages with mock data
6. add tables and status badges
7. add upload UI only, no backend first
8. add API adapter layer
9. connect to Python/FastAPI later
10. polish README screenshots
```

## 9. Anti-overbuilding check

Ask:

```text
Identify anything in the design or implementation plan that may overbuild the project.
Classify items as:
- keep for V1
- simplify for V1
- postpone to V2
- remove
```

Likely postpone:

- authentication
- multi-user roles
- full database persistence
- real-time collaboration
- complex charts
- AWS deployment
- AI risk scoring

## 10. Final agent handoff prompt

Use this when ready:

```text
You are implementing the UI for Sales Admin Automation Toolkit.

Use the Figma design as a visual and structural reference through MCP if available.
Do not copy irrelevant text or overbuild.

Implement only the approved V1/V2 UI scope:
- Overview Dashboard
- Order Validation
- Inventory Allocation
- Payment Aging
- Reports / Export Center

Use mock data first.
Keep business logic separate and API-ready.
Create reusable components.
Use TypeScript interfaces for all data.
Add empty/loading/error states.
Make the UI look professional for a hiring-manager portfolio demo.

Before each implementation step, tell me which file you will create or modify and why.
```
