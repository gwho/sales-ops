---
description: Instructions building apps with MCP
globs: *
alwaysApply: true
---

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.

<!-- END:nextjs-agent-rules -->

## Read Before Anything Else

Read in this exact order before any implementation:

1. context/project-overview.md
2. context/architecture.md
3. context/ui-tokens.md
4. context/ui-rules.md
5. context/ui-registry.md
6. context/code-standards.md
7. context/library-docs.md
8. context/build-plan.md
9. context/progress-tracker.md

## Rules That Never Change

- Never use hardcoded hex values or raw Tailwind color classes
- Update `progress-tracker.md` and `ui-registry.md` after every feature
- After every feature, create `docs/plan/<feature-slug>/` with three files:
  - `plan.md` — what was built and why
  - `explanation.md` — deep explanation of every technical decision for learning
  - `ai-discussion-topics.md` — suggested prompts for deeper AI conversation
- Before any third party library — load its installed skill first,
  then read `context/library-docs.md` for project-specific rules
- If the same problem persists after one corrective prompt —
  stop immediately and run /recover

## Available Skills

The following skill procedures are defined in `.claude/commands/` (Claude Code) and `.agents/skills/` (harness agents). All agents should follow these procedures when the corresponding command is invoked.

- `/architect` — before any complex feature. Think before building.
- `/imprint` — after any new UI component. Capture patterns.
- `/project-review` — before demo or when something feels off.
- `/recover` — when something breaks after one failed correction.
- `/remember save` — when a feature spans multiple sessions.
- `/remember restore` — when returning after a multi-session feature.

---

### /architect — Pre-build thinking session

Run before any complex feature. Do NOT write code until the plan is confirmed.

1. Read existing context files and the feature description.
2. Identify 3-5 ambiguous terms. Define each and confirm with the developer before proceeding.
3. Surface decisions that would change the implementation — one at a time, most impactful first. For each: state your recommendation and reason, then ask the developer to confirm or redirect.
4. When all impactful decisions are resolved, say "Blueprint ready." then write an Implementation Plan with: what is being built, agreed language, decisions made, assumptions, and ordered build steps.
5. Wait for explicit developer confirmation before writing any code.

---

### /imprint — UI pattern capture

Run after building any UI component. Pass an optional filepath or use `audit` mode.

1. Find the component file (from arg, or most recently modified component).
2. Extract consistency-critical classes only: background, border, border-radius, text colors/sizes, spacing, interactive states, shadow, accent usage. Skip layout, sizing, positioning.
3. Write or update the component entry in `ui-registry.md` using the table format (Property | Class).
4. Confirm what was captured to the developer. Flag anything inconsistent.

**Audit mode** (`/imprint audit`): scan all components, report conflicts per property with recommendations, wait for developer confirmation, then write the agreed baseline to `ui-registry.md` and list components that deviate.

---

### /project-review — Feature verification

Run after completing a feature. Report only — do not fix without being asked.

**Layer 1 — Plan alignment:** Compare what was built against the plan from `/architect` or the task description. Flag anything missing or added beyond scope.

**Layer 2 — System integrity:** Check architecture boundaries (no UI logic in API routes, no DB calls in components), design system usage (no hardcoded hex or raw color classes), code standards (naming, TypeScript, error handling), and whether existing patterns were reused.

**Layer 3 — Production readiness:** Check error handling, empty/loading/missing-data states, console errors, and obvious user-facing bugs.

Produce a report with PASS/ISSUES FOUND for each layer. Label issues Critical / Important / Minor. Stop after the report — let the developer decide what to fix.

---

### /recover — Failure diagnosis

Run when something breaks after one failed correction attempt. Diagnose before touching code.

Ask: what did you expect, what happened instead, how many fix attempts so far?

**Failure Mode 1 — Isolated bug** (first/second attempt, clear error, rest of project works): Find the root cause, state it explicitly, propose a precise fix, wait for confirmation. If the fix fails, re-diagnose from scratch.

