// External imports
import Link from "next/link";
import {
  ClipboardList,
  CheckCircle2,
  XCircle,
  AlertCircle,
  AlertTriangle,
  Clock,
  Truck,
  ReceiptText,
  FileSpreadsheet,
  Upload,
  PackageCheck,
  ArrowRight,
  BookOpen,
} from "lucide-react";

// Internal imports
import { MetricCard } from "@/components/workflow/MetricCard";
import { ReportCard } from "@/components/workflow/ReportCard";
import { TableSectionHeading } from "@/components/tables/TableSectionHeading";
import { DonutBreakdownChart } from "@/components/charts/DonutBreakdownChart";
import { VerticalBucketBarChart } from "@/components/charts/VerticalBucketBarChart";
import {
  StatusBadge,
  followUpPriorityTone,
  agingBucketTone,
  allocationStatusTone,
} from "@/components/workflow/StatusBadge";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeaderCell,
  TableCell,
} from "@/components/ui/Table";
import { Card } from "@/components/ui/Card";
import {
  orderValidationResult,
  inventoryAllocationResult,
  paymentAgingResult,
  reportManifests,
  amountByAgingBucket,
} from "@/lib/mock-data";
import { formatAmount, formatNumber } from "@/lib/formatters";

const WORKFLOW_ENTRIES = [
  {
    href: "/order-validation",
    label: "Validate Orders",
    description: "Check orders against required fields, SKUs, and business rules.",
  },
  {
    href: "/inventory-allocation",
    label: "Allocate Inventory",
    description: "Allocate stock by priority, delivery date, and warehouse availability.",
  },
  {
    href: "/payment-aging",
    label: "Review Payment Aging",
    description: "Track outstanding invoices, aging buckets, and follow-up priority.",
  },
] as const;

