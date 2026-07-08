# Phase 1: Python Project Foundation — AI Discussion Topics

## On TypedDict and contract design

1. "What are the trade-offs between TypedDict, dataclasses, and Pydantic for JSON-boundary contracts in a Python + FastAPI project?"
2. "TypedDict is structurally typed — two dicts with the same keys are compatible even if from different types. When does this cause problems and how do you guard against it?"
3. "Should output contracts be defined in a single `contracts.py` or co-located with the module that produces them? What are the trade-offs?"

## On error handling at module boundaries

4. "What's the difference between a technical exception (KeyError, FileNotFoundError) and a business-readable error? How do you enforce that distinction at module boundaries?"
5. "The `load_workbook()` function raises ValueError for missing columns. Should it return an error dict instead? When is raising vs returning better?"

## On the Python-first sequencing decision (ADR 0003)

6. "ADR 0003 chose Python-core-before-UI to avoid spending the first milestone on polish before the portfolio payload exists. What's the general principle here and when would you reverse it?"
7. "The Phase 8 gate is hard: every test case in three spec files must pass before any Next.js code is written. What are the risks of a hard gate like this vs a softer 'good enough' gate?"

## On testing strategy

8. "Phase 1 tests cover contracts and loading only. Why is it valuable to test the contract shape before the business rules that produce values for those contracts exist?"
9. "What's the difference between a test fixture (minimal DataFrame for a specific edge case) and a demo fixture (realistic sample workbook)? Why does this distinction matter for portfolio projects?"

## On the overall project architecture

10. "This project is a portfolio piece simulating Excel-based workflows. What makes a good portfolio project for a sales-ops / data engineering role, and how does the Python-first decision serve that?"
