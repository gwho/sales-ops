# 03 — Screenshot-to-Wireframe Options

## Goal

Understand the realistic options for turning screenshots into wireframes or code.

## Option A: Manual low-fi wireframe in Figma

Best for beginners.

Workflow:

1. Paste screenshot into Figma.
2. Draw simple rectangles over the layout.
3. Label key sections.
4. Replace the screenshot with your own business content.
5. Export the wireframe or share the Figma link.

Pros:

- Reliable
- Easy to understand
- Avoids messy generated layers
- Good for coding-agent planning

Cons:

- Requires some manual effort

## Option B: Figma AI / Figma Make prompt-to-wireframe

Use AI to generate an initial wireframe from your prompt.

Example prompt:

```text
Create a clean B2B SaaS dashboard wireframe for a Sales Admin Automation Toolkit.
Include sidebar navigation, top KPI cards, Excel upload panel, validation error table, inventory allocation table, payment aging summary, and report export cards.
Light theme, professional internal operations style.
```

Pros:

- Fast
- Good for exploring layouts
- Useful when you do not know where to start

Cons:

- May look generic
- Needs refinement
- May not match your exact business workflow

## Option C: Screenshot-to-Figma plugin/tool

Some tools can convert screenshots/images into editable Figma layers.

Pros:

- Can create editable layers quickly
- Useful for extracting rough layout

Cons:

- Output may be messy
- Text, icons, shadows, and spacing often need cleanup
- May create many unnecessary layers
- Risk of copying too closely

## Option D: Screenshot-to-code with coding agent

Provide screenshots directly to a coding agent and ask it to build a similar UI.

Pros:

- Fast for Next.js/Tailwind/shadcn prototypes
- Good for agentic UI scaffolding

Cons:

- Can miss details
- Can produce inconsistent components
- Better if you first provide a component spec

## Recommended choice for this project

Use a mixed approach:

```text
Reference screenshots
→ Figma annotation board
→ simple manual wireframes
→ coding-agent UI spec
→ Next.js/shadcn or Streamlit implementation
```

Do not rely purely on screenshot-to-code. The business workflow matters more than pixel-perfect copying.
