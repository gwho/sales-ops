# UI Reference → Figma → Coding Agent Workflow

## Purpose

This workflow helps turn visual dashboard references into a professional UI direction for the **Sales Admin Automation Toolkit** without requiring deep Figma/design knowledge.

The goal is not to copy screenshots. The goal is to use screenshots as **visual references**, then translate them into a practical UI plan that coding agents can implement.

## Short answer

You can paste screenshots into Figma, but you should not expect Figma to automatically produce perfect wireframes by itself.

A realistic workflow is:

1. Collect UI screenshots.
2. Paste them into Figma as a reference board.
3. Annotate what you like and dislike.
4. Ask an AI/design agent to generate a wireframe or component plan.
5. Clean up the wireframe manually or with AI prompts.
6. Give the resulting screen structure to coding agents.
7. Build with Streamlit, or with Next.js + Tailwind + shadcn/ui for a more polished version.

## Important distinction

| Action | What it gives you | Risk |
|---|---|---|
| Paste screenshot into Figma | A static image reference | Not editable by default |
| Screenshot-to-Figma plugin/tool | Editable layers, sometimes | Output may be messy |
| Figma AI / Figma Make prompt | Generated wireframe/prototype | May look generic without guidance |
| Manual low-fi wireframe | Clear structure | Requires some time |
| Coding agent from screenshot only | Fast draft UI | Can miss details or create inconsistent layout |

## Recommended approach for this project

Use Figma as a **reference board and wireframe container**, not as a full professional design system.

For the Sales Admin Automation Toolkit, create these Figma pages:

1. `01_UI_References`
2. `02_Annotated_References`
3. `03_Low_Fidelity_Wireframes`
4. `04_Component_Sheet`
5. `05_Final_UI_Direction`
6. `06_Coding_Agent_Handoff`

## Screen set to design

Only design the screens that matter for the hiring-manager demo:

1. Overview Dashboard
2. Order Validation
3. Inventory Allocation
4. Payment Aging
5. Reports / Export Center

Optional:

6. CRM Cleaner
7. Settings / Business Rules

## Recommended UI style

- Clean B2B SaaS dashboard
- Light theme first
- Sidebar navigation
- Professional data tables
- KPI cards
- Status badges
- File upload panels
- Workflow stepper
- Report export cards
- Clear empty/loading/error states

Avoid:

- Neon AI dashboard look
- Crypto-style dark gradients
- Too many charts
- Overly complex ERP navigation
- Generic AI-generated purple/blue cards
- Fake metrics that do not connect to the business logic

## Recommended implementation stack

### V1 Practical Demo

- Python
- Pandas
- openpyxl
- Streamlit
- pytest

### V2 Polished UI Demo

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Table or MUI Data Grid
- Recharts
- TanStack Query
- FastAPI backend

## Final output expected from this workflow

By the end, you should have:

- 5 UI reference screenshots
- 5 annotated notes explaining what to borrow
- 5 low-fidelity wireframes
- 1 component list
- 1 page-by-page UI spec
- 1 coding-agent implementation prompt
- optional Figma link or screenshot export for coding agents


## Added: Figma MCP design-to-code workflow

Additional draft files were added for the possible Figma MCP path:

- `08_figma_mcp_design_to_code_requirements.md`
- `09_coding_agent_mcp_checklist.md`

These files are **not final implementation requirements**. They are prompts/checklists to discuss with coding agents before deciding whether to implement the polished UI with Next.js, Tailwind, shadcn/ui, MUI Data Grid, or another stack.

Use them when you have a Figma Make / Figma design URL and want the coding agent to inspect the design, map it to reusable components, and propose a safe implementation plan before generating code.
