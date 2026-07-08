# 05 — Agent Prompts for UI Planning

## Prompt 1: Analyze references

```text
I am building a portfolio project called Sales Admin Automation Toolkit.

I have collected several dashboard UI screenshots as references.
Please analyze them as visual inspiration only. Do not copy them exactly.

My app workflows:
- order validation
- inventory allocation
- payment aging
- report export

Please identify:
1. reusable layout patterns
2. useful table patterns
3. useful card patterns
4. good status badge styles
5. good upload/report patterns
6. what to avoid
7. how to adapt the references into a unique B2B operations dashboard
```

## Prompt 2: Create UI direction

```text
Act as a senior B2B SaaS product designer.

Create a UI direction for Sales Admin Automation Toolkit.

Requirements:
- professional internal operations dashboard
- light theme first
- sidebar navigation
- KPI cards
- data tables
- status badges
- Excel upload workflow
- report export center
- clear empty/loading/error states
- not generic AI dashboard
- not overdesigned

Please produce:
1. visual style summary
2. layout system
3. component list
4. page-by-page UI plan
5. design tokens
6. accessibility notes
```

## Prompt 3: Convert wireframes to component plan

```text
Here are my low-fidelity wireframes for Sales Admin Automation Toolkit.

Please convert them into a Next.js + Tailwind + shadcn/ui component plan.

For each screen, define:
- route path
- components
- props
- data needed
- loading state
- empty state
- error state
- responsive behavior
- acceptance criteria

Do not write code yet.
```

## Prompt 4: Streamlit version from UI spec

```text
I want to implement V1 in Streamlit but keep the UI professional.

Using this UI spec, suggest how to approximate the layout in Streamlit.

Include:
- page layout
- sidebar navigation
- KPI cards
- upload sections
- tables
- status badges
- charts
- export buttons
- custom CSS if necessary
- limitations compared with Next.js
```

## Prompt 5: Next.js polished version

```text
Implement the V2 UI as a polished Next.js frontend.

Stack:
- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Table or MUI Data Grid
- Recharts
- TanStack Query

Use mock data first. Do not connect to backend yet.

Build these pages:
- Overview
- Order Validation
- Inventory Allocation
- Payment Aging
- Reports

Focus on professional B2B SaaS visual quality and readable tables.
```
