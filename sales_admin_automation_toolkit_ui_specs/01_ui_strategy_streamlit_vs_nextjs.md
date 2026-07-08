# 01 — UI Strategy: Streamlit vs React / Next.js

## Project context

The Sales Admin Automation Toolkit has three core demos:

1. Order Entry Validation Tool
2. Inventory Allocation Mini Engine
3. Payment Aging Report Generator

Optional extension:

4. CRM Data Cleaner

The project should demonstrate that Python and Excel automation can improve daily sales admin and operations workflows without pretending to be a full ERP system.

## UI goal

The UI should make the demo feel:

- professional
- business-friendly
- easy to understand by non-technical hiring managers
- credible for sales admin / operations roles
- polished enough for a portfolio
- simple enough to finish

## Option A — Streamlit-first UI

### Best for

- Fastest build
- Python-only implementation
- Excel upload/download
- quick interview demo
- business logic demonstration

### Strengths

- Very fast to build with coding agents
- Uses Python directly
- Easy to connect to Pandas and openpyxl
- Minimal frontend complexity
- Good for showing practical operations automation

### Weaknesses

- Less polished than a custom React dashboard
- Less flexible visual design
- Some hiring managers may see it as a data demo rather than a full web app
- State management is simpler but less scalable

### Recommended Streamlit UI structure

- Sidebar navigation
- Overview dashboard
- Upload panel
- Validation results table
- Allocation results table
- Payment aging table
- Download report buttons
- Simple KPI cards

## Option B — React / Next.js UI with Python backend

### Best for

- Polished portfolio presentation
- Modern web development impression
- Future-proofing stack
- Agentic UI scaffolding
- reusable component architecture
- stronger developer-style portfolio

### Strengths

- Modern SaaS dashboard look
- Better control of layout, animation, states, and tables
- Stronger UI component system
- Can use shadcn/ui, Tailwind, TanStack Table, Recharts
- Easier to present as a professional product demo

### Weaknesses

- More moving parts
- Requires API layer, frontend/backend integration, deployment complexity
- Can distract from core business logic
- More risk of overbuilding

### Recommended Next.js architecture

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Table or MUI Data Grid
- Recharts
- Zustand or TanStack Query for state/data fetching
- FastAPI backend
- Python business logic modules

## Recommended path

### V1

Build with Python logic first.

Possible UI:

- Streamlit for the first working demo
- or a very thin Next.js frontend if you strongly want a modern UI from the beginning

### V2

Build a polished Next.js frontend using the same Python backend logic.

### Do not do in V1

- authentication
- role-based permissions
- full database persistence
- complex deployment
- real customer data
- full ERP workflow
- advanced AI predictions

## Final recommendation

Use this principle:

> Business logic first. UI polish second. Deployment third.

A professional-looking UI helps, but the hiring manager should mainly understand that the tool solves real daily operations problems.
