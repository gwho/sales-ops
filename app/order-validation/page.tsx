"use client";

// This page must be a Client Component: its DataTable column definitions
// contain render functions, and functions cannot cross the Server->Client
// props boundary. Phase 10: also owns live Workflow Request/Result state.

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
import { EmptyState } from "@/components/feedback/EmptyState";
import { LoadingState } from "@/components/feedback/LoadingState";
import { BusinessErrorMessage } from "@/components/feedback/BusinessErrorMessage";
import { Button } from "@/components/ui/Button";
import { ApiError, downloadBlob, fetchSampleFile, postJSON, postReport } from "@/lib/api-client";
import { formatDate, formatNumber } from "@/lib/formatters";
import type { OrderValidationResult, ValidationErrorRow, ValidOrderRow } from "@/types";

const SEVERITY_OPTIONS = ["All", "Error", "Warning"];
const PRIORITY_OPTIONS = ["All", "High", "Normal", "Low"];

const STEPS = ["Upload Files", "Run Validation", "Review Results"];

type RequestStatus = "idle" | "submitting" | "succeeded" | "failed";
type ReportRequestState = "idle" | "processing" | "failed";

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
  const [ordersFile, setOrdersFile] = useState<File | null>(null);
  const [productMasterFile, setProductMasterFile] = useState<File | null>(null);

  const [status, setStatus] = useState<RequestStatus>("idle");
  const [currentResult, setCurrentResult] = useState<OrderValidationResult | null>(null);
  const [errorDetail, setErrorDetail] = useState<string | null>(null);

  const [reportStatus, setReportStatus] = useState<ReportRequestState>("idle");
  const [reportErrorDetail, setReportErrorDetail] = useState<string | null>(null);

  const [errorSeverity, setErrorSeverity] = useState("All");
  const [errorSearch, setErrorSearch] = useState("");
  const [orderPriority, setOrderPriority] = useState("All");
  const [orderSearch, setOrderSearch] = useState("");

  const [sampleDataLabel, setSampleDataLabel] = useState<string | null>(null);
  const [sampleDataLoading, setSampleDataLoading] = useState(false);

  const canSubmit = ordersFile !== null && productMasterFile !== null;
  const currentStep = status === "succeeded" ? 2 : canSubmit ? 1 : 0;

  async function runValidation(orders: File, productMaster: File) {
    setStatus("submitting");
    setErrorDetail(null);
    try {
      const formData = new FormData();
      formData.set("orders_file", orders);
      formData.set("product_master_file", productMaster);
      const result = await postJSON<OrderValidationResult>("/api/orders/validate", formData);
      setCurrentResult(result);
      setStatus("succeeded");
    } catch (error) {
      setErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
      setStatus("failed");
    }
  }

  function handleRunValidation() {
    if (!ordersFile || !productMasterFile) return;
    void runValidation(ordersFile, productMasterFile);
  }

  async function handleRunSampleData() {
    setSampleDataLoading(true);
    setSampleDataLabel(null);
    setErrorDetail(null);
    try {
      const [orders, productMaster] = await Promise.all([
        fetchSampleFile("orders", "sample_orders.xlsx"),
        fetchSampleFile("product-master", "sample_product_master.xlsx"),
      ]);
      setOrdersFile(orders);
      setProductMasterFile(productMaster);
      setSampleDataLabel(`Using sample data: ${orders.name}, ${productMaster.name}`);
      setSampleDataLoading(false);
      await runValidation(orders, productMaster);
    } catch (error) {
      setSampleDataLoading(false);
      setErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
      setStatus("failed");
    }
  }

  async function handleDownloadReport() {
    if (!ordersFile || !productMasterFile) return;
    setReportStatus("processing");
    setReportErrorDetail(null);
    try {
      const formData = new FormData();
      formData.set("orders_file", ordersFile);
      formData.set("product_master_file", productMasterFile);
      const report = await postReport("/api/orders/validate/report", formData, "order_validation_report.xlsx");
      downloadBlob(report.blob, report.filename);
      setReportStatus("idle");
    } catch (error) {
      setReportErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
      setReportStatus("failed");
    }
  }

  const errors = useMemo(() => currentResult?.errors ?? [], [currentResult]);
  const validOrders = useMemo(() => currentResult?.valid_orders ?? [], [currentResult]);

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
    return validOrders.filter((row) => {
      if (orderPriority !== "All" && row.priority !== orderPriority) return false;
      if (query) {
        const haystack = `${row.order_id} ${row.customer_name} ${row.sku}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });
  }, [validOrders, orderPriority, orderSearch]);

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
        <div className="flex flex-col items-end gap-2">
          <Button
            variant="secondary"
            disabled={!canSubmit || reportStatus === "processing" || status === "submitting" || sampleDataLoading}
            onClick={handleDownloadReport}
            title={canSubmit ? "Recomputes and downloads order_validation_report.xlsx" : "Upload both files first"}
          >
            {reportStatus === "processing" ? "Preparing report…" : "Download Report"}
          </Button>
          {reportStatus === "failed" && reportErrorDetail ? (
            <div className="max-w-xs">
              <BusinessErrorMessage message={reportErrorDetail} />
            </div>
          ) : null}
        </div>
      </div>

      <div className="mt-6">
        <WorkflowStepper steps={STEPS} currentStep={currentStep} />
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
          sampleFileName="orders"
          onFileChange={setOrdersFile}
          selectedFileName={ordersFile?.name ?? null}
        />
        <UploadPanel
          label="Product Master File"
          requiredColumns={["sku", "product_name", "active"]}
          sampleFileName="product-master"
          onFileChange={setProductMasterFile}
          selectedFileName={productMasterFile?.name ?? null}
        />
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <Button onClick={handleRunValidation} disabled={!canSubmit || status === "submitting" || sampleDataLoading}>
          {status === "submitting" ? "Validating…" : "Run Validation"}
        </Button>
        <Button
          variant="secondary"
          onClick={handleRunSampleData}
          disabled={sampleDataLoading || status === "submitting"}
          title="Fetches the committed sample workbooks and runs validation on them"
        >
          {sampleDataLoading ? "Loading sample data…" : "Run sample data"}
        </Button>
        {sampleDataLabel ? <span className="text-xs text-text-muted">{sampleDataLabel}</span> : null}
      </div>

      {status === "idle" ? (
        <div className="mt-6">
          <EmptyState
            title="Upload an orders file and product master file to begin validation."
            description="Both files are required before validation can run."
          />
        </div>
      ) : null}

      {status === "submitting" ? (
        <div className="mt-6">
          <LoadingState label="Validating orders…" />
        </div>
      ) : null}

      {status === "failed" && errorDetail ? (
        <div className="mt-6">
          <BusinessErrorMessage message={errorDetail} />
        </div>
      ) : null}

      {status === "succeeded" && currentResult ? (
        <>
          <section className="mt-6">
            <h2 className="text-base font-semibold text-text-primary">Summary</h2>
            <div className="mt-3 grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
              <MetricCard
                label="Total Orders"
                value={formatNumber(currentResult.summary.total_orders)}
                icon={<ClipboardList size={16} />}
                tone="info"
              />
              <MetricCard
                label="Valid Orders"
                value={formatNumber(currentResult.summary.valid_orders)}
                icon={<CheckCircle2 size={16} />}
                tone="success"
              />
              <MetricCard
                label="Invalid Orders"
                value={formatNumber(currentResult.summary.invalid_orders)}
                icon={<XCircle size={16} />}
                tone="danger"
              />
              <MetricCard
                label="Duplicate Orders"
                value={formatNumber(currentResult.summary.duplicate_orders)}
                icon={<Copy size={16} />}
                tone="warning"
              />
              <MetricCard
                label="Invalid SKUs"
                value={formatNumber(currentResult.summary.invalid_skus)}
                icon={<AlertCircle size={16} />}
                tone="danger"
              />
              <MetricCard
                label="Missing Fields"
                value={formatNumber(currentResult.summary.missing_field_count)}
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
        </>
      ) : null}
    </div>
  );
}
