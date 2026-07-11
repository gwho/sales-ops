"use client";

// See app/order-validation/page.tsx for why this page must be a Client
// Component (its DataTable column configs contain render functions).

// External imports
import { useId, useMemo, useState } from "react";
import { DollarSign, AlertTriangle, AlertCircle, Clock, ReceiptText, Mail } from "lucide-react";

// Internal imports
import { MetricCard } from "@/components/workflow/MetricCard";
import { UploadPanel } from "@/components/workflow/UploadPanel";
import { WorkflowStepper } from "@/components/workflow/WorkflowStepper";
import { DataTable, type DataTableColumn } from "@/components/tables/DataTable";
import { FilterToolbar } from "@/components/tables/FilterToolbar";
import { FilterSelect } from "@/components/tables/FilterSelect";
import { AgingBucketBars } from "@/components/tables/AgingBucketBars";
import { TableSectionHeading } from "@/components/tables/TableSectionHeading";
import { StatusBadge, agingBucketTone, followUpPriorityTone } from "@/components/workflow/StatusBadge";
import { EmptyState } from "@/components/feedback/EmptyState";
import { LoadingState } from "@/components/feedback/LoadingState";
import { BusinessErrorMessage } from "@/components/feedback/BusinessErrorMessage";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ApiError, downloadBlob, fetchSampleFile, postJSON, postReport } from "@/lib/api-client";
import { formatAmount, formatDate, formatNumber } from "@/lib/formatters";
import type { DraftMessageRow, PaymentAgingResult, PaymentAgingRow, PaymentDataIssueRow } from "@/types";

const STEPS = ["Upload Invoices", "Calculate Aging", "Review Results"];

const AGING_BUCKET_OPTIONS = ["All", "Current", "1-30 Days", "31-60 Days", "61-90 Days", "90+ Days"];
const FOLLOW_UP_PRIORITY_OPTIONS = ["All", "High", "Medium", "Low", "Watch", "None"];

type RequestStatus = "idle" | "submitting" | "succeeded" | "failed";
type ReportRequestState = "idle" | "processing" | "failed";

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10);
}

/** Sums outstanding_amount for 90+ Days rows -- a derived display-only aggregate (ui-contract-plan.md), not new business logic. */
function ninetyPlusDaysAmount(result: PaymentAgingResult): number {
  return result.aging_rows
    .filter((row) => row.aging_bucket === "90+ Days")
    .reduce((sum, row) => sum + row.outstanding_amount, 0);
}

