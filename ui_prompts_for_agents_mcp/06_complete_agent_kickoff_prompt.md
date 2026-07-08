# 06 — Complete Agent Kickoff Prompt

Use this as a complete kickoff prompt for a coding agent with Figma MCP or UI design capability.

```text
I am building a portfolio project called Sales Admin Automation Toolkit.

It is a small internal operations dashboard for sales admin / operations workflows:
- order validation
- inventory allocation
- payment aging
- Excel report export

I want the UI to look professional and not generic or AI-generated. I may provide Figma Make designs, Figma files, screenshots, or UI references. If Figma MCP is available, use it to inspect the design context. If not, use screenshots and written requirements as fallback.

Important constraints:
- Do not turn this into a full ERP system.
- Do not implement features that are outside the V1 scope unless we explicitly approve them.
- Do not write code immediately.
- First inspect, critique, and plan.

Please produce:
1. summary of the intended product
2. UI screens needed
3. reusable component list
4. visual direction
5. Figma/MCP findings if available
6. component-to-code mapping
7. data requirements per screen
8. suggested Next.js/Tailwind/shadcn implementation plan
9. what should be mocked first
10. what should connect to Python logic later
11. risks and simplifications
12. questions I need to answer before implementation

After I approve, we will implement the UI in phases.
```
