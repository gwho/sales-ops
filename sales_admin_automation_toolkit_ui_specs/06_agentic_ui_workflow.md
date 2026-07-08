# 06 — Agentic UI Workflow

## Purpose

This file gives instructions for using coding agents to create a professional UI without losing control of the business scope.

## Recommended agentic workflow

Use this loop:

```text
Spec → Generate → Review → Refine → Test → Explain
```

## Step 1 — Ask for UI direction first

Prompt:

```text
Act as a senior B2B SaaS product designer.
I am building a Sales Admin Automation Toolkit for order validation, inventory allocation, and payment aging.
Suggest a professional dashboard UI direction suitable for a sales admin / operations portfolio project.
Do not write code yet.
Define the visual style, layout, key pages, reusable components, and user flow.
```

## Step 2 — Ask for wireframe-level plan

Prompt:

```text
Create a wireframe specification for the toolkit.
Include:
- overview dashboard
- order validation page
- inventory allocation page
- payment aging page
- reports page
For each page, define layout sections, components, table columns, empty states, and user actions.
```

## Step 3 — Ask for component list

Prompt:

```text
Convert the wireframe into a React component plan.
Use Next.js, TypeScript, Tailwind, shadcn/ui, TanStack Table, and Recharts.
List all components, props, folder structure, and acceptance criteria.
Do not implement yet.
```

## Step 4 — Ask for design tokens

Prompt:

```text
Create a lightweight design system for this B2B operations dashboard.
Include colors, typography, spacing, card radius, table style, status badge colors, and chart style.
Make it professional and restrained.
```

## Step 5 — Ask for a static mockup first

Prompt:

```text
Generate a static frontend mockup using mock data only.
Do not connect to the backend yet.
Implement the dashboard, order validation table, allocation table, payment aging table, and reports page.
Use mock JSON data.
```

## Step 6 — Ask for backend integration after static UI works

Prompt:

```text
Now replace mock data with API calls to the FastAPI backend.
Use TanStack Query for upload mutations and result fetching.
Keep all UI states: idle, loading, success, error, and empty.
```

## Step 7 — Ask for UI review

Prompt:

```text
Review this UI like a hiring manager and a senior product designer.
Tell me:
1. what looks professional
2. what looks amateur
3. what is confusing
4. what should be simplified
5. what is impressive for a sales admin / operations role
6. what should be removed to avoid overbuilding
```

## Figma / v0 / shadcn workflow

### Option A — v0 / shadcn-first

Use v0 or an LLM to generate a polished dashboard screen, then adapt it manually.

Good for:

- fast visual scaffolding
- modern dashboard cards
- tables
- empty states

### Option B — Figma-first

Create simple Figma frames before coding.

Good for:

- layout planning
- portfolio screenshots
- design-to-code discussion

### Option C — Screenshot inspiration

Collect 3-5 screenshots of clean B2B dashboards and ask the agent to extract patterns.

Prompt:

```text
Analyze these dashboard references.
Extract reusable UI patterns for my Sales Admin Automation Toolkit.
Do not copy the design exactly.
Suggest layout, spacing, table style, and component ideas.
```

## Guardrails for coding agents

Tell the agent:

```text
Do not add authentication.
Do not add complex database workflows.
Do not build a full ERP system.
Do not add AI prediction features.
Do not change the Python business rules without asking.
Focus on making the existing workflow clear and polished.
```

## UI success standard

The UI is successful if a hiring manager can open it and understand:

1. what problem it solves
2. what files to upload
3. what errors were found
4. what stock was allocated
5. which payments need follow-up
6. what report can be downloaded
