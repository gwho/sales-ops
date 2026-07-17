// External imports
import Link from "next/link";

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

      <p className="mt-6 rounded-xl border border-border bg-surface-subtle p-3 text-xs text-text-secondary">
        Workflow results are stored under an anonymous session associated with this browser. Sections
        labelled &quot;Sample data&quot; show fictional fallback records until that workflow has been run.
      </p>
    </div>
  );
}
