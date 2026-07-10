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
import { TableSectionHeading } from "@/components/tables/TableSectionHeading";
import { AgingBucketBars } from "@/components/tables/AgingBucketBars";
import { StatusBadge, agingBucketTone, followUpPriorityTone } from "@/components/workflow/StatusBadge";
import { EmptyState } from "@/components/feedback/EmptyState";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { paymentAgingResult, ninetyPlusDaysAmount, reportManifests } from "@/lib/mock-data";
import { formatAmount, formatDate, formatNumber } from "@/lib/formatters";
import type { DraftMessageRow, PaymentAgingRow, PaymentDataIssueRow } from "@/types";

const STEPS = ["Upload Invoices", "Calculate Aging", "Review Results"];

const AGING_BUCKET_OPTIONS = ["All", "Current", "1-30 Days", "31-60 Days", "61-90 Days", "90+ Days"];
const FOLLOW_UP_PRIORITY_OPTIONS = ["All", "High", "Medium", "Low", "Watch", "None"];

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
  const { summary, aging_rows, data_issues, draft_messages } = paymentAgingResult;
  const report = reportManifests.find((m) => m.report_type === "payment_aging");
  const dateInputId = useId();

  const [bucket, setBucket] = useState("All");
  const [priority, setPriority] = useState("All");
  const [search, setSearch] = useState("");

  const filteredAgingRows = useMemo(() => {
    const query = search.trim().toLowerCase();
    return aging_rows.filter((row) => {
      if (bucket !== "All" && row.aging_bucket !== bucket) return false;
      if (priority !== "All" && row.follow_up_priority !== priority) return false;
      if (query) {
        const haystack = `${row.invoice_id} ${row.customer_name}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });
  }, [aging_rows, bucket, priority, search]);

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
              value={report ? report.generated_at.slice(0, 10) : ""}
              disabled
              readOnly
              title="Live date selection arrives with the API layer (Phase 10) — this reflects the mock report's generated date."
              className="rounded-md border border-border bg-surface-subtle px-2 py-1 text-sm text-text-secondary disabled:cursor-not-allowed"
            />
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
      </div>

      <div className="mt-6">
        <WorkflowStepper steps={STEPS} currentStep={STEPS.length - 1} />
      </div>

      <div className="mt-6">
        <UploadPanel
          label="Invoices File"
          requiredColumns={["invoice_id", "customer_name", "invoice_date", "due_date", "invoice_amount"]}
        />
      </div>

      <section className="mt-6">
        <h2 className="text-base font-semibold text-text-primary">Summary</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            label="Total Outstanding"
            value={formatAmount(summary.total_outstanding_amount)}
            icon={<DollarSign size={16} />}
            tone="info"
          />
          <MetricCard
            label="Overdue Amount"
            value={formatAmount(summary.overdue_amount)}
            icon={<AlertTriangle size={16} />}
            tone="warning"
          />
          <MetricCard
            label="High Priority Count"
            value={formatNumber(summary.high_priority_count)}
            icon={<AlertCircle size={16} />}
            tone="danger"
          />
          <MetricCard
            label="90+ Days Amount"
            value={formatAmount(ninetyPlusDaysAmount(paymentAgingResult))}
            icon={<Clock size={16} />}
            tone="danger"
          />
        </div>
      </section>

      <section className="mt-6">
        <h2 className="text-base font-semibold text-text-primary">Aging Bucket Breakdown</h2>
        <Card className="mt-3">
          <AgingBucketBars counts={summary.aging_bucket_counts} />
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
            data={data_issues}
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
          <DraftMessages messages={draft_messages} />
        </div>
      </section>
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