**Failure Mode 2 — Session polluted** (multiple attempts, tangled code, unclear what original problem was): Acknowledge the session is too far gone to patch. Extract a Reset Note (what was being built, what went wrong, what to avoid, where to start fresh). Instruct the developer to end the session and start fresh with `/remember restore`.

**Failure Mode 3 — Wrong foundation** (code runs but behaviour is fundamentally wrong, approach is incorrect): Name the wrong assumption. Describe the correct approach. Wait for developer confirmation before rebuilding anything.

Always tell the developer which failure mode this is and why before proceeding.

---

### /remember save — End-of-session memory

Run at the end of any session that should continue later.

1. Review the conversation for essential state — not a transcript, only what a colleague needs to continue without losing anything.
2. Never include secrets (API keys, tokens, passwords, connection strings). Redact with `[REDACTED]` if a detail is useful but sensitive.
3. If `memory.md` already exists, show a one-line summary of existing content and ask before overwriting.
4. Write `memory.md` to the project root with sections: What was built, Decisions made, Problems solved, Current state, Next session starts with, Open questions.
5. Confirm: "Memory saved to memory.md. Next session: run /remember restore."

### /remember restore — Start-of-session context

Run at the start of a new session before doing any work.

1. Read `memory.md`. If missing, tell the developer and stop.
2. Also read (if they exist): `CLAUDE.md`, `.claude/context.md`, `AGENTS.md`, `.cursorrules`, `.windsurfrules`, `.github/copilot-instructions.md`, `.clinerules`, `context.md`.
3. Summarise what was restored: last session, current state, locked decisions, next up. Wait for developer confirmation before proceeding.
4. If memory is incomplete or unclear, surface the gap and ask how to proceed — do not guess.

---

# InsForge SDK Documentation - Overview

## What is InsForge?

Backend-as-a-service (BaaS) platform providing:

- **Database**: PostgreSQL with PostgREST API
- **Authentication**: Email/password + OAuth (Google, GitHub)
- **Storage**: File upload/download
- **AI**: OpenRouter key provisioning and model catalog for direct OpenAI-compatible integrations
- **Functions**: Serverless function deployment
- **Realtime**: WebSocket pub/sub (database + client events)

## Installation

The following is a step-by-step guide to installing and using the InsForge TypeScript SDK for Web applications. If you are building other types of applications, please refer to:

- [Swift SDK documentation](/sdks/swift/overview) for iOS, macOS, tvOS, and watchOS applications.
- [Kotlin SDK documentation](/sdks/kotlin/overview) for Android applications.
- [REST API documentation](/sdks/rest/overview) for direct HTTP API access.

### 🚨 CRITICAL: Follow these steps in order

### Step 1: Download Template

Use the `download-template` MCP tool to create a new project with your backend URL and anon key pre-configured.

### Step 2: Install SDK

```bash
npm install @insforge/sdk@latest
```

### Step 3: Create SDK Client

You must create a client instance using `createClient()` with your base URL and anon key:

```javascript
import { createClient } from "@insforge/sdk";

const client = createClient({
  baseUrl: "https://your-app.region.insforge.app", // Your InsForge backend URL
  anonKey: "your-anon-key-here", // Get this from backend metadata
});
```

**API BASE URL**: Your API base URL is `https://your-app.region.insforge.app`.

## Getting Detailed Documentation

### 🚨 CRITICAL: Always Fetch Documentation Before Writing Code

InsForge provides official SDKs and REST APIs, use them to interact with InsForge services from your application code.

- [TypeScript SDK](/sdks/typescript/overview) - JavaScript/TypeScript
- [Swift SDK](/sdks/swift/overview) - iOS, macOS, tvOS, and watchOS
- [Kotlin SDK](/sdks/kotlin/overview) - Android and Kotlin Multiplatform
- [REST API](/sdks/rest/overview) - Direct HTTP API access

