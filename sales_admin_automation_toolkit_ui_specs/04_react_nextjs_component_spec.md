# 04 — React / Next.js Component Specification

## Purpose

This file defines possible frontend components if the toolkit is rebuilt or polished using React / Next.js.

The goal is not to overbuild. The goal is to make the project look like a professional B2B dashboard while keeping the business logic in Python.

## Recommended stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Table or MUI Data Grid
- Recharts
- TanStack Query or Zustand
- FastAPI backend

## Folder structure suggestion

```text
frontend/
  app/
    page.tsx
    orders/page.tsx
    allocation/page.tsx
    payments/page.tsx
    reports/page.tsx
  components/
    layout/
      AppShell.tsx
      SidebarNav.tsx
      TopNav.tsx
    dashboard/
      MetricCard.tsx
      WorkflowStepper.tsx
      SummaryChart.tsx
    upload/
      UploadPanel.tsx
      FileRequirementCard.tsx
    tables/
      DataTable.tsx
      StatusBadge.tsx
      ValidationResultsTable.tsx
      AllocationResultsTable.tsx
      PaymentAgingTable.tsx
    reports/
      ExportReportCard.tsx
    feedback/
      EmptyState.tsx
      LoadingState.tsx
      ErrorBanner.tsx
  lib/
    api.ts
    formatters.ts
    constants.ts
  types/
    orders.ts
    inventory.ts
    payments.ts
    reports.ts
```

## Component list

### AppShell

Wraps the whole app.

Includes:

- sidebar
- top navigation
- main content area
- responsive layout

### SidebarNav

Navigation items:

- Overview
- Order Validation
- Inventory Allocation
- Payment Aging
- Reports
- Optional: CRM Cleaner
- Settings

### TopNav

Displays:

- app name
- demo mode label
- theme toggle if implemented
- GitHub / portfolio link if appropriate

### MetricCard

Reusable KPI card.

Props:

```ts
interface MetricCardProps {
  title: string;
  value: string | number;
  helperText?: string;
  status?: "neutral" | "success" | "warning" | "danger";
  icon?: React.ReactNode;
}
```

### WorkflowStepper

Shows the current process:

1. Upload
2. Validate
3. Allocate
4. Review
5. Export

Props:

```ts
interface WorkflowStepperProps {
  currentStep: number;
}
```

### UploadPanel

Reusable file upload component.

Props:

```ts
interface UploadPanelProps {
  title: string;
  description: string;
  acceptedTypes: string[];
  requiredColumns: string[];
  onUpload: (file: File) => void;
  isProcessing?: boolean;
}
```

### StatusBadge

Consistent status labels.

Status categories:

```ts
type StatusType =
  | "valid"
  | "error"
  | "warning"
  | "fully_allocated"
  | "partial"
  | "backordered"
  | "current"
  | "overdue"
  | "high_risk";
```

### DataTable

Reusable table wrapper.

Should support:

- sorting
- filtering
- pagination
- empty state
- loading state

### ValidationResultsTable

Specialized table for order validation.

Columns:

- row number
- order ID
- customer
- SKU
- issue type
- issue message
- severity

### AllocationResultsTable

Columns:

- order ID
- customer
- SKU
- requested quantity
- allocated quantity
- backorder quantity
- warehouse
- status

### PaymentAgingTable

Columns:

- invoice ID
- customer
- due date
- amount
- days overdue
- aging bucket
- priority
- suggested action

### ExportReportCard

Displays report download options.

Props:

```ts
interface ExportReportCardProps {
  title: string;
  description: string;
  fileType: "xlsx" | "csv";
  disabled: boolean;
  onDownload: () => void;
}
```

### EmptyState

Used before upload or when no results exist.

Example message:

```text
No order file uploaded yet. Upload a sample Excel file to start validation.
```

### LoadingState

Used while processing files.

Example message:

```text
Checking order file against product master and validation rules...
```

### ErrorBanner

Shows business-readable error messages.

Example:

```text
The uploaded file is missing required column: sku.
```

## Design system tokens

Suggested tokens:

```text
Background: slate-50
Surface: white
Text primary: slate-900
Text secondary: slate-500
Border: slate-200
Accent: blue-600
Success: emerald-600
Warning: amber-500
Danger: red-600
Radius: 12px or 16px
Card shadow: subtle
```

## Important principle

The UI should not hide the business logic. It should make the business rules visible and easy to explain in an interview.
