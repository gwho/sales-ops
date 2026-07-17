// External imports
import { FileSpreadsheet } from "lucide-react";

// Internal imports
import { ReportCard } from "@/components/workflow/ReportCard";
import { reportManifests } from "@/lib/mock-data";

const WORKFLOW_HREF_BY_REPORT_TYPE: Record<string, string> = {
  order_validation: "/order-validation",
  inventory_allocation: "/inventory-allocation",
  payment_aging: "/payment-aging",
};

// Component
export default function ReportsPage() {
  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="flex items-center gap-2 text-2xl font-semibold text-text-primary">
        <FileSpreadsheet size={20} className="text-text-secondary" aria-hidden="true" />
        Sample Report Overview
      </h1>
      <p className="mt-2 text-sm text-text-secondary">
        These cards show what each report looks like using sample data. Live report downloads are generated
        from each workflow page after you upload files there — this page doesn&apos;t track live results.
      </p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {reportManifests.map((manifest) => (
          <ReportCard
            key={manifest.report_id}
            state="Ready"
            manifest={manifest}
            workflowHref={WORKFLOW_HREF_BY_REPORT_TYPE[manifest.report_type]}
          />
        ))}
      </div>
    </div>
  );
}
