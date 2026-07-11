"use client";

// See app/order-validation/page.tsx for why this page must be a Client
// Component (its DataTable column configs contain render functions).

// External imports
import { useMemo, useState } from "react";
import {
  ClipboardList,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  TrendingDown,
  PackageCheck,
  Warehouse,
  Truck,
} from "lucide-react";

// Internal imports
import { MetricCard } from "@/components/workflow/MetricCard";
import { UploadPanel } from "@/components/workflow/UploadPanel";
import { WorkflowStepper } from "@/components/workflow/WorkflowStepper";
import { DataTable, type DataTableColumn } from "@/components/tables/DataTable";
import { FilterToolbar } from "@/components/tables/FilterToolbar";
import { FilterSelect } from "@/components/tables/FilterSelect";
import { MiniBar } from "@/components/tables/MiniBar";
import { TableSectionHeading } from "@/components/tables/TableSectionHeading";
import {
  StatusBadge,
  allocationStatusTone,
  importancePriorityTone,
} from "@/components/workflow/StatusBadge";
import { EmptyState } from "@/components/feedback/EmptyState";
import { LoadingState } from "@/components/feedback/LoadingState";
import { BusinessErrorMessage } from "@/components/feedback/BusinessErrorMessage";
import { Button } from "@/components/ui/Button";
import { ApiError, downloadBlob, fetchSampleFile, postJSON, postReport } from "@/lib/api-client";
import { formatDate, formatNumber } from "@/lib/formatters";
import type { AllocationResultRow, InventoryAllocationResult, RemainingInventoryRow, SupplierFollowUpRow } from "@/types";

const STEPS = ["Upload Files", "Run Allocation", "Review Results"];

const STATUS_OPTIONS = ["All", "Fully Allocated", "Partially Allocated", "Backordered"];
const PRIORITY_OPTIONS = ["All", "High", "Normal", "Low"];
const REORDER_ALERT_OPTIONS = ["All", "Below Reorder Point", "No Alert"];

type RequestStatus = "idle" | "submitting" | "succeeded" | "failed";
type ReportRequestState = "idle" | "processing" | "failed";

// Single main table (Figma-safe pattern: one table + filter views, not a
// separate near-duplicate "Backorders" table for status === "Backordered").
const ALLOCATION_COLUMNS: DataTableColumn<AllocationResultRow>[] = [
  {
    key: "order_id",
    header: "Order ID",
    render: (r) => <span className="font-medium text-text-primary">{r.order_id}</span>,
    sortable: true,
    sortValue: (r) => r.order_id,
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
    key: "requested_qty",
    header: "Requested Qty",
    render: (r) => <span className="font-medium tabular-nums">{formatNumber(r.requested_qty)}</span>,
    sortable: true,
    sortValue: (r) => r.requested_qty,
    align: "right",
  },
  {
    key: "allocated_qty",
    header: "Allocated Qty",
    render: (r) => (
      <div className="flex items-center justify-end gap-2">
        <MiniBar value={r.allocated_qty} max={r.requested_qty} tone={r.allocated_qty >= r.requested_qty ? "success" : "warning"} />
        <span className="font-medium tabular-nums">{formatNumber(r.allocated_qty)}</span>
      </div>
    ),
    sortable: true,
    sortValue: (r) => r.allocated_qty,
    align: "right",
  },
  {
    key: "backorder_qty",
    header: "Backorder Qty",
    render: (r) => (
      <div className="flex items-center justify-end gap-2">
        {r.backorder_qty > 0 ? <MiniBar value={r.backorder_qty} max={r.requested_qty} tone="danger" /> : null}
        <span className={r.backorder_qty > 0 ? "font-semibold tabular-nums text-danger" : "tabular-nums text-text-muted"}>
          {formatNumber(r.backorder_qty)}
        </span>
      </div>
    ),
    sortable: true,
    sortValue: (r) => r.backorder_qty,
    align: "right",
  },
  {
    key: "warehouse",
    header: "Warehouse",
    render: (r) => <span className="text-text-secondary">{r.warehouse || "—"}</span>,
    sortable: true,
    sortValue: (r) => r.warehouse,
  },
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
    render: (r) => <span className="text-text-secondary">{formatDate(r.requested_delivery_date)}</span>,
    sortable: true,
    sortValue: (r) => r.requested_delivery_date,
  },
];

