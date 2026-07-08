# 08 — UI Grilling Questions for Coding Agents

Use these questions before asking a coding agent to implement the UI.

## Strategic UI questions

1. Should this project use Streamlit first or Next.js first?
2. What is the smallest UI that still looks professional?
3. Which UI elements are necessary for a hiring manager demo?
4. Which UI elements are unnecessary overbuilding?
5. How can the UI make the business logic easy to explain?
6. How can the UI avoid looking like a generic tutorial dashboard?

## Framework questions

1. If using Next.js, should I use shadcn/ui or MUI Data Grid?
2. Should tables use TanStack Table or MUI Data Grid?
3. Should API state use TanStack Query, Zustand, Redux Toolkit, or local state?
4. Is Redux overkill for this project?
5. How can I keep Python as the business logic layer while using React for UI?
6. What is the best deployment split for frontend and backend?

## Design questions

1. What visual style best fits a sales admin / operations dashboard?
2. What colors should be used for statuses?
3. How many KPI cards should the dashboard show?
4. What charts are actually useful?
5. How can tables be made readable and not overwhelming?
6. What empty states should be included?
7. What loading states should be included?

## Page-level questions

1. What should the Overview page show before any files are uploaded?
2. What should the Order Validation page show after errors are found?
3. How should the Inventory Allocation page separate allocated orders and backorders?
4. How should the Payment Aging page prioritize follow-up actions?
5. What should the Reports page contain?
6. Should the CRM Cleaner be included in V1 or delayed?

## Agent implementation questions

1. Can you first build a static UI using mock data only?
2. Can you keep all business logic out of the frontend?
3. Can you define TypeScript interfaces matching the backend responses?
4. Can you add loading, error, and empty states for every page?
5. Can you create reusable components instead of page-specific duplicated UI?
6. Can you make the UI responsive but not overcomplicate mobile design?

## Review questions

1. Does this look like a professional internal business tool?
2. Would a non-technical hiring manager understand the value?
3. Would an operations manager trust this report output?
4. Is the project scope still small enough to finish?
5. Is the UI hiding or revealing the useful business rules?
6. What should be cut before implementation?

## Final agent prompt

```text
Review the UI specs for Sales Admin Automation Toolkit.
Before coding, challenge the design.
Tell me:
1. What UI elements are essential?
2. What UI elements are overkill?
3. Should I use Streamlit, Next.js, or both in phases?
4. What is the fastest impressive version?
5. What component structure should I use?
6. What should be mocked first?
7. What should connect to the Python backend later?
8. What acceptance criteria should I use to judge the UI?
```
