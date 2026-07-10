// Internal imports
import { Badge } from "@/components/ui/Badge";

// Types
export type Tone = "success" | "warning" | "danger" | "info" | "neutral";

type StatusBadgeProps = {
  status: string;
  tone: Tone;
};

/**
 * Thin display wrapper around Badge. Callers pick the tone using one of the
 * domain helpers below rather than StatusBadge inferring it from the raw
 * string — the same label text ("High") maps to a different tone depending
 * on which contract field it came from (see the StatusBadge mapping table in
 * docs/plan/phase-9-reusable-ui-components-static-pages/plan.md).
 */
export function StatusBadge({ status, tone }: StatusBadgeProps) {
  return <Badge tone={tone}>{status}</Badge>;
}

// --- Domain tone mappings ---

export function severityTone(severity: "Error" | "Warning"): Tone {
  return severity === "Error" ? "danger" : "warning";
}

export function allocationStatusTone(
  status: "Fully Allocated" | "Partially Allocated" | "Backordered",
): Tone {
  switch (status) {
    case "Fully Allocated":
      return "success";
    case "Partially Allocated":
      return "warning";
    case "Backordered":
      return "danger";
  }
}

/** Order/allocation `priority` is an importance ranking, not a problem — High just draws attention. */
export function importancePriorityTone(priority: "High" | "Normal" | "Low"): Tone {
  return priority === "High" ? "warning" : "neutral";
}

export function agingBucketTone(
  bucket: "Current" | "1-30 Days" | "31-60 Days" | "61-90 Days" | "90+ Days",
): Tone {
  switch (bucket) {
    case "Current":
      return "success";
    case "1-30 Days":
      return "info";
    case "31-60 Days":
    case "61-90 Days":
      return "warning";
    case "90+ Days":
      return "danger";
  }
}

/** Payment `follow_up_priority` is an urgency-of-problem ranking — High is the worst case. */
export function followUpPriorityTone(priority: "High" | "Medium" | "Low" | "Watch" | "None"): Tone {
  switch (priority) {
    case "High":
      return "danger";
    case "Medium":
      return "warning";
    case "Low":
      return "info";
    case "Watch":
    case "None":
      return "neutral";
  }
}

export type ReportLifecycleState = "Needs Input" | "Not Generated" | "Processing" | "Ready";

export function reportLifecycleTone(state: ReportLifecycleState): Tone {
  switch (state) {
    case "Ready":
      return "success";
    case "Processing":
      return "info";
    case "Not Generated":
    case "Needs Input":
      return "neutral";
  }
}
