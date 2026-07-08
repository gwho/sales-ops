# Optional Extension — CRM Data Cleaner

## 1. Summary

The **CRM Data Cleaner** checks customer/contact data for duplicates, missing fields, inconsistent region/industry tags, and incomplete contact information.

This is optional for V1, but it connects strongly to sales support, CRM maintenance, marketing list preparation, and customer data quality work.

## 2. Business problem

Customer and prospect lists often contain messy records:

- duplicate company names,
- duplicate emails,
- missing phone numbers,
- missing contact person,
- inconsistent region names,
- missing industry tags.

This causes duplicated outreach, inaccurate reports, and poor sales follow-up.

## 3. User story

As a sales admin or business development support staff member, I want to upload a customer list and detect data quality issues, so that the sales team can maintain a cleaner CRM database.

## 4. Input file

### File name

`customers.xlsx`

### Required columns

| Column | Type | Required | Example |
|---|---:|---:|---|
| customer_id | string | Optional | CUST-001 |
| company_name | string | Yes | Bright Medical Trading Ltd |
| contact_person | string | Optional | Mary Chan |
| email | string | Optional | mary@example.com |
| phone | string | Optional | 2345 6789 |
| region | string | Optional | Hong Kong |
| industry | string | Optional | Medical Device |
| source | string | Optional | Trade Show |
| last_contact_date | date | Optional | 2026-06-15 |

## 5. Data quality rules

### Rule CRM-001 — Missing company name

`company_name` is required.

### Rule CRM-002 — Missing contact method

At least one of `email` or `phone` should be present.

### Rule CRM-003 — Duplicate email

If the same email appears in multiple rows, flag as possible duplicate.

### Rule CRM-004 — Duplicate phone

If the same phone appears in multiple rows, flag as possible duplicate.

### Rule CRM-005 — Similar company names

V1 simple approach:

- Normalize company names by lowercasing and removing punctuation/common suffixes like Ltd, Limited, Co.
- If normalized names match, flag as possible duplicate.

### Rule CRM-006 — Missing region

If region is blank, flag as warning.

### Rule CRM-007 — Missing industry tag

If industry is blank, flag as warning.

## 6. Output

### Screen output

The app should display:

- total customer records,
- possible duplicate count,
- missing contact method count,
- missing region count,
- missing industry count,
- data issue table.

### Downloadable output

`crm_cleaning_report.xlsx`

Suggested sheets:

1. `CRM Summary`
2. `Possible Duplicates`
3. `Missing Contact Info`
4. `Missing Tags`
5. `Original Customers`

## 7. Suggested issue table columns

| Column | Description |
|---|---|
| row_number | Source row number |
| customer_id | Customer ID if available |
| company_name | Company name |
| issue_code | Example: CRM-003 |
| issue_message | Human-readable issue |
| severity | Error / Warning |
| suggested_action | Recommended fix |

## 8. UI requirements

### Page title

`CRM Data Cleaner`

### UI elements

- File uploader for `customers.xlsx`
- Button: `Check CRM Data`
- KPI cards:
  - Total Records
  - Possible Duplicates
  - Missing Contact Method
  - Missing Region
  - Missing Industry
- Data issue table
- Download report button

## 9. Suggested Python modules

```text
src/
  crm_cleaning.py
  excel_io.py
  report_export.py
```

## 10. Suggested functions

```python
def load_customers(file) -> pd.DataFrame:
    """Load customer Excel file into a DataFrame."""


def normalize_company_name(name: str) -> str:
    """Normalize company names for simple duplicate detection."""


def check_crm_data_quality(customers_df: pd.DataFrame) -> pd.DataFrame:
    """Return CRM data issue table."""


def export_crm_cleaning_report(customers_df, crm_issues_df) -> bytes:
    """Return Excel report as bytes."""
```

## 11. Test cases

| Test case | Input | Expected output |
|---|---|---|
| Missing company name | blank company_name | CRM-001 error |
| Missing email and phone | both blank | CRM-002 warning/error |
| Duplicate email | same email twice | CRM-003 duplicate flag |
| Duplicate phone | same phone twice | CRM-004 duplicate flag |
| Similar company names | ABC Ltd vs ABC Limited | CRM-005 duplicate flag |
| Missing region | blank region | CRM-006 warning |
| Missing industry | blank industry | CRM-007 warning |

## 12. Interview explanation

> This optional module connects to CRM maintenance and sales support. It checks customer data for duplicates, missing contact information, and incomplete segmentation fields. It is useful because clean customer data improves sales follow-up, reporting, and marketing campaigns.
