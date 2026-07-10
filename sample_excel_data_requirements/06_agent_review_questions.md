# Questions to Grill Coding Agents

Use these questions before implementation or during review.

## Business Realism

```text
1. Does the generated data support order validation, inventory allocation, and payment aging without adding new business rules?
2. Does the data feel like HK regional medical-device sales operations rather than random numbers?
3. Are products, customers, warehouses, orders, and invoices internally consistent?
4. Are the intentional errors realistic and limited?
5. Are the data volumes small enough for a portfolio demo?
6. Could a hiring manager understand the story in 60 seconds?
```

## Schema and Workflow

```text
1. Which columns are required by the current Python loaders?
2. Which optional columns are already tolerated or consumed?
3. Which proposed fields are reference-only and must not affect V1 behavior?
4. Which files are uploaded by each Phase 10 page?
5. Which files depend on each other?
6. What should happen if a file is missing a required column?
7. Does any proposed column name conflict with current code?
```

## Current Contract Alignment

```text
1. Are we using active, not is_active?
2. Are we using available_qty / reserved_qty, not available_stock / reserved_stock?
3. Are we using invoice_id, not invoice_no?
4. Are priorities High / Normal / Low, not High / Standard / Low?
5. Are payment terms represented as payment_terms strings?
6. Are customer IDs reference-only unless an ADR adds customer validation?
```

## Data Quality

```text
1. How do we ensure SKUs are mostly valid but still include invalid examples?
2. How do we ensure duplicate order IDs exist intentionally?
3. How do we ensure blank payment_terms produces warnings without invalidating rows?
4. How do we ensure some valid orders fully allocate, partially allocate, and backorder?
5. How do we ensure all payment aging buckets appear?
6. How do we avoid unrealistic perfect data?
7. How do we document every intentional defect?
```

## Technical Implementation

```text
1. Should the generator remain in src/sample_data.py or move to a generation package?
2. How do we keep generation deterministic?
3. Which constants control data volume and error ratios?
4. How should tests verify generated Excel files?
5. Should generated Excel files be committed to GitHub?
6. How will generated files feed lib/mock-data refresh before Phase 10?
```

## Portfolio Presentation

```text
1. How should README_sample_data.md explain that the data is synthetic?
2. How can we show intentional errors without making the project look broken?
3. How can the UI make required upload files obvious in Phase 10?
4. Should sample template download buttons point to these committed files?
5. How can the generated data support a smooth 60-second demo?
```
