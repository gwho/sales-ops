# Mission: Sales Admin Automation Toolkit — Full-Stack Mastery From First Principles

## Why

This project was built across 12 phases with heavy AI-assisted development. The learner wants genuine ownership of it, not a guided tour: the ability to explain and defend every architecture decision in a technical interview, the ability to extract its reusable engineering patterns (phased sequencing, ADR discipline, contract-first design) for future projects, and enough depth to safely extend it (Phase 13+) without an AI agent re-deriving context from scratch every session.

Critically: the learner does **not** yet know Python, pandas, pytest, FastAPI, React, Next.js, TypeScript, SQL, Postgres, deployment mechanics, or general software architecture patterns. This repo is being used as the *trigger* for learning all of those — every underlying concept must be taught before (or alongside) the real file that uses it, never assumed.

## Success looks like

- Can explain, from memory and without notes, why Python business logic was built before any UI (ADR 0003), and defend that trade-off to a skeptical interviewer.
- Can trace a single order from Excel upload through validation → allocation → aging → dashboard, naming every module boundary and output contract it crosses, and explaining *in plain language* what each underlying technology (pandas, FastAPI, Postgres, Next.js) is doing at that step.
- Can draft a new ADR-worthy decision for a hypothetical Phase 13 feature using the repo's own three-part ADR-worthiness test, unassisted.
- Can reproduce, in a brand-new project, the RSC/Client Component boundary rule, the statelessness-by-default pattern, and the "best-effort, never-silent" persistence pattern this repo uses — and explain *why* each exists, not just *that* it exists.
- Can independently extend the codebase (e.g. a 4th workflow) respecting Field Scope Boundary, Scope Gate, and the existing module boundaries, without an agent re-explaining them first.
- Can hold a basic conversation about each underlying technology (what pandas/pytest/FastAPI/React/Postgres/CORS/deployment *are*, generically) independent of this repo — the repo is the vehicle, not the ceiling.

## Constraints

- **Zero assumed prior knowledge** of: Python, pandas, pytest, uv, FastAPI, HTTP/REST, React, Next.js/App Router, TypeScript, SQL, Postgres, deployment/CORS/env vars, or software architecture vocabulary (ADR, statelessness, contracts, etc.). Every module must teach the prerequisite concept before tying it to the real file.
- Learner is the sole author/maintainer of this repo — teaching can assume full read access to the real ADRs, docs, and code; the genuine artifacts are the curriculum, not synthetic stand-ins.
- Wants **concept-first** sequencing with the 12 build phases used as *case studies*, not as the syllabus itself — module order will diverge from phase-number order whenever a concept is better taught by a different phase's example.
- Wants durable understanding (storage strength) over speed or the feeling of fluency — retrieval practice (recall, trace, rebuild, explain) is a first-class part of the plan, not an afterthought.

## Out of scope (for now)

- The paused/superseded SQLite reporting design (`docs/archive/`) — historical reference only.
- The excluded V1.5/V2/CRM-Cleaner spec scope — deliberately out of bounds per the repo's own Scope Gate; not a learning target unless the learner chooses to implement it later.
- Deep computer-science theory beyond what's needed to understand this repo's choices (e.g. full algorithms coursework) — teach only the slice a given file actually uses (e.g. "greedy allocation by priority," not general graph theory).
