"use client";

// This page must be a Client Component: its DataTable column definitions
// contain render functions, and functions cannot cross the Server->Client
// props boundary (only the DataTable primitive itself strictly needed to be
// client — but its callers do too, since they construct its column config).

// External imports
import { useMemo, useState } from "react";
import {
  ClipboardList,
  CheckCircle2,
  XCircle,
  Copy,
  AlertCircle,
  FileWarning,
  AlertTriangle,
} from "lucide-react";

// Internal imports
import { MetricCard } from "@/components/workflow/MetricCard";
import { UploadPanel } from "@/components/workflow/UploadPanel";
import { WorkflowStepper } from "@/components/workflow/WorkflowStepper";
import { DataTable, type DataTableColumn } from "@/components/tables/DataTable";
import { FilterToolbar } from "@/components/tables/FilterToolbar";
import { FilterSelect } from "@/components/tables/FilterSelect";
import { TableSectionHeading } from "@/components/tables/TableSectionHeading";
import { StatusBadge, severityTone, importancePriorityTone } from "@/components/workflow/StatusBadge";
import { Button } from "@/components/ui/Button";
import { orderValidationResult, reportManifests } from "@/lib/mock-data";
import { formatDate, formatNumber } from "@/lib/formatters";
import type { ValidationErrorRow, ValidOrderRow } from "@/types";

const SEVERITY_OPTIONS = ["All", "Error", "Warning"];
const PRIORITY_OPTIONS = ["All", "High", "Normal", "Low"];

const STEPS = ["Upload Files", "Run Validation", "Review Results"];

const ERROR_COLUMNS: DataTableColumn<ValidationErrorRow>[] = [
  { key: "row_number", header: "Row", render: (r) => r.row_number, sortable: true, sortValue: (r) => r.row_number, align: "right" },
  {
    key: "order_id",
    header: "Order ID",
    render: (r) => <span className="font-medium text-text-primary">{r.order_id ?? "—"}</span>,
    sortable: true,
    sortValue: (r) => r.order_id ?? "",
  },
  {
    key: "sku",
    header: "SKU",
    render: (r) => <span className="font-medium text-text-primary">{r.sku ?? "—"}</span>,
    sortable: true,
    sortValue: (r) => r.sku ?? "",
  },
  { key: "error_code", header: "Error Code", render: (r) => <span className="text-text-secondary">{r.error_code}</span> },
  {
    key: "error_message",
    header: "Error Message",
    render: (r) => (
      <span className="block max-w-[280px] truncate" title={r.error_message}>
        {r.error_message}
      </span>
    ),
  },
  {
    key: "severity",
    header: "Severity",
    render: (r) => <StatusBadge status={r.severity} tone={severityTone(r.severity)} />,
  },
];

