# Questions to Ask Coding Agents Before Implementation

Use these questions to grill coding agents before allowing them to write code.

## 1. Scope control

```text
Given this project specification, what is the smallest V1 that still demonstrates value for sales admin / operations roles?
What should be excluded from V1 to avoid overbuilding?
```

```text
Which features are must-have, nice-to-have, and should-not-build for V1?
```

## 2. Business rule review

```text
Review the order validation rules. Are they clear, testable, and realistic for sales admin work?
Suggest improvements without making the project too complex.
```

```text
Review the inventory allocation rules. Are priority, delivery date, partial allocation, and reorder alerts enough for V1?
What edge cases should be tested?
```

```text
Review the payment aging rules. Are the aging buckets and follow-up priority logic realistic?
What should happen with missing due dates or partial payments?
```

## 3. Data design

```text
Design the sample Excel templates for this project.
For each file, list required columns, optional columns, sample rows, and validation requirements.
```

```text
Should orders be represented as one row per order or one row per order line?
Explain the tradeoff for a beginner and recommend a V1 choice.
```

## 4. Technical architecture

```text
Recommend a simple Python project structure for this toolkit.
Separate business logic from Streamlit UI.
Explain why this separation matters for testing and interview explanation.
```

```text
Should I use Streamlit only, or should I build FastAPI/Next.js?
Compare speed, portfolio value, and relevance to sales admin roles.
```

## 5. Testing

```text
Write a pytest-focused test plan for this project.
Prioritize business logic tests over UI tests.
```

```text
For each module, define 5 to 10 test cases with input and expected output.
```

## 6. Excel handling

```text
Design the Excel import/export workflow using pandas and openpyxl.
How should errors be displayed and exported?
```

```text
How should the app behave if uploaded files are missing required columns?
```

## 7. UI/UX

```text
Suggest a clean Streamlit UI layout for this toolkit.
Make it look like a professional internal operations tool, not a student demo.
```

```text
What KPI cards, tables, charts, loading states, and empty states should be included?
```

## 8. Portfolio presentation

```text
Write a GitHub README structure for this project.
It should explain the business problem, features, tech stack, screenshots, setup, and interview value.
```

```text
Write a 60-second interview demo script for this project.
```

```text
Write resume bullet points for this project targeted at Sales Admin / Operations Executive roles.
```

## 9. Risk review

```text
What are the main risks of this project becoming too big or too technical for sales admin roles?
How should I prevent that?
```

```text
How can I make sure this project does not look like a random coding project but instead clearly connects to my work experience?
```

## 10. Implementation instruction

```text
Now create the implementation plan, but do not write code yet.
Break the work into small commits:
1. sample data
2. order validation module
3. order validation tests
4. inventory allocation module
5. allocation tests
6. payment aging module
7. payment aging tests
8. report export
9. Streamlit UI
10. README and screenshots
```