const REMAINING_INVENTORY_COLUMNS: DataTableColumn<RemainingInventoryRow>[] = [
  {
    key: "sku",
    header: "SKU",
    render: (r) => <span className="font-medium text-text-primary">{r.sku}</span>,
    sortable: true,
    sortValue: (r) => r.sku,
  },
  {
    key: "warehouse",
    header: "Warehouse",
    render: (r) => <span className="text-text-secondary">{r.warehouse}</span>,
    sortable: true,
    sortValue: (r) => r.warehouse,
  },
  {
    key: "starting_available_qty",
    header: "Starting Qty",
    render: (r) => <span className="tabular-nums text-text-secondary">{formatNumber(r.starting_available_qty)}</span>,
    sortable: true,
    sortValue: (r) => r.starting_available_qty,
    align: "right",
  },
  {
    key: "allocated_qty",
    header: "Allocated Qty",
    render: (r) => <span className="tabular-nums text-text-secondary">{formatNumber(r.allocated_qty)}</span>,
    sortable: true,
    sortValue: (r) => r.allocated_qty,
    align: "right",
  },
  {
    key: "remaining_qty",
    header: "Remaining vs Reorder Pt.",
    render: (r) =>
      r.reorder_point != null ? (
        <div className="flex items-center justify-end gap-2">
          <MiniBar
            value={r.remaining_qty}
            max={Math.max(r.reorder_point, r.remaining_qty, 1)}
            tone={r.remaining_qty < r.reorder_point ? "warning" : "success"}
          />
          <span className="font-medium tabular-nums">{formatNumber(r.remaining_qty)}</span>
        </div>
      ) : (
        <span className="font-medium tabular-nums">{formatNumber(r.remaining_qty)}</span>
      ),
    sortable: true,
    sortValue: (r) => r.remaining_qty,
    align: "right",
  },
  {
    key: "reorder_point",
    header: "Reorder Pt.",
    render: (r) => (r.reorder_point != null ? formatNumber(r.reorder_point) : "—"),
    align: "right",
  },
  {
    key: "reorder_alert",
    header: "Alert",
    render: (r) =>
      r.reorder_alert === "Yes" ? (
        <StatusBadge status="Below Reorder Point" tone="warning" />
      ) : (
        <span className="text-text-secondary">No</span>
      ),
    sortable: true,
    sortValue: (r) => r.reorder_alert,
  },
];

const SUPPLIER_FOLLOW_UP_COLUMNS: DataTableColumn<SupplierFollowUpRow>[] = [
  {
    key: "sku",
    header: "SKU",
    render: (r) => <span className="font-medium text-text-primary">{r.sku}</span>,
    sortable: true,
    sortValue: (r) => r.sku,
  },
  {
    key: "warehouse",
    header: "Warehouse",
    render: (r) => <span className="text-text-secondary">{r.warehouse}</span>,
    sortable: true,
    sortValue: (r) => r.warehouse,
  },
  {
    key: "remaining_qty",
    header: "Remaining",
    render: (r) => <span className="font-medium tabular-nums">{formatNumber(r.remaining_qty)}</span>,
    sortable: true,
    sortValue: (r) => r.remaining_qty,
    align: "right",
  },
  { key: "reorder_point", header: "Reorder Pt.", render: (r) => formatNumber(r.reorder_point), align: "right" },
  {
    key: "supplier_name",
    header: "Supplier",
    render: (r) => (
      <span className="block max-w-[140px] truncate text-text-secondary" title={r.supplier_name ?? undefined}>
        {r.supplier_name ?? "—"}
      </span>
    ),
  },
  { key: "lead_time_days", header: "Lead (Days)", render: (r) => (r.lead_time_days != null ? formatNumber(r.lead_time_days) : "—"), align: "right" },
];