const VALID_ORDER_COLUMNS: DataTableColumn<ValidOrderRow>[] = [
  {
    key: "order_id",
    header: "Order ID",
    render: (r) => <span className="font-medium text-text-primary">{r.order_id}</span>,
    sortable: true,
    sortValue: (r) => r.order_id,
  },
  {
    key: "order_date",
    header: "Order Date",
    render: (r) => <span className="text-text-secondary">{formatDate(r.order_date)}</span>,
    sortable: true,
    sortValue: (r) => r.order_date,
  },
  {
    key: "customer_name",
    header: "Customer",
    render: (r) => (
      <span className="block max-w-[160px] truncate font-medium text-text-primary" title={r.customer_name}>
        {r.customer_name}
      </span>
    ),
    sortable: true,
    sortValue: (r) => r.customer_name,
  },
  { key: "customer_region", header: "Region", render: (r) => <span className="text-text-secondary">{r.customer_region}</span> },
  {
    key: "sku",
    header: "SKU",
    render: (r) => <span className="font-medium text-text-primary">{r.sku}</span>,
    sortable: true,
    sortValue: (r) => r.sku,
  },
  {
    key: "product_name",
    header: "Product",
    render: (r) => (
      <span className="block max-w-[160px] truncate text-text-secondary" title={r.product_name ?? undefined}>
        {r.product_name ?? "—"}
      </span>
    ),
  },
  {
    key: "quantity",
    header: "Qty",
    render: (r) => <span className="font-medium tabular-nums">{formatNumber(r.quantity)}</span>,
    sortable: true,
    sortValue: (r) => r.quantity,
    align: "right",
  },
  {
    key: "requested_delivery_date",
    header: "Requested Delivery",
    render: (r) => <span className="text-text-secondary">{formatDate(r.requested_delivery_date)}</span>,
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
  { key: "payment_terms", header: "Payment Terms", render: (r) => <span className="text-text-secondary">{r.payment_terms}</span> },
  { key: "sales_owner", header: "Sales Owner", render: (r) => <span className="text-text-muted">{r.sales_owner ?? "—"}</span> },
];

// Component
export default function OrderValidationPage() {
  const { summary, errors, valid_orders } = orderValidationResult;
  const report = reportManifests.find((m) => m.report_type === "order_validation");

  const [errorSeverity, setErrorSeverity] = useState("All");
  const [errorSearch, setErrorSearch] = useState("");
  const [orderPriority, setOrderPriority] = useState("All");
  const [orderSearch, setOrderSearch] = useState("");

  const filteredErrors = useMemo(() => {
    const query = errorSearch.trim().toLowerCase();
    return errors.filter((row) => {
      if (errorSeverity !== "All" && row.severity !== errorSeverity) return false;
      if (query) {
        const haystack = `${row.order_id ?? ""} ${row.sku ?? ""}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });
  }, [errors, errorSeverity, errorSearch]);

  const filteredValidOrders = useMemo(() => {
    const query = orderSearch.trim().toLowerCase();
    return valid_orders.filter((row) => {
      if (orderPriority !== "All" && row.priority !== orderPriority) return false;
      if (query) {
        const haystack = `${row.order_id} ${row.customer_name} ${row.sku}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });
  }, [valid_orders, orderPriority, orderSearch]);

  const errorFiltersActive = errorSeverity !== "All" || errorSearch !== "";
  const orderFiltersActive = orderPriority !== "All" || orderSearch !== "";

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Order Validation</h1>
          <p className="mt-2 text-sm text-text-secondary">
            Check orders against required fields, active SKUs, and business rules.
          </p>
        </div>
        <Button
          variant="secondary"
          disabled
          title={
            report
              ? `Download ${report.file_name} — available once the API layer (Phase 10) is live`
              : "Available once the API layer (Phase 10) is live"
          }
        >
          Download Report
        </Button>
      </div>

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

      <section className="mt-6">
        <h2 className="text-base font-semibold text-text-primary">Summary</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <MetricCard
            label="Total Orders"
            value={formatNumber(summary.total_orders)}
            icon={<ClipboardList size={16} />}
            tone="info"
          />
          <MetricCard
            label="Valid Orders"
            value={formatNumber(summary.valid_orders)}
            icon={<CheckCircle2 size={16} />}
            tone="success"
          />
          <MetricCard
            label="Invalid Orders"
            value={formatNumber(summary.invalid_orders)}
            icon={<XCircle size={16} />}
            tone="danger"
          />
          <MetricCard
            label="Duplicate Orders"
            value={formatNumber(summary.duplicate_orders)}
            icon={<Copy size={16} />}
            tone="warning"
          />
          <MetricCard
            label="Invalid SKUs"
            value={formatNumber(summary.invalid_skus)}
            icon={<AlertCircle size={16} />}
            tone="danger"
          />
          <MetricCard
            label="Missing Fields"
            value={formatNumber(summary.missing_field_count)}
            icon={<FileWarning size={16} />}
            tone="warning"
          />
        </div>
      </section>

      <section className="mt-6">
        <TableSectionHeading
          icon={<AlertTriangle size={16} />}
          title="Validation Errors"
          caption="Row → error code → business-readable message."
        />
        <div className="mt-3 flex flex-col gap-3">
          <FilterToolbar
            search={{ value: errorSearch, onChange: setErrorSearch, placeholder: "Order ID or SKU…" }}
            onClear={() => {
              setErrorSeverity("All");
              setErrorSearch("");
            }}
            hasActiveFilters={errorFiltersActive}
          >
            <FilterSelect label="Severity" value={errorSeverity} options={SEVERITY_OPTIONS} onChange={setErrorSeverity} />
          </FilterToolbar>
          <DataTable
            columns={ERROR_COLUMNS}
            data={filteredErrors}
            getRowKey={(r) => `${r.row_number}-${r.error_code}`}
            emptyTitle={errorFiltersActive ? "No errors match the current filter." : "No validation errors."}
            emptyDescription={
              errorFiltersActive
                ? "Try a different severity or search term."
                : "Every row in the uploaded orders file passed validation."
            }
          />
        </div>
      </section>

      <section className="mt-6">
        <TableSectionHeading
          icon={<CheckCircle2 size={16} />}
          title="Valid Orders"
          caption="Validated orders → allocation-ready rows."
        />
        <div className="mt-3 flex flex-col gap-3">
          <FilterToolbar
            search={{ value: orderSearch, onChange: setOrderSearch, placeholder: "Order ID, customer, or SKU…" }}
            onClear={() => {
              setOrderPriority("All");
              setOrderSearch("");
            }}
            hasActiveFilters={orderFiltersActive}
          >
            <FilterSelect label="Priority" value={orderPriority} options={PRIORITY_OPTIONS} onChange={setOrderPriority} />
          </FilterToolbar>
          <DataTable
            columns={VALID_ORDER_COLUMNS}
            data={filteredValidOrders}
            getRowKey={(r) => r.order_id}
            emptyTitle={orderFiltersActive ? "No orders match the current filter." : "No valid orders yet."}
            emptyDescription={
              orderFiltersActive
                ? "Try a different priority or search term."
                : "No rows in the uploaded orders file passed validation."
            }
          />
        </div>
      </section>
    </div>
  );
}
