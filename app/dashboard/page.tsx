// External imports
import Link from "next/link";
import {
  ClipboardList,
  CheckCircle2,
  AlertCircle,
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
import { ReportCard } from "@/components/workflow/ReportCard";
import { Card } from "@/components/ui/Card";
import { DashboardLiveSections } from "@/components/dashboard/DashboardLiveSections";
import { reportManifests } from "@/lib/mock-data";

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
  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <p className="text-xs font-medium uppercase tracking-wide text-text-secondary">
        Sales Admin Automation Toolkit
      </p>
      <h1 className="mt-1 text-2xl font-semibold text-text-primary">Dashboard</h1>
      <p className="mt-2 text-sm text-text-secondary">
        Your latest saved results for order validation, inventory allocation, and payment aging —
        falling back to sample data for any workflow you haven&apos;t run yet.
      </p>

      <DashboardLiveSections />

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
            <span className="font-medium text-text-primary">Your results, saved anonymously:</span> running a workflow saves its
            result to this browser only (no account, no login) — the dashboard above shows your own latest run for each workflow
            you&apos;ve tried, and falls back to fictional sample data for any you haven&apos;t. A &quot;Sample data&quot; label
            marks which sections are showing seeded demo content rather than something you ran.
          </p>
          <p>
            <span className="font-medium text-text-primary">All sample data is fictional</span> — sample orders, customers, SKUs, and
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