const AGING_ROW_COLUMNS: DataTableColumn<PaymentAgingRow>[] = [
  {
    key: "invoice_id",
    header: "Invoice ID",
    render: (r) => <span className="font-medium text-text-primary">{r.invoice_id}</span>,
    sortable: true,
    sortValue: (r) => r.invoice_id,
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
  {
    key: "invoice_date",
    header: "Invoice Date",
    render: (r) => <span className="text-text-secondary">{formatDate(r.invoice_date)}</span>,
    sortable: true,
    sortValue: (r) => r.invoice_date,
  },
  {
    key: "due_date",
    header: "Due Date",
    render: (r) => <span className="text-text-secondary">{formatDate(r.due_date)}</span>,
    sortable: true,
    sortValue: (r) => r.due_date,
  },
  {
    key: "invoice_amount",
    header: "Invoice Amount",
    render: (r) => <span className="font-medium tabular-nums">{formatAmount(r.invoice_amount)}</span>,
    sortable: true,
    sortValue: (r) => r.invoice_amount,
    align: "right",
  },
  {
    key: "paid_amount",
    header: "Paid Amount",
    render: (r) => <span className="tabular-nums text-text-secondary">{formatAmount(r.paid_amount)}</span>,
    sortable: true,
    sortValue: (r) => r.paid_amount,
    align: "right",
  },
  {
    key: "outstanding_amount",
    header: "Outstanding",
    render: (r) => <span className="font-semibold tabular-nums text-text-primary">{formatAmount(r.outstanding_amount)}</span>,
    sortable: true,
    sortValue: (r) => r.outstanding_amount,
    align: "right",
  },
  {
    key: "days_overdue",
    header: "Days Overdue",
    render: (r) => <span className="font-medium tabular-nums">{formatNumber(r.days_overdue)}</span>,
    sortable: true,
    sortValue: (r) => r.days_overdue,
    align: "right",
  },
  {
    key: "aging_bucket",
    header: "Aging Bucket",
    render: (r) => <StatusBadge status={r.aging_bucket} tone={agingBucketTone(r.aging_bucket)} />,
    sortable: true,
    sortValue: (r) => r.aging_bucket,
  },
  {
    key: "follow_up_priority",
    header: "Follow-up Priority",
    render: (r) => <StatusBadge status={r.follow_up_priority} tone={followUpPriorityTone(r.follow_up_priority)} />,
    sortable: true,
    sortValue: (r) => r.follow_up_priority,
  },
  {
    key: "suggested_action",
    header: "Suggested Action",
    render: (r) => (
      <span className="block max-w-[220px] truncate" title={r.suggested_action}>
        {r.suggested_action}
      </span>
    ),
  },
];

const DATA_ISSUE_COLUMNS: DataTableColumn<PaymentDataIssueRow>[] = [
  { key: "invoice_id", header: "Invoice ID", render: (r) => <span className="font-medium text-text-primary">{r.invoice_id ?? "—"}</span> },
  { key: "customer_name", header: "Customer", render: (r) => <span className="font-medium text-text-primary">{r.customer_name ?? "—"}</span> },
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
    render: (r) => <StatusBadge status={r.severity} tone="danger" />,
  },
];

