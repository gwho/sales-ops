"use client";

// See app/order-validation/page.tsx for why this page must be a Client
// Component (its DataTable column configs contain render functions).

// Internal imports
import { MetricCard } from "@/components/workflow/MetricCard";
import { UploadPanel } from "@/components/workflow/UploadPanel";
import { WorkflowStepper } from "@/components/workflow/WorkflowStepper";
import { DataTable, type DataTableColumn } from "@/components/tables/DataTable";
import {
  StatusBadge,
  allocationStatusTone,
  importancePriorityTone,
} from "@/components/workflow/StatusBadge";
import { inventoryAllocationResult } from "@/lib/mock-data";
import { formatDate, formatNumber } from "@/lib/formatters";
import type { AllocationResultRow, RemainingInventoryRow, SupplierFollowUpRow } from "@/types";

const STEPS = ["Upload Files", "Run Allocation", "Review Results"];

const ALLOCATION_COLUMNS: DataTableColumn<AllocationResultRow>[] = [
  { key: "order_id", header: "Order ID", render: (r) => r.order_id },
  { key: "customer_name", header: "Customer", render: (r) => r.customer_name },
  { key: "sku", header: "SKU", render: (r) => r.sku },
  { key: "product_name", header: "Product", render: (r) => r.product_name ?? "—" },
  { key: "requested_qty", header: "Requested Qty", render: (r) => formatNumber(r.requested_qty) },
  { key: "allocated_qty", header: "Allocated Qty", render: (r) => formatNumber(r.allocated_qty) },
  { key: "backorder_qty", header: "Backorder Qty", render: (r) => formatNumber(r.backorder_qty) },
  { key: "warehouse", header: "Warehouse", render: (r) => r.warehouse || "—" },
  {
    key: "status",
    header: "Status",
    render: (r) => <StatusBadge status={r.status} tone={allocationStatusTone(r.status)} />,
    sortable: true,
    sortValue: (r) => r.status,
  },
  {
    key: "priority",
    header: "Priority",
    render: (r) => <StatusBadge status={r.priority} tone={importancePriorityTone(r.priority)} />,
    sortable: true,
    sortValue: (r) => r.priority,
  },
  {
    key: "requested_delivery_date",
    header: "Requested Delivery",
    render: (r) => formatDate(r.requested_delivery_date),
  },
];

const REMAINING_INVENTORY_COLUMNS: DataTableColumn<RemainingInventoryRow>[] = [
  { key: "sku", header: "SKU", render: (r) => r.sku },
  { key: "warehouse", header: "Warehouse", render: (r) => r.warehouse },
  { key: "starting_available_qty", header: "Starting Qty", render: (r) => formatNumber(r.starting_available_qty) },
  { key: "allocated_qty", header: "Allocated Qty", render: (r) => formatNumber(r.allocated_qty) },
  { key: "remaining_qty", header: "Remaining Qty", render: (r) => formatNumber(r.remaining_qty) },
  { key: "reorder_point", header: "Reorder Point", render: (r) => (r.reorder_point != null ? formatNumber(r.reorder_point) : "—") },
  {
    key: "reorder_alert",
    header: "Reorder Alert",
    render: (r) =>
      r.reorder_alert === "Yes" ? (
        <StatusBadge status="Below Reorder Point" tone="warning" />
      ) : (
        <span className="text-text-secondary">No</span>
      ),
  },
];

const SUPPLIER_FOLLOW_UP_COLUMNS: DataTableColumn<SupplierFollowUpRow>[] = [
  { key: "sku", header: "SKU", render: (r) => r.sku },
  { key: "warehouse", header: "Warehouse", render: (r) => r.warehouse },
  { key: "remaining_qty", header: "Remaining Qty", render: (r) => formatNumber(r.remaining_qty) },
  { key: "reorder_point", header: "Reorder Point", render: (r) => formatNumber(r.reorder_point) },
  { key: "supplier_name", header: "Supplier", render: (r) => r.supplier_name ?? "—" },
  { key: "lead_time_days", header: "Lead Time (Days)", render: (r) => (r.lead_time_days != null ? formatNumber(r.lead_time_days) : "—") },
];

// Component
export default function InventoryAllocationPage() {
  const { summary, allocation_results, backorders, remaining_inventory, supplier_follow_ups } =
    inventoryAllocationResult;

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-2xl font-semibold text-text-primary">Inventory Allocation</h1>
      <p className="mt-2 text-sm text-text-secondary">
        Allocate stock by priority, delivery date, and warehouse availability.
      </p>

      <div className="mt-6">
        <WorkflowStepper steps={STEPS} currentStep={STEPS.length - 1} />
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <UploadPanel
          label="Valid Orders File"
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
        <UploadPanel label="Inventory File" requiredColumns={["sku", "warehouse", "available_qty"]} />
      </div>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Summary</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-3 lg:grid-cols-5">
          <MetricCard label="Total Order Lines" value={formatNumber(summary.total_order_lines)} />
          <MetricCard label="Fully Allocated" value={formatNumber(summary.fully_allocated_count)} />
          <MetricCard label="Partially Allocated" value={formatNumber(summary.partially_allocated_count)} />
          <MetricCard label="Backordered" value={formatNumber(summary.backordered_count)} />
          <MetricCard label="Low Stock SKUs" value={formatNumber(summary.low_stock_sku_count)} />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Allocation Results</h2>
        <div className="mt-3">
          <DataTable
            columns={ALLOCATION_COLUMNS}
            data={allocation_results}
            getRowKey={(r) => `${r.order_id}-${r.sku}`}
            emptyTitle="No allocation results."
          />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Backorders</h2>
        <div className="mt-3">
          <DataTable
            columns={ALLOCATION_COLUMNS}
            data={backorders}
            getRowKey={(r) => `${r.order_id}-${r.sku}`}
            emptyTitle="No backorders."
            emptyDescription="Every requested quantity was fully allocated."
          />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Remaining Inventory</h2>
        <div className="mt-3">
          <DataTable
            columns={REMAINING_INVENTORY_COLUMNS}
            data={remaining_inventory}
            getRowKey={(r) => `${r.sku}-${r.warehouse}`}
            emptyTitle="No remaining inventory data."
          />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-base font-semibold text-text-primary">Supplier Follow-up</h2>
        <div className="mt-3">
          <DataTable
            columns={SUPPLIER_FOLLOW_UP_COLUMNS}
            data={supplier_follow_ups}
            getRowKey={(r) => `${r.sku}-${r.warehouse}`}
            emptyTitle="No supplier follow-ups."
            emptyDescription="No SKUs are currently below their reorder point."
          />
        </div>
      </section>
    </div>
  );
}
