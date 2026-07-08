# 03 — Figma MCP Prompts for Coding Agents

Use these prompts when your coding agent can access Figma designs through MCP.

Important: The agent should not immediately generate code. It should first inspect the Figma file and produce a design-to-code plan.

---

## Figma MCP Inspection Prompt

```text
You have access to a Figma design or Figma Make output for the Sales Admin Automation Toolkit.

Do not immediately generate code.

First inspect the design through Figma MCP and produce:
1. list of screens/frames found
2. list of reusable UI components
3. mapping from Figma components to React components
4. design tokens detected or recommended
5. data needed by each screen
6. interactions needed by each screen
7. responsive layout assumptions
8. accessibility concerns
9. missing design details or ambiguities
10. recommended implementation sequence

After I approve the plan, implement the UI using Next.js, TypeScript, Tailwind CSS, and shadcn/ui or MUI Data Grid.
```

---

## MCP Capability Check Prompt

```text
Before using the Figma design, confirm what MCP or design-reading capabilities you have.

Please answer:
1. Can you access the Figma file directly through MCP?
2. Can you inspect frames, components, layout, spacing, colors, and text?
3. Can you identify component hierarchy and variants?
4. Can you read design tokens or variables?
5. Can you export assets if needed?
6. Do you need screenshots as a fallback?
7. What information should I provide if MCP access is incomplete?

Do not write UI code yet.
```

---

## Figma-to-Code Mapping Prompt

```text
Inspect the Figma design for Sales Admin Automation Toolkit and map it into a React/Next.js implementation plan.

For each Figma screen, provide:
- screen name
- route path
- layout structure
- reusable components
- data props required
- user interactions
- loading state
- empty state
- error state
- responsive behavior

For each reusable component, provide:
- component name
- purpose
- props
- visual states
- recommended shadcn/ui or custom implementation
- related backend/mock data

Do not code until this mapping is approved.
```

---

## Design Scope Control Prompt

```text
Review the Figma design and identify whether it introduces features beyond the agreed project scope.

Agreed V1 scope:
- order validation
- inventory allocation
- payment aging
- report export
- Excel upload/download

Please classify Figma UI elements into:
- must implement for V1
- nice-to-have for V1.5
- postpone to V2
- remove because it suggests a full ERP system

The goal is to keep the app polished but not overcommitted.
```

---

## MCP Implementation Approval Prompt

```text
Based on your Figma MCP inspection, produce a final implementation proposal.

Include:
1. files to create
2. components to implement first
3. mock data needed
4. API endpoints or placeholder functions needed
5. Tailwind/shadcn setup required
6. table library recommendation
7. chart library recommendation
8. implementation order
9. risks
10. simplifications

Wait for my approval before creating code.
```
