# Resume and Interview Positioning

## 1. Resume project title

Use one of these:

- Sales Admin Automation Toolkit — Python / Excel / Streamlit
- Sales & Inventory Operations Assistant — Python / Pandas / Excel
- Sales Operations Excel Automation Demo — Python / Streamlit

Recommended:

> **Sales Admin Automation Toolkit — Python / Excel / Streamlit**

## 2. Resume project bullet

```text
Built a practical Python/Excel automation demo for sales admin and operations workflows. The toolkit validates Excel-based sales orders, detects missing or incorrect entries, allocates inventory by SKU and warehouse, flags backorders, generates payment aging reports, and exports clean follow-up reports for operational use.
```

## 3. Short portfolio description

```text
Sales Admin Automation Toolkit is a practical portfolio demo inspired by real sales coordination and operations workflows. It shows how Python and Excel automation can reduce manual checking, improve order accuracy, support inventory allocation, and prioritize payment follow-up.
```

## 4. 60-second interview demo script

```text
This is a small portfolio project I built to demonstrate how I can apply Python to daily sales admin and operations work.

The app has three connected parts. First, it validates a sales order Excel file and flags issues like missing customer names, duplicate order numbers, invalid SKUs, and wrong quantities. Second, it uses the valid orders and inventory file to allocate available stock, show full or partial allocation, and create a backorder list. Third, it reads invoice data and creates a payment aging report so overdue follow-up can be prioritized.

I kept the project Excel-first because many admin and operations teams still work with Excel. The goal is not to replace an ERP system, but to show how small automation tools can reduce errors and speed up routine checking.
```

## 5. Deeper technical explanation

```text
The project separates business logic from the UI. The core rules are implemented in Python modules for order validation, inventory allocation, and payment aging. Each module can be tested independently with pytest. The Streamlit UI is only the interface for uploading Excel files, running the checks, displaying results, and downloading reports.

This separation is important because the business rules are the real value. The interface can later be changed to FastAPI or Next.js, but the core logic remains reusable.
```

## 6. How to connect to past experience

```text
This project is inspired by patterns I saw in sales coordination and admin work: checking order details, preparing quotations and reports, following up with customers and suppliers, monitoring stock and delivery status, and maintaining customer data. I used fictional sample data, but the workflow reflects real daily operations problems.
```

## 7. What to say if asked whether this is production-ready

```text
It is a portfolio demo, not a production ERP system. I designed it with production-minded habits such as clear business rules, separate modules, tests, sample data, and report exports. For real production use, it would need user authentication, database integration, permission control, audit logs, and integration with existing ERP/accounting systems.
```

## 8. What to say if asked about AI/coding agents

```text
I used AI coding tools as assistants, but I defined the business rules myself based on sales admin and operations workflows. I reviewed the generated code, kept the logic in separate Python modules, added tests, and made sure I could explain the allocation and payment aging rules clearly.
```

## 9. What not to claim

Do not claim:

- it was used by a previous employer,
- it is a full ERP system,
- it is production-ready,
- it can replace accounting or warehouse systems,
- it handles real confidential data,
- it guarantees perfect inventory decisions.

Do claim:

- it is a practical portfolio demo,
- it uses fictional sample data,
- it demonstrates Python/Excel automation for sales admin workflows,
- it shows business-rule thinking,
- it can be extended into a larger system later.
