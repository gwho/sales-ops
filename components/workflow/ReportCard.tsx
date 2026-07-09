// Internal imports
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  StatusBadge,
  reportLifecycleTone,
  type ReportLifecycleState,
} from "@/components/workflow/StatusBadge";
import { formatDateTime } from "@/lib/formatters";
import type { ReportManifest } from "@/types";

// Types
type ReportCardProps =
  | { state: "Ready"; manifest: ReportManifest }
  | { state: Exclude<ReportLifecycleState, "Ready">; reportTypeLabel: string };

const NOT_READY_COPY: Record<Exclude<ReportLifecycleState, "Ready">, string> = {
  "Needs Input": "Run this workflow first to generate a report.",
  "Not Generated": "Export hasn't been run yet this session.",
  Processing: "Generating report…",
};

// Component
export function ReportCard(props: ReportCardProps) {
  const title = props.state === "Ready" ? reportTypeLabel(props.manifest.report_type) : props.reportTypeLabel;

  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-base font-semibold text-text-primary">{title}</span>
        <StatusBadge status={props.state} tone={reportLifecycleTone(props.state)} />
      </div>

      {props.state === "Ready" ? (
        <>
          <div className="flex flex-col gap-1 text-sm text-text-secondary">
            <span>{props.manifest.file_name}</span>
            <span className="text-xs text-text-muted">
              Generated {formatDateTime(props.manifest.generated_at)}
            </span>
            <span className="text-xs text-text-muted">
              Sheets: {props.manifest.sheet_names.join(", ")}
            </span>
          </div>
          <Button
            variant="secondary"
            disabled
            title="Download becomes available once the API layer (Phase 10) is live"
          >
            Download .xlsx
          </Button>
        </>
      ) : (
        <p className="text-sm text-text-secondary">{NOT_READY_COPY[props.state]}</p>
      )}
    </Card>
  );
}

function reportTypeLabel(reportType: ReportManifest["report_type"]): string {
  switch (reportType) {
    case "order_validation":
      return "Order Validation Report";
    case "inventory_allocation":
      return "Inventory Allocation Report";
    case "payment_aging":
      return "Payment Aging Report";
  }
}
