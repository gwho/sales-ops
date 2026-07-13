"use client";

// Client Component boundary for the session-aware parts of the dashboard --
// see docs/adr/0007-session-scoped-workflow-result-persistence.md's
// "Frontend read boundary" section. The Anonymous Session ID lives only in
// localStorage, so this fetch must happen in the browser after hydration,
// not during app/dashboard/page.tsx's server render. That page stays a
// Server Component for the static shell (nav cards, infographic, guide
// copy, Reports section); this component owns the Overview KPIs, both
// chart cards, and both tables -- the sections that depend on the
// visitor's own saved results, resolved independently per workflow type
// against the same static sample fallback the dashboard has always used.

// External imports
import { useEffect, useState } from "react";
import Link from "next/link";
import { ClipboardList, CheckCircle2, XCircle, AlertTriangle, PackageCheck, ReceiptText, Truck } from "lucide-react";

// Internal imports
import { MetricCard } from "@/components/workflow/MetricCard";
import { TableSectionHeading } from "@/components/tables/TableSectionHeading";
import { DonutBreakdownChart } from "@/components/charts/DonutBreakdownChart";
import { VerticalBucketBarChart } from "@/components/charts/VerticalBucketBarChart";
import { StatusBadge, followUpPriorityTone, agingBucketTone, allocationStatusTone } from "@/components/workflow/StatusBadge";
import { Badge } from "@/components/ui/Badge";
import { Table, TableHead, TableBody, TableRow, TableHeaderCell, TableCell } from "@/components/ui/Table";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/feedback/LoadingState";
import { BusinessErrorMessage } from "@/components/feedback/BusinessErrorMessage";
import { ApiError, getDashboardResults } from "@/lib/api-client";
import { formatAmount, formatNumber } from "@/lib/formatters";
import { orderValidationResult, inventoryAllocationResult, paymentAgingResult, amountByAgingBucket } from "@/lib/mock-data";
import type { OrderValidationResult, InventoryAllocationResult, PaymentAgingResult } from "@/types";

type FetchStatus = "loading" | "loaded" | "failed";

function SampleDataChip() {
  return (
    <Badge tone="neutral" dot={false} className="px-2 py-0.5 text-[10px]">
      Sample data
    </Badge>
  );
}

// Component
export function DashboardLiveSections() {
  const [status, setStatus] = useState<FetchStatus>("loading");
  const [errorDetail, setErrorDetail] = useState<string | null>(null);
  const [liveOrderValidation, setLiveOrderValidation] = useState<OrderValidationResult | null>(null);
  const [liveInventoryAllocation, setLiveInventoryAllocation] = useState<InventoryAllocationResult | null>(null);
  const [livePaymentAging, setLivePaymentAging] = useState<PaymentAgingResult | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const results = await getDashboardResults();
        if (cancelled) return;
        setLiveOrderValidation(results.order_validation);
        setLiveInventoryAllocation(results.inventory_allocation);
        setLivePaymentAging(results.payment_aging);
        setStatus("loaded");
      } catch (error) {
        if (cancelled) return;
        setErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
        setStatus("failed");
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  // First paint is always a skeleton, never sample-then-swap -- showing
  // sample values immediately and replacing them on fetch return would
  // flash content and blur "is this real or sample?" (ADR 0007).
  if (status === "loading") {
    return (
      <div className="mt-6">
        <LoadingState label="Loading your saved results…" />
      </div>
    );
  }

  if (status === "failed") {
    return (
      <div className="mt-6">
        <BusinessErrorMessage message={errorDetail ?? "Something went wrong. Please try again."} />
      </div>
    );
  }

  const orderValidationIsSample = liveOrderValidation === null;
  const inventoryAllocationIsSample = liveInventoryAllocation === null;
  const paymentAgingIsSample = livePaymentAging === null;

  const resolvedInventoryAllocation = liveInventoryAllocation ?? inventoryAllocationResult;
  const resolvedPaymentAging = livePaymentAging ?? paymentAgingResult;

  const validation = (liveOrderValidation ?? orderValidationResult).summary;
  const allocation = resolvedInventoryAllocation.summary;
  const aging = resolvedPaymentAging.summary;
  const { supplier_follow_ups } = resolvedInventoryAllocation;
  const followUpItems = resolvedPaymentAging.aging_rows.filter((row) => row.follow_up_priority !== "None");

  return (
    <>
      <section className="mt-6">
        <h2 className="text-base font-semibold text-text-primary">Overview</h2>
        <div className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          <MetricCard
            label="Total Orders"
            value={formatNumber(validation.total_orders)}
            icon={<ClipboardList size={16} />}
            tone="info"
            sample={orderValidationIsSample}
          />
          <MetricCard
            label="Invalid Orders"
            value={formatNumber(validation.invalid_orders)}
            icon={<XCircle size={16} />}
            tone="danger"
            sample={orderValidationIsSample}
          />
          <MetricCard
            label="Fully Allocated"
            value={formatNumber(allocation.fully_allocated_count)}
            icon={<CheckCircle2 size={16} />}
            tone="success"
            sample={inventoryAllocationIsSample}
          />
          <MetricCard
            label="Backordered"
            value={formatNumber(allocation.backordered_count)}
            icon={<Truck size={16} />}
            tone="danger"
            sample={inventoryAllocationIsSample}
          />
          <MetricCard
            label="Overdue Amount"
            value={formatAmount(aging.overdue_amount)}
            icon={<AlertTriangle size={16} />}
            tone="warning"
            sample={paymentAgingIsSample}
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
              inventoryAllocationIsSample ? (
                <SampleDataChip />
              ) : (
                <Link href="/inventory-allocation" className="text-xs font-medium text-accent hover:text-accent-hover">
                  View all
                </Link>
              )
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
              paymentAgingIsSample ? (
                <SampleDataChip />
              ) : (
                <Link href="/payment-aging" className="text-xs font-medium text-accent hover:text-accent-hover">
                  AR report
                </Link>
              )
            }
          />
          <div className="mt-3 flex min-h-48 flex-col justify-center">
            <VerticalBucketBarChart
              data={amountByAgingBucket(resolvedPaymentAging).map((bucket) => ({
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
            action={inventoryAllocationIsSample ? <SampleDataChip /> : null}
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
            action={paymentAgingIsSample ? <SampleDataChip /> : null}
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
                      <TableCell
                        className="block max-w-[160px] truncate whitespace-nowrap font-medium text-text-primary"
                        title={row.customer_name}
                      >
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
    </>
  );
}
