"use client";

// See app/order-validation/page.tsx for why this page must be a Client
// Component (its DataTable column configs contain render functions).

// Internal imports
import { MetricCard } from "@/components/workflow/MetricCard";
import { UploadPanel } from "@/components/workflow/UploadPanel";
import { WorkflowStepper } from "@/components/workflow/WorkflowStepper";
import { DataTable, type DataTableColumn } from "@/components/tables/DataTable";
import { StatusBadge, agingBucketTone, followUpPriorityTone } from "@/components/workflow/StatusBadge";
import { EmptyState } from "@/components/feedback/EmptyState";
import { Card } from "@/components/ui/Card";
import { paymentAgingResult, ninetyPlusDaysAmount } from "@/lib/mock-data";
import { formatAmount, formatDate, formatNumber } from "@/lib/formatters";
import type { DraftMessageRow, PaymentAgingRow, PaymentAgingSummary, PaymentDataIssueRow } from "@/types";

const STEPS = ["Upload Invoices", "Calculate Aging", "Review Results"];

const AGING_ROW_COLUMNS: DataTableColumn<PaymentAgingRow>[] = [
  { key: "invoice_id", header: "Invoice ID", render: (r) => r.invoice_id },
  { key: "customer_name", header: "Customer", render: (r) => r.customer_name },
  { key: "invoice_date", header: "Invoice Date", render: (r) => formatDate(r.invoice_date) },
  { key: "due_date", header: "Due Date", render: (r) => formatDate(r.due_date) },
  { key: "invoice_amount", header: "Invoice Amount", render: (r) => formatAmount(r.invoice_amount) },
  { key: "paid_amount", header: "Paid Amount", render: (r) => formatAmount(r.paid_amount) },
  { key: "outstanding_amount", header: "Outstanding", render: (r) => formatAmount(r.outstanding_amount) },
  {
    key: "days_overdue",
    header: "Days Overdue",
    render: (r) => formatNumber(r.days_overdue),
    sortable: true,
    sortValue: (r) => r.days_overdue,
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
  { key: "suggested_action", header: "Suggested Action", render: (r) => r.suggested_action },
];

const DATA_ISSUE_COLUMNS: DataTableColumn<PaymentDataIssueRow>[] = [
  { key: "invoice_id", header: "Invoice ID", render: (r) => r.invoice_id ?? "—" },
  { key: "customer_name", header: "Customer", render: (r) => r.customer_name ?? "—" },
  { key: "error_code", header: "Error Code", render: (r) => r.error_code },
  { key: "error_message", header: "Error Message", render: (r) => r.error_message },
  {
    key: "severity",
    header: "Severity",
    render: (r) => <StatusBadge status={r.severity} tone="danger" />,
  },
];

// Component
export default function PaymentAgingPage() {
  const { summary, aging_rows, data_issues, draft_messages } = paymentAgingResult;

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-2xl font-semibold text-text-primary">Payment Aging</h1>
      <p className="mt-2 text-sm text-text-secondary">
        Track outstanding invoices, aging buckets, and follow-up priority.
      </p>

      <div className="mt-6">
        <WorkflowStepper steps={STEPS} currentStep={STEPS.length - 1} />
      </div>

      <div className="mt-6">
        <UploadPanel
          label="Invoices File"
          requiredColumns={["invoice_id", "customer_name", "invoice_date", "due_date", "invoice_amount"]}
        />
      </div>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Summary</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Total Outstanding" value={formatAmount(summary.total_outstanding_amount)} />
          <MetricCard label="Overdue Amount" value={formatAmount(summary.overdue_amount)} />
          <MetricCard label="High Priority Count" value={formatNumber(summary.high_priority_count)} />
          <MetricCard label="90+ Days Amount" value={formatAmount(ninetyPlusDaysAmount(paymentAgingResult))} />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Aging Bucket Breakdown</h2>
        <Card className="mt-3">
          <AgingBucketBars counts={summary.aging_bucket_counts} />
        </Card>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Payment Aging</h2>
        <div className="mt-3">
          <DataTable
            columns={AGING_ROW_COLUMNS}
            data={aging_rows}
            getRowKey={(r) => r.invoice_id}
            emptyTitle="No invoices to age."
          />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Data Issues</h2>
        <div className="mt-3">
          <DataTable
            columns={DATA_ISSUE_COLUMNS}
            data={data_issues}
            getRowKey={(r) => `${r.invoice_id ?? "unknown"}-${r.error_code}`}
            emptyTitle="No data issues."
            emptyDescription="Every invoice row had a usable due date and amount."
          />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Draft Messages</h2>
        <div className="mt-3">
          <DraftMessages messages={draft_messages} />
        </div>
      </section>
    </div>
  );
}

function AgingBucketBars({ counts }: { counts: PaymentAgingSummary["aging_bucket_counts"] }) {
  const entries = Object.entries(counts) as [keyof PaymentAgingSummary["aging_bucket_counts"], number][];
  const max = Math.max(1, ...entries.map(([, count]) => count));

  return (
    <div className="flex flex-col gap-2">
      {entries.map(([bucket, count]) => (
        <div key={bucket} className="flex items-center gap-3">
          <span className="w-24 shrink-0 text-xs text-text-secondary">{bucket}</span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-muted">
            <div className="h-full rounded-full bg-accent" style={{ width: `${(count / max) * 100}%` }} />
          </div>
          <span className="w-6 shrink-0 text-right text-xs text-text-secondary">{count}</span>
        </div>
      ))}
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