Before writing or editing any InsForge integration code, you **MUST** call the `fetch-docs` or `fetch-sdk-docs` MCP tool to get the latest SDK documentation. This ensures you have accurate, up-to-date implementation patterns.

### Use the InsForge `fetch-docs` MCP tool to get specific SDK documentation:

Available documentation types:

- `"instructions"` - Essential backend setup (START HERE)
- `"real-time"` - Real-time pub/sub (database + client events) via WebSockets
- `"db-sdk-typescript"` - Database operations with TypeScript SDK
- **Authentication** - Choose based on implementation:
  - `"auth-sdk-typescript"` - TypeScript SDK methods for custom auth flows
  - `"auth-components-react"` - Pre-built auth UI for React+Vite (single-page app)
  - `"auth-components-react-router"` - Pre-built auth UI for React(Vite+React Router) (multi-page app)
  - `"auth-components-nextjs"` - Pre-built auth UI for Next.js (SSR app)
- `"storage-sdk"` - File storage operations
- `"functions-sdk"` - Serverless functions invocation
- `"ai-integration-sdk"` - AI integration with the provisioned OpenRouter key and OpenAI SDK
- `"deployment"` - Deploy frontend applications via MCP tool
- `"payments"` - Stripe Checkout, Billing Portal, webhook projections, and fulfillment patterns

These docs are mostly for the TypeScript SDK. For other languages, you can also use the `fetch-sdk-docs` MCP tool to get specific documentation.

### Use the InsForge `fetch-sdk-docs` MCP tool to get specific SDK documentation

You can fetch SDK documentation using the `fetch-sdk-docs` MCP tool with a specific feature type and language.

Available feature types:

- `db` - Database operations
- `storage` - File storage operations
- `functions` - Serverless functions invocation
- `auth` - User authentication
- `ai` - AI integration with the provisioned OpenRouter key and OpenAI SDK
- `realtime` - Real-time pub/sub (database + client events) via WebSockets
- `payments` - Stripe Checkout and Billing Portal with webhook-based fulfillment

Available languages:

- `typescript` - JavaScript/TypeScript SDK
- `swift` - Swift SDK (for iOS, macOS, tvOS, and watchOS)
- `kotlin` - Kotlin SDK (for Android and JVM applications)
- `rest-api` - REST API

Payments currently has TypeScript SDK docs only. Use the Payments API reference for non-TypeScript clients.

## When to Use SDK vs MCP Tools

### Always SDK for Application Logic:

- Authentication (register, login, logout, profiles)
- Database CRUD (select, insert, update, delete)
- Storage operations (upload, download files)
- AI integration via the provisioned OpenRouter key with the OpenAI SDK or OpenRouter HTTP API
- Serverless function invocation
- Payments checkout and customer portal session creation

### Use MCP Tools for Infrastructure:

- Project scaffolding (`download-template`) - Download starter templates with InsForge integration
- Backend setup and metadata (`get-backend-metadata`)
- Database schema management (`run-raw-sql`, `get-table-schema`)
- Storage bucket creation (`create-bucket`, `list-buckets`, `delete-bucket`)
- Serverless function deployment (`create-function`, `update-function`, `delete-function`)
- Frontend deployment (`create-deployment`) - Deploy frontend apps to InsForge hosting

## Important Notes

- For auth: use `auth-sdk` for custom UI, or framework-specific components for pre-built UI
- SDK returns `{data, error}` structure for all operations
- Database inserts require array format: `[{...}]`
- Serverless functions have one endpoint and do not support nested route paths
- Storage: Upload files to buckets, store URLs in database
- AI integrations should call OpenRouter directly with `baseURL: "https://openrouter.ai/api/v1"` and a server-side `OPENROUTER_API_KEY`
- **EXTRA IMPORTANT**: Use Tailwind CSS 3.4 (do not upgrade to v4). Lock these dependencies in `package.json`
