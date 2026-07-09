// External imports
import Link from "next/link";

// Internal imports
import { MetricCard } from "@/components/workflow/MetricCard";
import { ReportCard } from "@/components/workflow/ReportCard";
import { Card } from "@/components/ui/Card";
import {
  orderValidationResult,
  inventoryAllocationResult,
  paymentAgingResult,
  reportManifests,
  ninetyPlusDaysAmount,
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

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Order Validation</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <MetricCard label="Total Orders" value={formatNumber(validation.total_orders)} />
          <MetricCard label="Valid Orders" value={formatNumber(validation.valid_orders)} />
          <MetricCard label="Invalid Orders" value={formatNumber(validation.invalid_orders)} />
          <MetricCard label="Duplicate Orders" value={formatNumber(validation.duplicate_orders)} />
          <MetricCard label="Invalid SKUs" value={formatNumber(validation.invalid_skus)} />
          <MetricCard label="Missing Fields" value={formatNumber(validation.missing_field_count)} />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Inventory Allocation</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-3 lg:grid-cols-5">
          <MetricCard label="Total Order Lines" value={formatNumber(allocation.total_order_lines)} />
          <MetricCard label="Fully Allocated" value={formatNumber(allocation.fully_allocated_count)} />
          <MetricCard
            label="Partially Allocated"
            value={formatNumber(allocation.partially_allocated_count)}
          />
          <MetricCard label="Backordered" value={formatNumber(allocation.backordered_count)} />
          <MetricCard label="Low Stock SKUs" value={formatNumber(allocation.low_stock_sku_count)} />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Payment Aging</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Total Outstanding" value={formatAmount(aging.total_outstanding_amount)} />
          <MetricCard label="Overdue Amount" value={formatAmount(aging.overdue_amount)} />
          <MetricCard label="High Priority Count" value={formatNumber(aging.high_priority_count)} />
          <MetricCard
            label="90+ Days Amount"
            value={formatAmount(ninetyPlusDaysAmount(paymentAgingResult))}
          />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Reports</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-3">
          {reportManifests.map((manifest) => (
            <ReportCard key={manifest.report_id} state="Ready" manifest={manifest} />
          ))}
        </div>
      </section>

      <section className="mt-8">
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
    </div>
  );
}
