# Demo 3 — Payment Aging Report Generator

## 1. Summary

The **Payment Aging Report Generator** reads invoice/payment data and groups outstanding balances into aging buckets. It flags overdue invoices and creates a follow-up priority list.

This demo connects directly to payment follow-up, cash-flow awareness, and sales/admin coordination work.

## 2. Business problem

Sales/admin and operations staff often need to follow up with customers or suppliers about payment status. Manual checks can miss overdue invoices, especially when data is spread across Excel files, email threads, and accounting exports.

A small payment aging tool can help by:

- calculating days overdue,
- grouping invoices into aging buckets,
- prioritizing high-risk follow-up,
- generating clean Excel reports,
- creating draft follow-up messages.

## 3. User story

As a sales admin / operations staff member, I want to upload invoice/payment data and automatically generate a payment aging report, so that I can prioritize follow-up and support healthy cash flow.

## 4. Input file

### File name

`invoices.xlsx`

### Required columns

| Column | Type | Required | Example |
|---|---:|---:|---|
| invoice_id | string | Yes | INV-2026-001 |
| customer_name | string | Yes | Bright Medical Trading Ltd |
| invoice_date | date | Yes | 2026-06-01 |
| due_date | date | Yes | 2026-07-01 |
| invoice_amount | float | Yes | 12000.00 |
| paid_amount | float | Optional | 3000.00 |
| currency | string | Optional | HKD |
| payment_status | string | Optional | Partial |
| sales_owner | string | Optional | Jesse |
| remarks | string | Optional | Waiting for client confirmation |

## 5. Payment aging rules

### Rule PA-001 — Outstanding amount

Outstanding amount is:

```text
outstanding_amount = invoice_amount - paid_amount
```

If `paid_amount` is missing, treat it as 0.

### Rule PA-002 — Fully paid invoices

If `outstanding_amount <= 0`, mark invoice as `Paid` and exclude it from overdue follow-up.

### Rule PA-003 — Days overdue

Days overdue is:

```text
days_overdue = today_date - due_date
```

If `days_overdue <= 0`, the invoice is not overdue.

### Rule PA-004 — Aging buckets

| Bucket | Condition |
|---|---|
| Current | due date not passed |
| 1-30 Days | 1 to 30 days overdue |
| 31-60 Days | 31 to 60 days overdue |
| 61-90 Days | 61 to 90 days overdue |
| 90+ Days | more than 90 days overdue |

### Rule PA-005 — Follow-up priority

V1 priority rules:

| Priority | Condition |
|---|---|
| High | days_overdue > 60 or outstanding_amount >= 50000 |
| Medium | days_overdue between 31 and 60 |
| Low | days_overdue between 1 and 30 |
| Watch | not overdue but due within 7 days |
| None | paid or not due soon |

### Rule PA-006 — Missing due date

If due date is missing, flag the row as an error and exclude from aging calculation.

### Rule PA-007 — Invalid amount

If invoice amount is missing or less than 0, flag as error.

## 6. Output

### Screen output

The app should display:

- total invoices,
- total outstanding amount,
- overdue amount,
- high-priority follow-up count,
- aging bucket summary,
- follow-up table.

### Downloadable output

`payment_aging_report.xlsx`

Suggested sheets:

1. `Aging Summary`
2. `Follow-up List`
3. `All Invoices with Aging`
4. `Data Issues`
5. `Draft Messages`

### Aging output columns

| Column | Description |
|---|---|
| invoice_id | Invoice number |
| customer_name | Customer name |
| invoice_date | Invoice date |
| due_date | Due date |
| invoice_amount | Original invoice amount |
| paid_amount | Paid amount |
| outstanding_amount | Remaining unpaid amount |
| days_overdue | Days overdue |
| aging_bucket | Current / 1-30 / 31-60 / 61-90 / 90+ |
| follow_up_priority | High / Medium / Low / Watch / None |
| suggested_action | Suggested next step |

## 7. Suggested actions

| Condition | Suggested action |
|---|---|
| High priority | Call or email customer urgently |
| Medium priority | Send payment reminder this week |
| Low priority | Include in regular follow-up list |
| Watch | Monitor before due date |
| Paid | No action required |
| Missing due date | Confirm payment terms or due date |

## 8. Draft follow-up message

The app can generate a simple draft message for each overdue customer.

Example:

```text
Dear [Customer Name],

Hope you are well. We would like to follow up on invoice [Invoice ID], with an outstanding amount of [Outstanding Amount], which is currently [Days Overdue] days overdue.

Please let us know the expected payment status or if any further information is required from our side.

Thank you.
```

## 9. UI requirements

### Page title

`Payment Aging`

### UI elements

- File uploader for `invoices.xlsx`
- Date selector for `as_of_date`
- Button: `Generate Aging Report`
- KPI cards:
  - Total Outstanding
  - Overdue Amount
  - High Priority Count
  - 90+ Days Amount
- Aging bucket chart or table
- Follow-up priority table
- Draft message preview
- Download report button

### Empty state

Show:

> Upload an invoice/payment file to generate an aging report.

### Error state

If due dates or amounts are invalid, show them in a `Data Issues` section.

## 10. Suggested Python modules

```text
src/
  payment_aging.py
  excel_io.py
  report_export.py
```

## 11. Suggested functions

```python
def load_invoices(file) -> pd.DataFrame:
    """Load invoice Excel file into a DataFrame."""


def calculate_payment_aging(invoices_df: pd.DataFrame, as_of_date: date) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return aging_df and data_issues_df."""


def create_follow_up_messages(aging_df: pd.DataFrame) -> pd.DataFrame:
    """Generate draft follow-up messages for overdue invoices."""


def export_payment_aging_report(aging_df, data_issues_df, messages_df) -> bytes:
    """Return Excel report as bytes."""
```

## 12. Test cases

| Test case | Input | Expected output |
|---|---|---|
| Fully paid invoice | invoice 1000, paid 1000 | Paid, no follow-up |
| Missing paid amount | paid blank | paid treated as 0 |
| Current invoice | due date in future | aging bucket Current |
| 20 days overdue | due date 20 days ago | 1-30 Days, Low priority |
| 45 days overdue | due date 45 days ago | 31-60 Days, Medium priority |
| 75 days overdue | due date 75 days ago | 61-90 Days, High priority |
| 100 days overdue | due date 100 days ago | 90+ Days, High priority |
| Large overdue amount | overdue amount >= 50000 | High priority |
| Missing due date | due date blank | Data issue |
| Negative invoice amount | invoice amount < 0 | Data issue |

## 13. Interview explanation

> This module supports payment follow-up by turning invoice data into a clear aging report. It calculates outstanding amounts, days overdue, aging buckets, and follow-up priority. It also generates simple draft reminder messages. This connects directly to sales admin work because payment follow-up is often manual and easy to miss.