// Component
export default function DashboardPage() {
  const validation = orderValidationResult.summary;
  const allocation = inventoryAllocationResult.summary;
  const aging = paymentAgingResult.summary;
  const { supplier_follow_ups } = inventoryAllocationResult;
  const followUpItems = paymentAgingResult.aging_rows.filter((row) => row.follow_up_priority !== "None");

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <p className="text-xs font-medium uppercase tracking-wide text-text-secondary">
        Sales Admin Automation Toolkit
      </p>
      <h1 className="mt-1 text-2xl font-semibold text-text-primary">Dashboard</h1>
      <p className="mt-2 text-sm text-text-secondary">
        A read-only snapshot of this session&apos;s order validation, inventory allocation, and
        payment aging results.
      </p>

      <section className="mt-6">
        <h2 className="text-base font-semibold text-text-primary">Overview</h2>
        <div className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          <MetricCard
            label="Total Orders"
            value={formatNumber(validation.total_orders)}
            icon={<ClipboardList size={16} />}
            tone="info"
          />
          <MetricCard
            label="Invalid Orders"
            value={formatNumber(validation.invalid_orders)}
            icon={<XCircle size={16} />}
            tone="danger"
          />
          <MetricCard
            label="Fully Allocated"
            value={formatNumber(allocation.fully_allocated_count)}
            icon={<CheckCircle2 size={16} />}
            tone="success"
          />
          <MetricCard
            label="Backordered"
            value={formatNumber(allocation.backordered_count)}
            icon={<Truck size={16} />}
            tone="danger"
          />
          <MetricCard
            label="Overdue Amount"
            value={formatAmount(aging.overdue_amount)}
            icon={<AlertTriangle size={16} />}
            tone="warning"
          />
        </div>
      </section>

      <section className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card className="transition-shadow hover:border-border-strong hover:shadow-md">
          <TableSectionHeading
            icon={<PackageCheck size={16} />}
            title="Allocation Status"
            caption="Fully allocated → partially allocated → backordered."
            action={
              <Link href="/inventory-allocation" className="text-xs font-medium text-accent hover:text-accent-hover">
                View all
              </Link>
            }
          />
          <div className="mt-3 flex min-h-48 flex-col justify-center">
            <DonutBreakdownChart
              segments={[
                {
                  label: "Fully Allocated",
                  value: allocation.fully_allocated_count,
                  tone: allocationStatusTone("Fully Allocated"),
                },
                {
                  label: "Partially Allocated",
                  value: allocation.partially_allocated_count,
                  tone: allocationStatusTone("Partially Allocated"),
                },
                {
                  label: "Backordered",
                  value: allocation.backordered_count,
                  tone: allocationStatusTone("Backordered"),
                },
              ]}
              totalLabel="Order Lines"
            />
          </div>
        </Card>
        <Card className="transition-shadow hover:border-border-strong hover:shadow-md">
          <TableSectionHeading
            icon={<ReceiptText size={16} />}
            title="Outstanding by Aging Bucket"
            caption="Outstanding amount → aging bucket."
            action={
              <Link href="/payment-aging" className="text-xs font-medium text-accent hover:text-accent-hover">
                AR report
              </Link>
            }
          />
          <div className="mt-3 flex min-h-48 flex-col justify-center">
            <VerticalBucketBarChart
              data={amountByAgingBucket(paymentAgingResult).map((bucket) => ({
                label: bucket.label,
                value: bucket.value,
                tone: agingBucketTone(bucket.label),
              }))}
              subtitle="Outstanding amount by bucket"
            />
          </div>
        </Card>
      </section>

      <section className="mt-6 grid gap-4 lg:grid-cols-2">
        <div>
          <TableSectionHeading
            icon={<Truck size={16} />}
            title="Inventory Shortage Alerts"
            caption="SKUs below reorder point → gap to reorder point → supplier contact."
          />
        <div className="mt-3 rounded-xl border border-border bg-surface-subtle p-4">
          {supplier_follow_ups.length === 0 ? (
            <Card className="text-sm text-text-secondary">No SKUs are currently below their reorder point.</Card>
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeaderCell>SKU</TableHeaderCell>
                  <TableHeaderCell>Warehouse</TableHeaderCell>
                  <TableHeaderCell className="text-right">Remaining Qty</TableHeaderCell>
                  <TableHeaderCell className="text-right">Reorder Point</TableHeaderCell>
                  <TableHeaderCell className="text-right">Gap to Reorder Pt.</TableHeaderCell>
                  <TableHeaderCell>Supplier</TableHeaderCell>
                  <TableHeaderCell className="text-right">Lead Time (Days)</TableHeaderCell>
                  <TableHeaderCell>Alert</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {supplier_follow_ups.map((row, index) => (
                  <TableRow key={`${row.sku}-${row.warehouse}`} className={index % 2 === 1 ? "bg-surface-muted" : undefined}>
                    <TableCell className="whitespace-nowrap font-medium text-text-primary">{row.sku}</TableCell>
                    <TableCell className="whitespace-nowrap text-text-secondary">{row.warehouse}</TableCell>
                    <TableCell className="whitespace-nowrap text-right font-medium tabular-nums">
                      {formatNumber(row.remaining_qty)}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-right tabular-nums">{formatNumber(row.reorder_point)}</TableCell>
                    <TableCell className="whitespace-nowrap text-right font-semibold tabular-nums text-warning">
                      {formatNumber(row.reorder_point - row.remaining_qty)}
                    </TableCell>
                    <TableCell
                      className="block max-w-[140px] truncate whitespace-nowrap text-text-secondary"
                      title={row.supplier_name ?? undefined}
                    >
                      {row.supplier_name ?? "—"}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-right tabular-nums">
                      {row.lead_time_days != null ? formatNumber(row.lead_time_days) : "—"}
                    </TableCell>
                    <TableCell className="whitespace-nowrap">
                      <StatusBadge status="Below Reorder Point" tone="warning" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
        </div>

        <div>
          <TableSectionHeading
            icon={<ReceiptText size={16} />}
            title="Payment Follow-up Items"
            caption="Outstanding amount → aging bucket → follow-up priority."
          />
        <div className="mt-3 rounded-xl border border-border bg-surface-subtle p-4">
          {followUpItems.length === 0 ? (
            <Card className="text-sm text-text-secondary">No invoices currently need follow-up.</Card>
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeaderCell>Invoice ID</TableHeaderCell>
                  <TableHeaderCell>Customer</TableHeaderCell>
                  <TableHeaderCell className="text-right">Outstanding Amount</TableHeaderCell>
                  <TableHeaderCell className="text-right">Days Overdue</TableHeaderCell>
                  <TableHeaderCell>Aging Bucket</TableHeaderCell>
                  <TableHeaderCell>Follow-up Priority</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {followUpItems.map((row, index) => (
                  <TableRow key={row.invoice_id} className={index % 2 === 1 ? "bg-surface-muted" : undefined}>
                    <TableCell className="whitespace-nowrap font-medium text-text-primary">{row.invoice_id}</TableCell>
                    <TableCell className="block max-w-[160px] truncate whitespace-nowrap font-medium text-text-primary" title={row.customer_name}>
                      {row.customer_name}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-right font-semibold tabular-nums">
                      {formatAmount(row.outstanding_amount)}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-right font-medium tabular-nums">
                      {formatNumber(row.days_overdue)}
                    </TableCell>
                    <TableCell className="whitespace-nowrap">
                      <StatusBadge status={row.aging_bucket} tone={agingBucketTone(row.aging_bucket)} />
                    </TableCell>
                    <TableCell className="whitespace-nowrap">
                      <StatusBadge status={row.follow_up_priority} tone={followUpPriorityTone(row.follow_up_priority)} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
        </div>
      </section>

      <section className="mt-6">
        <h2 className="text-base font-semibold text-text-primary">Reports</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-3">
          {reportManifests.map((manifest) => (
            <ReportCard key={manifest.report_id} state="Ready" manifest={manifest} />
          ))}
        </div>
      </section>

      <section className="mt-6">
        <h2 className="text-base font-semibold text-text-primary">Workflows</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-3">
          {WORKFLOW_ENTRIES.map((entry) => (
            <Link key={entry.href} href={entry.href} className="block">
              <Card className="h-full transition-colors hover:border-accent">
                <span className="text-base font-semibold text-text-primary">{entry.label}</span>
                <p className="mt-1 text-sm text-text-secondary">{entry.description}</p>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      <section className="mt-6">
        <h2 className="text-base font-semibold text-text-primary">How the Workflows Connect</h2>
        <Card className="mt-3 flex flex-col gap-3">
          <FlowRow
            steps={[
              { icon: <Upload size={14} />, label: "Orders Excel" },
              { icon: <CheckCircle2 size={14} />, label: "Order Validation" },
              { icon: <ClipboardList size={14} />, label: "Valid Orders" },
            ]}
          />
          <FlowRow
            steps={[
              { icon: <ClipboardList size={14} />, label: "Valid Orders + Inventory" },
              { icon: <PackageCheck size={14} />, label: "Allocation" },
              { icon: <Truck size={14} />, label: "Backorders / Supplier Follow-up" },
            ]}
          />
          <FlowRow
            steps={[
              { icon: <ReceiptText size={14} />, label: "Invoices" },
              { icon: <Clock size={14} />, label: "Payment Aging" },
              { icon: <AlertCircle size={14} />, label: "Draft Reminders" },
            ]}
          />
          <FlowRow
            steps={[
              { icon: <CheckCircle2 size={14} />, label: "Workflow Outputs" },
              { icon: <FileSpreadsheet size={14} />, label: "Excel Reports" },
            ]}
          />
        </Card>
      </section>

      <section className="mt-6">
        <h2 className="flex items-center gap-2 text-base font-semibold text-text-primary">
          <BookOpen size={16} className="text-text-secondary" aria-hidden="true" />
          How This Demo Works
        </h2>
        <Card className="mt-3 flex flex-col gap-3 text-sm text-text-secondary">
          <p>
            This toolkit simulates three sales-admin workflows — <span className="font-medium text-text-primary">order validation</span>,{" "}
            <span className="font-medium text-text-primary">inventory allocation</span>, and{" "}
            <span className="font-medium text-text-primary">payment aging</span> — plus the Excel reports each one exports. It is a
            portfolio project, not a real ERP/CRM system.
          </p>
          <p>
            The three workflows connect in one direction: validated orders feed inventory allocation, and allocation and payment
            aging each produce their own report. Nothing here is cross-workflow risk scoring or forecasting — every number traces to
            a specific, tested Python function.
          </p>
          <p>
            <span className="font-medium text-text-primary">All data is fictional</span> — sample orders, customers, SKUs, and
            invoices generated for this demo, refreshed each time the underlying fixtures are regenerated. No real customer,
            order, or financial data is used anywhere.
          </p>
          <p>
            <span className="font-medium text-text-primary">Reading tags:</span> colored pills always come from a fixed, controlled
            vocabulary — e.g. Order priority is exactly High/Normal/Low, Allocation status is exactly Fully Allocated/Partially
            Allocated/Backordered, Payment follow-up priority is exactly High/Medium/Low/Watch/None. The color (green/amber/red/blue/
            gray) is a visual aid; the label is always the source of truth.
          </p>
          <p>
            <span className="font-medium text-text-primary">Filters and sorting</span> on each workflow page run entirely in the
            browser against the data already loaded — use the dropdowns and search box above a table to narrow it, and click a
            sortable column header to reorder it. Filtering never changes the KPI totals above the table, which always reflect the
            full result set.
          </p>
          <p>
            <span className="font-medium text-text-primary">Why Python first:</span> every rule you see enforced here (duplicate
            order detection, warehouse allocation order, aging-bucket thresholds, follow-up priority) is implemented and unit-tested
            in a Python core before this interface was built — the UI only displays outputs the tested business logic already
            produced, not the other way around.
          </p>
        </Card>
      </section>
    </div>
  );
}

function FlowRow({ steps }: { steps: { icon: React.ReactNode; label: string }[] }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {steps.map((step, index) => (
        <div key={step.label} className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 rounded-md border border-border bg-surface-subtle px-2.5 py-1.5 text-xs font-medium text-text-primary">
            <span className="text-text-secondary" aria-hidden="true">
              {step.icon}
            </span>
            {step.label}
          </span>
          {index < steps.length - 1 ? (
            <ArrowRight size={14} className="shrink-0 text-text-muted" aria-hidden="true" />
          ) : null}
        </div>
      ))}
    </div>
  );
}
