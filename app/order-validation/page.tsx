"use client";

// This page must be a Client Component: its DataTable column definitions
// contain render functions, and functions cannot cross the Server->Client
// props boundary (only the DataTable primitive itself strictly needed to be
// client — but its callers do too, since they construct its column config).

// Internal imports
import { MetricCard } from "@/components/workflow/MetricCard";
import { UploadPanel } from "@/components/workflow/UploadPanel";
import { WorkflowStepper } from "@/components/workflow/WorkflowStepper";
import { DataTable, type DataTableColumn } from "@/components/tables/DataTable";
import { StatusBadge, severityTone, importancePriorityTone } from "@/components/workflow/StatusBadge";
import { orderValidationResult } from "@/lib/mock-data";
import { formatDate, formatNumber } from "@/lib/formatters";
import type { ValidationErrorRow, ValidOrderRow } from "@/types";

const STEPS = ["Upload Files", "Run Validation", "Review Results"];

const ERROR_COLUMNS: DataTableColumn<ValidationErrorRow>[] = [
  { key: "row_number", header: "Row", render: (r) => r.row_number, sortable: true, sortValue: (r) => r.row_number },
  { key: "order_id", header: "Order ID", render: (r) => r.order_id ?? "—" },
  { key: "sku", header: "SKU", render: (r) => r.sku ?? "—" },
  { key: "error_code", header: "Error Code", render: (r) => r.error_code },
  { key: "error_message", header: "Error Message", render: (r) => r.error_message },
  {
    key: "severity",
    header: "Severity",
    render: (r) => <StatusBadge status={r.severity} tone={severityTone(r.severity)} />,
  },
];

const VALID_ORDER_COLUMNS: DataTableColumn<ValidOrderRow>[] = [
  { key: "order_id", header: "Order ID", render: (r) => r.order_id },
  {
    key: "order_date",
    header: "Order Date",
    render: (r) => formatDate(r.order_date),
    sortable: true,
    sortValue: (r) => r.order_date,
  },
  { key: "customer_name", header: "Customer", render: (r) => r.customer_name },
  { key: "customer_region", header: "Region", render: (r) => r.customer_region },
  { key: "sku", header: "SKU", render: (r) => r.sku },
  { key: "product_name", header: "Product", render: (r) => r.product_name ?? "—" },
  { key: "quantity", header: "Qty", render: (r) => formatNumber(r.quantity) },
  {
    key: "requested_delivery_date",
    header: "Requested Delivery",
    render: (r) => formatDate(r.requested_delivery_date),
    sortable: true,
    sortValue: (r) => r.requested_delivery_date,
  },
  {
    key: "priority",
    header: "Priority",
    render: (r) => <StatusBadge status={r.priority} tone={importancePriorityTone(r.priority)} />,
    sortable: true,
    sortValue: (r) => r.priority,
  },
  { key: "payment_terms", header: "Payment Terms", render: (r) => r.payment_terms },
  { key: "sales_owner", header: "Sales Owner", render: (r) => r.sales_owner ?? "—" },
];

// Component
export default function OrderValidationPage() {
  const { summary, errors, valid_orders } = orderValidationResult;

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-2xl font-semibold text-text-primary">Order Validation</h1>
      <p className="mt-2 text-sm text-text-secondary">
        Check orders against required fields, active SKUs, and business rules.
      </p>

      <div className="mt-6">
        <WorkflowStepper steps={STEPS} currentStep={STEPS.length - 1} />
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <UploadPanel
          label="Orders File"
          requiredColumns={[
            "order_id",
            "order_date",
            "customer_name",
            "customer_region",
            "sku",
            "quantity",
            "requested_delivery_date",
            "priority",
            "payment_terms",
          ]}
        />
        <UploadPanel label="Product Master File" requiredColumns={["sku", "product_name", "active"]} />
      </div>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Summary</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <MetricCard label="Total Orders" value={formatNumber(summary.total_orders)} />
          <MetricCard label="Valid Orders" value={formatNumber(summary.valid_orders)} />
          <MetricCard label="Invalid Orders" value={formatNumber(summary.invalid_orders)} />
          <MetricCard label="Duplicate Orders" value={formatNumber(summary.duplicate_orders)} />
          <MetricCard label="Invalid SKUs" value={formatNumber(summary.invalid_skus)} />
          <MetricCard label="Missing Fields" value={formatNumber(summary.missing_field_count)} />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Validation Errors</h2>
        <div className="mt-3">
          <DataTable
            columns={ERROR_COLUMNS}
            data={errors}
            getRowKey={(r) => `${r.row_number}-${r.error_code}`}
            emptyTitle="No validation errors."
            emptyDescription="Every row in the uploaded orders file passed validation."
          />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Valid Orders</h2>
        <div className="mt-3">
          <DataTable
            columns={VALID_ORDER_COLUMNS}
            data={valid_orders}
            getRowKey={(r) => r.order_id}
            emptyTitle="No valid orders yet."
            emptyDescription="No rows in the uploaded orders file passed validation."
          />
        </div>
      </section>
    </div>
  );
}