// Component
export default function PaymentAgingPage() {
  const dateInputId = useId();

  const [invoicesFile, setInvoicesFile] = useState<File | null>(null);
  const [asOfDate, setAsOfDate] = useState<string>(() => todayIsoDate());

  const [status, setStatus] = useState<RequestStatus>("idle");
  const [currentResult, setCurrentResult] = useState<PaymentAgingResult | null>(null);
  const [errorDetail, setErrorDetail] = useState<string | null>(null);

  const [reportStatus, setReportStatus] = useState<ReportRequestState>("idle");
  const [reportErrorDetail, setReportErrorDetail] = useState<string | null>(null);

  const [sampleDataLabel, setSampleDataLabel] = useState<string | null>(null);
  const [sampleDataLoading, setSampleDataLoading] = useState(false);

  const canSubmit = invoicesFile !== null && asOfDate !== "";
  const currentStep = status === "succeeded" ? 2 : canSubmit ? 1 : 0;

  function buildFormData(invoices: File, forDate: string): FormData {
    const formData = new FormData();
    formData.set("invoices_file", invoices);
    formData.set("as_of_date", forDate);
    return formData;
  }

  async function runAging(invoices: File, forDate: string) {
    setStatus("submitting");
    setErrorDetail(null);
    try {
      const result = await postJSON<PaymentAgingResult>("/api/payments/aging", buildFormData(invoices, forDate));
      setCurrentResult(result);
      setStatus("succeeded");
    } catch (error) {
      setErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
      setStatus("failed");
    }
  }

  function handleCalculateAging() {
    if (!invoicesFile || asOfDate === "") return;
    void runAging(invoicesFile, asOfDate);
  }

  async function handleRunSampleData() {
    setSampleDataLoading(true);
    setSampleDataLabel(null);
    setErrorDetail(null);
    try {
      const invoices = await fetchSampleFile("invoices", "sample_invoices.xlsx");
      setInvoicesFile(invoices);
      setSampleDataLabel(`Using sample data: ${invoices.name} (as of ${asOfDate})`);
      setSampleDataLoading(false);
      await runAging(invoices, asOfDate);
    } catch (error) {
      setSampleDataLoading(false);
      setErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
      setStatus("failed");
    }
  }

  async function handleDownloadReport() {
    if (!invoicesFile || asOfDate === "") return;
    setReportStatus("processing");
    setReportErrorDetail(null);
    try {
      const report = await postReport(
        "/api/payments/aging/report",
        buildFormData(invoicesFile, asOfDate),
        "payment_aging_report.xlsx",
      );
      downloadBlob(report.blob, report.filename);
      setReportStatus("idle");
    } catch (error) {
      setReportErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
      setReportStatus("failed");
    }
  }

  const agingRows = useMemo(() => currentResult?.aging_rows ?? [], [currentResult]);
  const dataIssues = useMemo(() => currentResult?.data_issues ?? [], [currentResult]);
  const draftMessages = useMemo(() => currentResult?.draft_messages ?? [], [currentResult]);

  const [bucket, setBucket] = useState("All");
  const [priority, setPriority] = useState("All");
  const [search, setSearch] = useState("");

  const filteredAgingRows = useMemo(() => {
    const query = search.trim().toLowerCase();
    return agingRows.filter((row) => {
      if (bucket !== "All" && row.aging_bucket !== bucket) return false;
      if (priority !== "All" && row.follow_up_priority !== priority) return false;
      if (query) {
        const haystack = `${row.invoice_id} ${row.customer_name}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });
  }, [agingRows, bucket, priority, search]);

  const agingFiltersActive = bucket !== "All" || priority !== "All" || search !== "";

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Payment Aging</h1>
          <p className="mt-2 text-sm text-text-secondary">
            Track outstanding invoices, aging buckets, and follow-up priority.
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="flex flex-col items-end gap-1">
            <label htmlFor={dateInputId} className="text-xs font-medium uppercase tracking-wide text-text-secondary">
              As of Date
            </label>
            <input
              id={dateInputId}
              type="date"
              value={asOfDate}
              onChange={(event) => setAsOfDate(event.target.value)}
              title="Recalculates aging buckets, days overdue, and follow-up priority against this date"
              className="rounded-md border border-border bg-surface px-2 py-1 text-sm text-text-primary"
            />
          </div>
          <Button
            variant="secondary"
            disabled={!canSubmit || reportStatus === "processing"}
            onClick={handleDownloadReport}
            title={canSubmit ? "Recomputes and downloads payment_aging_report.xlsx" : "Upload an invoices file first"}
          >
            {reportStatus === "processing" ? "Preparing report…" : "Download Report"}
          </Button>
          {reportStatus === "failed" && reportErrorDetail ? (
            <p className="max-w-xs text-right text-xs text-danger">{reportErrorDetail}</p>
          ) : null}
        </div>
      </div>

      <div className="mt-6">
        <WorkflowStepper steps={STEPS} currentStep={currentStep} />
      </div>

      <div className="mt-6">
        <UploadPanel
          label="Invoices File"
          requiredColumns={["invoice_id", "customer_name", "invoice_date", "due_date", "invoice_amount"]}
          sampleFileName="invoices"
          onFileChange={setInvoicesFile}
        />
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <Button onClick={handleCalculateAging} disabled={!canSubmit || status === "submitting"}>
          {status === "submitting" ? "Calculating…" : "Calculate Aging"}
        </Button>
        <Button
          variant="secondary"
          onClick={handleRunSampleData}
          disabled={sampleDataLoading || status === "submitting"}
          title="Fetches the committed sample invoices and calculates aging as of the selected date"
        >
          {sampleDataLoading ? "Loading sample data…" : "Run sample data"}
        </Button>
        {sampleDataLabel ? <span className="text-xs text-text-muted">{sampleDataLabel}</span> : null}
      </div>

      {status === "idle" ? (
        <div className="mt-6">
          <EmptyState
            title="Upload an invoice/payment file to generate an aging report."
            description="An invoices file and an as-of date are required."
          />
        </div>
      ) : null}

      {status === "submitting" ? (
        <div className="mt-6">
          <LoadingState label="Calculating outstanding amounts, aging buckets, and follow-up priority…" />
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
            <div className="mt-3 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <MetricCard
                label="Total Outstanding"
                value={formatAmount(currentResult.summary.total_outstanding_amount)}
                icon={<DollarSign size={16} />}
                tone="info"
              />
              <MetricCard
                label="Overdue Amount"
                value={formatAmount(currentResult.summary.overdue_amount)}
                icon={<AlertTriangle size={16} />}
                tone="warning"
              />
              <MetricCard
                label="High Priority Count"
                value={formatNumber(currentResult.summary.high_priority_count)}
                icon={<AlertCircle size={16} />}
                tone="danger"
              />
              <MetricCard
                label="90+ Days Amount"
                value={formatAmount(ninetyPlusDaysAmount(currentResult))}
                icon={<Clock size={16} />}
                tone="danger"
              />
            </div>
          </section>

          <section className="mt-6">
            <h2 className="text-base font-semibold text-text-primary">Aging Bucket Breakdown</h2>
            <Card className="mt-3">
              <AgingBucketBars counts={currentResult.summary.aging_bucket_counts} />
            </Card>
          </section>

          <section className="mt-6">
            <TableSectionHeading
              icon={<ReceiptText size={16} />}
              title="Payment Aging"
              caption="Outstanding amount → aging bucket → follow-up priority."
            />
            <div className="mt-3 flex flex-col gap-3">
              <FilterToolbar
                search={{ value: search, onChange: setSearch, placeholder: "Invoice ID or customer…" }}
                onClear={() => {
                  setBucket("All");
                  setPriority("All");
                  setSearch("");
                }}
                hasActiveFilters={agingFiltersActive}
              >
                <FilterSelect label="Aging Bucket" value={bucket} options={AGING_BUCKET_OPTIONS} onChange={setBucket} />
                <FilterSelect
                  label="Follow-up Priority"
                  value={priority}
                  options={FOLLOW_UP_PRIORITY_OPTIONS}
                  onChange={setPriority}
                />
              </FilterToolbar>
              <DataTable
                columns={AGING_ROW_COLUMNS}
                data={filteredAgingRows}
                getRowKey={(r) => r.invoice_id}
                emptyTitle={agingFiltersActive ? "No invoices match the current filter." : "No invoices to age."}
                emptyDescription={agingFiltersActive ? "Try a different bucket, priority, or search term." : undefined}
              />
            </div>
          </section>

          <section className="mt-6">
            <TableSectionHeading
              icon={<AlertCircle size={16} />}
              title="Data Issues"
              caption="Rows that couldn't be aged due to a missing or invalid due date or amount."
            />
            <div className="mt-3 rounded-xl border border-border bg-surface-subtle p-4">
              <DataTable
                columns={DATA_ISSUE_COLUMNS}
                data={dataIssues}
                getRowKey={(r) => `${r.invoice_id ?? "unknown"}-${r.error_code}`}
                emptyTitle="No data issues."
                emptyDescription="Every invoice row had a usable due date and amount."
              />
            </div>
          </section>

          <section className="mt-6">
            <TableSectionHeading
              icon={<Mail size={16} />}
              title="Draft Messages"
              caption="Ready-to-send reminders for overdue High/Medium/Low priority invoices."
            />
            <div className="mt-3">
              <DraftMessages messages={draftMessages} />
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}

function DraftMessages({ messages }: { messages: DraftMessageRow[] }) {
  if (messages.length === 0) {
    return (
      <EmptyState
        title="No draft reminders."
        description="No overdue invoices currently need a follow-up message."
      />
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {messages.map((message) => (
        <Card key={message.invoice_id} className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
            <span className="font-semibold text-text-primary">
              {message.invoice_id} — {message.customer_name}
            </span>
            <span className="text-text-secondary">
              {formatAmount(message.outstanding_amount)} · {message.days_overdue} days overdue
            </span>
          </div>
          <p className="whitespace-pre-line rounded-md bg-surface-muted p-3 text-sm text-text-primary">
            {message.message_text}
          </p>
        </Card>
      ))}
    </div>
  );
}
