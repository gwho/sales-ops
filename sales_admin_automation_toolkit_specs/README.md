# Sales Admin Automation Toolkit — Preliminary Portfolio Specification

## Purpose

This specification defines a small, practical portfolio project made of **three connected demos** under one portfolio name:

> **Sales Admin Automation Toolkit**

The goal is to demonstrate how Python, Excel automation, and light dashboard/UI work can improve daily sales administration, sales coordination, and operations workflows without overcommitting to a full ERP, CRM, WMS, or accounting system.

This project is designed for roles such as:

- Sales Coordinator
- Sales Administrator
- Operations Executive
- Supply Chain Assistant
- Logistics / Trading Coordinator
- IT Consulting Sales Admin
- Medical Device / Equipment Sales Coordinator

## Why this project exists

Many sales/admin/operations teams still work with Excel files, email attachments, order sheets, invoice lists, and stock reports. The most useful automation is often not a huge enterprise system, but a small tool that can:

1. catch order entry mistakes,
2. allocate stock clearly,
3. flag payment follow-up priorities,
4. export clean reports for colleagues.

This toolkit is intentionally small and practical. It is meant to prove:

> I understand daily sales operations because I have done this type of work, and I can use Python/Excel automation to make the work cleaner, faster, and easier to track.

## Background connection

The project is inspired by real work patterns from sales/admin and coordination roles:

- quotation preparation,
- order processing,
- customer and supplier coordination,
- purchase order / sales order preparation,
- stock monitoring,
- delivery management,
- CRM data cleaning,
- sales reporting,
- payment or invoice follow-up.

Use only fictional sample data. Do not use real customer, employer, supplier, invoice, order, or product data.

## The three connected demos

| Demo | Name | Main business value |
|---|---|---|
| Demo 1 | Order Entry Validation Tool | Reduce order-entry errors before processing |
| Demo 2 | Inventory Allocation Mini Engine | Allocate stock and identify backorders clearly |
| Demo 3 | Payment Aging Report Generator | Prioritize overdue payment follow-up |

Optional extension:

| Extension | Name | Main business value |
|---|---|---|
| Optional | CRM Data Cleaner | Detect duplicate or incomplete customer records |

## Recommended V1 stack

Use the simplest stack that creates a useful, credible portfolio demo:

- Python
- Pandas
- openpyxl
- Streamlit
- pytest
- GitHub
- Streamlit Community Cloud or local demo

Avoid building the full Next.js/FastAPI/PostgreSQL version first unless the simple version is already working.

## Recommended V1 user flow

1. User opens the Streamlit app.
2. User uploads sample Excel files.
3. App validates orders.
4. App allocates inventory.
5. App calculates payment aging.
6. App displays results in clean tables/cards.
7. User downloads an Excel report with multiple sheets.

## Suggested app pages

For V1, keep the UI simple:

1. **Overview**
2. **Order Validation**
3. **Inventory Allocation**
4. **Payment Aging**
5. **Download Reports**

## Non-goals

This project is **not** trying to be:

- a full ERP system,
- a full accounting system,
- a full warehouse management system,
- a production CRM,
- a real payment collection system,
- a real inventory synchronization tool,
- a multi-user enterprise platform.

## Key portfolio message

Use this wording in README/interview:

> This is a practical portfolio demo inspired by sales admin and operations workflows. It uses Python and Excel automation to validate sales orders, allocate stock, flag backorders, calculate payment aging, and generate follow-up reports. The goal is to show how small automation tools can reduce manual checking and improve daily operations.
