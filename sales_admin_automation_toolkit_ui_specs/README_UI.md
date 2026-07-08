# Sales Admin Automation Toolkit — UI Specification Pack

This UI specification pack extends the existing functional specs for the **Sales Admin Automation Toolkit**.

The purpose is to help coding agents design a demo that feels professional, business-friendly, and impressive to a hiring manager, while still keeping the project small enough to finish.

## Recommended UI strategy

The project can be built in two UI levels:

### V1: Streamlit UI
Fastest route. Best for proving the business logic works.

Use when the priority is to quickly demonstrate:
- Excel upload
- order validation
- inventory allocation
- payment aging
- downloadable reports

### V2: React / Next.js UI
More polished route. Best for portfolio presentation and future-proofing.

Use when the priority is to demonstrate:
- modern dashboard UI
- reusable components
- superior state management
- agent-friendly UI scaffolding
- professional SaaS-style presentation

## Recommended decision

Build the backend/business logic first in Python. Then choose one of these UI options:

1. **Fast demo path:** Streamlit + Python modules.
2. **Portfolio polish path:** Next.js frontend + FastAPI backend.

Do not let UI polish delay the core business logic. The most valuable part of the project is still the sales/admin automation logic.

## Files in this pack

- `01_ui_strategy_streamlit_vs_nextjs.md`
- `02_professional_dashboard_ui_elements.md`
- `03_page_by_page_ui_spec.md`
- `04_react_nextjs_component_spec.md`
- `05_state_management_and_data_flow.md`
- `06_agentic_ui_workflow.md`
- `07_ui_acceptance_criteria.md`
- `08_ui_grilling_questions_for_agents.md`