// Component
export default function InventoryAllocationPage() {
  const [ordersFile, setOrdersFile] = useState<File | null>(null);
  const [productMasterFile, setProductMasterFile] = useState<File | null>(null);
  const [inventoryFile, setInventoryFile] = useState<File | null>(null);

  const [status, setStatus] = useState<RequestStatus>("idle");
  const [currentResult, setCurrentResult] = useState<InventoryAllocationResult | null>(null);
  const [errorDetail, setErrorDetail] = useState<string | null>(null);

  const [reportStatus, setReportStatus] = useState<ReportRequestState>("idle");
  const [reportErrorDetail, setReportErrorDetail] = useState<string | null>(null);

  const [sampleDataLabel, setSampleDataLabel] = useState<string | null>(null);
  const [sampleDataLoading, setSampleDataLoading] = useState(false);

  const canSubmit = ordersFile !== null && productMasterFile !== null && inventoryFile !== null;
  const currentStep = status === "succeeded" ? 2 : canSubmit ? 1 : 0;

  function buildFormData(orders: File, productMaster: File, inventory: File): FormData {
    const formData = new FormData();
    formData.set("orders_file", orders);
    formData.set("product_master_file", productMaster);
    formData.set("inventory_file", inventory);
    return formData;
  }

  async function runAllocation(orders: File, productMaster: File, inventory: File) {
    setStatus("submitting");
    setErrorDetail(null);
    try {
      const result = await postJSON<InventoryAllocationResult>(
        "/api/inventory/allocate",
        buildFormData(orders, productMaster, inventory),
      );
      setCurrentResult(result);
      setStatus("succeeded");
    } catch (error) {
      setErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
      setStatus("failed");
    }
  }

  function handleRunAllocation() {
    if (!ordersFile || !productMasterFile || !inventoryFile) return;
    void runAllocation(ordersFile, productMasterFile, inventoryFile);
  }

  async function handleRunSampleData() {
    setSampleDataLoading(true);
    setSampleDataLabel(null);
    setErrorDetail(null);
    try {
      const [orders, productMaster, inventory] = await Promise.all([
        fetchSampleFile("orders", "sample_orders.xlsx"),
        fetchSampleFile("product-master", "sample_product_master.xlsx"),
        fetchSampleFile("inventory", "sample_inventory.xlsx"),
      ]);
      setOrdersFile(orders);
      setProductMasterFile(productMaster);
      setInventoryFile(inventory);
      setSampleDataLabel(`Using sample data: ${orders.name}, ${productMaster.name}, ${inventory.name}`);
      setSampleDataLoading(false);
      await runAllocation(orders, productMaster, inventory);
    } catch (error) {
      setSampleDataLoading(false);
      setErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
      setStatus("failed");
    }
  }

  async function handleDownloadReport() {
    if (!ordersFile || !productMasterFile || !inventoryFile) return;
    setReportStatus("processing");
    setReportErrorDetail(null);
    try {
      const report = await postReport(
        "/api/inventory/allocate/report",
        buildFormData(ordersFile, productMasterFile, inventoryFile),
        "inventory_allocation_report.xlsx",
      );
      downloadBlob(report.blob, report.filename);
      setReportStatus("idle");
    } catch (error) {
      setReportErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
      setReportStatus("failed");
    }
  }

  const allocationResults = useMemo(() => currentResult?.allocation_results ?? [], [currentResult]);
  const remainingInventory = useMemo(() => currentResult?.remaining_inventory ?? [], [currentResult]);
  const supplierFollowUps = useMemo(() => currentResult?.supplier_follow_ups ?? [], [currentResult]);

  const warehouseOptions = useMemo(
    () => ["All", ...Array.from(new Set(allocationResults.map((r) => r.warehouse).filter(Boolean))).sort()],
    [allocationResults],
  );

  const [allocStatus, setAllocStatus] = useState("All");
  const [priority, setPriority] = useState("All");
  const [warehouse, setWarehouse] = useState("All");
  const [search, setSearch] = useState("");

  const filteredAllocation = useMemo(() => {
    const query = search.trim().toLowerCase();
    return allocationResults.filter((row) => {
      if (allocStatus !== "All" && row.status !== allocStatus) return false;
      if (priority !== "All" && row.priority !== priority) return false;
      if (warehouse !== "All" && row.warehouse !== warehouse) return false;
      if (query) {
        const haystack = `${row.order_id} ${row.customer_name} ${row.sku}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });
  }, [allocationResults, allocStatus, priority, warehouse, search]);

  const allocationFiltersActive = allocStatus !== "All" || priority !== "All" || warehouse !== "All" || search !== "";

  const [reorderAlertFilter, setReorderAlertFilter] = useState("All");
  const filteredRemainingInventory = useMemo(() => {
    if (reorderAlertFilter === "All") return remainingInventory;
    const wantsAlert = reorderAlertFilter === "Below Reorder Point";
    return remainingInventory.filter((row) => (row.reorder_alert === "Yes") === wantsAlert);
  }, [remainingInventory, reorderAlertFilter]);

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Inventory Allocation</h1>
          <p className="mt-2 text-sm text-text-secondary">
            Allocate stock by priority, delivery date, and warehouse availability.
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <Button
            variant="secondary"
            disabled={!canSubmit || reportStatus === "processing"}
            onClick={handleDownloadReport}
            title={canSubmit ? "Recomputes and downloads inventory_allocation_report.xlsx" : "Upload all three files first"}
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

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
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
        />
        <UploadPanel
          label="Product Master File"
          requiredColumns={["sku", "product_name", "active"]}
          sampleFileName="product-master"
          onFileChange={setProductMasterFile}
        />
        <UploadPanel
          label="Inventory File"
          requiredColumns={["sku", "warehouse", "available_qty"]}
          sampleFileName="inventory"
          onFileChange={setInventoryFile}
        />
      </div>
      <p className="mt-2 text-xs text-text-muted">
        Orders and product master run through validation first, then valid orders are allocated against inventory.
      </p>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <Button onClick={handleRunAllocation} disabled={!canSubmit || status === "submitting"}>
          {status === "submitting" ? "Allocating…" : "Run Allocation"}
        </Button>
        <Button
          variant="secondary"
          onClick={handleRunSampleData}
          disabled={sampleDataLoading || status === "submitting"}
          title="Fetches the committed sample workbooks and runs allocation on them"
        >
          {sampleDataLoading ? "Loading sample data…" : "Run sample data"}
        </Button>
        {sampleDataLabel ? <span className="text-xs text-text-muted">{sampleDataLabel}</span> : null}
      </div>

      {status === "idle" ? (
        <div className="mt-6">
          <EmptyState
            title="Upload orders, product master, and inventory files to run allocation."
            description="All three files are required before allocation can run."
          />
        </div>
      ) : null}

      {status === "submitting" ? (
        <div className="mt-6">
          <LoadingState label="Allocating inventory by priority, delivery date, and stock availability…" />
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
            <div className="mt-3 grid gap-4 sm:grid-cols-3 lg:grid-cols-5">
              <MetricCard
                label="Total Order Lines"
                value={formatNumber(currentResult.summary.total_order_lines)}
                icon={<ClipboardList size={16} />}
                tone="info"
              />
              <MetricCard
                label="Fully Allocated"
                value={formatNumber(currentResult.summary.fully_allocated_count)}
                icon={<CheckCircle2 size={16} />}
                tone="success"
              />
              <MetricCard
                label="Partially Allocated"
                value={formatNumber(currentResult.summary.partially_allocated_count)}
                icon={<AlertTriangle size={16} />}
                tone="warning"
              />
              <MetricCard
                label="Backordered"
                value={formatNumber(currentResult.summary.backordered_count)}
                icon={<XCircle size={16} />}
                tone="danger"
              />
              <MetricCard
                label="Low Stock SKUs"
                value={formatNumber(currentResult.summary.low_stock_sku_count)}
                icon={<TrendingDown size={16} />}
                tone="warning"
              />
            </div>
          </section>

          <section className="mt-6">
            <TableSectionHeading
              icon={<PackageCheck size={16} />}
              title="Allocation Results"
              caption="Requested qty → allocated qty → backorder qty. Filter by status to view backorders."
            />
            <div className="mt-3 flex flex-col gap-3">
              <FilterToolbar
                search={{ value: search, onChange: setSearch, placeholder: "Order ID, customer, or SKU…" }}
                onClear={() => {
                  setAllocStatus("All");
                  setPriority("All");
                  setWarehouse("All");
                  setSearch("");
                }}
                hasActiveFilters={allocationFiltersActive}
              >
                <FilterSelect label="Status" value={allocStatus} options={STATUS_OPTIONS} onChange={setAllocStatus} />
                <FilterSelect label="Priority" value={priority} options={PRIORITY_OPTIONS} onChange={setPriority} />
                <FilterSelect label="Warehouse" value={warehouse} options={warehouseOptions} onChange={setWarehouse} />
              </FilterToolbar>
              <DataTable
                columns={ALLOCATION_COLUMNS}
                data={filteredAllocation}
                getRowKey={(r) => `${r.order_id}-${r.sku}`}
                emptyTitle={allocationFiltersActive ? "No rows match the current filter." : "No allocation results."}
                emptyDescription={allocationFiltersActive ? "Try a different status, priority, warehouse, or search term." : undefined}
              />
            </div>
          </section>

          <section className="mt-6 grid gap-4 lg:grid-cols-2">
            <div className="rounded-xl border border-border bg-surface-subtle p-4">
              <TableSectionHeading
                icon={<Warehouse size={16} />}
                title="Remaining Inventory"
                caption="Inventory remaining → reorder alert → supplier follow-up."
              />
              <div className="mt-3 flex flex-col gap-3">
                <FilterToolbar
                  onClear={() => setReorderAlertFilter("All")}
                  hasActiveFilters={reorderAlertFilter !== "All"}
                >
                  <FilterSelect
                    label="Reorder Alert"
                    value={reorderAlertFilter}
                    options={REORDER_ALERT_OPTIONS}
                    onChange={setReorderAlertFilter}
                  />
                </FilterToolbar>
                <DataTable
                  columns={REMAINING_INVENTORY_COLUMNS}
                  data={filteredRemainingInventory}
                  getRowKey={(r) => `${r.sku}-${r.warehouse}`}
                  emptyTitle={reorderAlertFilter !== "All" ? "No rows match the current filter." : "No remaining inventory data."}
                />
              </div>
            </div>

            <div className="rounded-xl border border-border bg-surface-subtle p-4">
              <TableSectionHeading
                icon={<Truck size={16} />}
                title="Supplier Follow-up"
                caption="SKUs below reorder point → supplier contact for restock."
              />
              <div className="mt-3">
                <DataTable
                  columns={SUPPLIER_FOLLOW_UP_COLUMNS}
                  data={supplierFollowUps}
                  getRowKey={(r) => `${r.sku}-${r.warehouse}`}
                  emptyTitle="No supplier follow-ups."
                  emptyDescription="No SKUs are currently below their reorder point."
                />
              </div>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
