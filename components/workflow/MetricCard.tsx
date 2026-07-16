// External imports
import { type ReactNode } from "react";

// Internal imports
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/utils";
import type { Tone } from "@/components/workflow/StatusBadge";

// Types
type MetricCardProps = {
  label: string;
  value: string | number;
  icon?: ReactNode;
  tone?: Tone;
  /** Dashboard-only (Phase 12): true when this card's value came from the
   * static sample fallback rather than the visitor's own Saved Workflow
   * Result -- see docs/adr/0007-session-scoped-workflow-result-persistence.md. */
  sample?: boolean;
};

const CHIP_TONE_CLASSES: Record<Tone, string> = {
  success: "bg-success-subtle text-success",
  warning: "bg-warning-subtle text-warning",
  danger: "bg-danger-subtle text-danger",
  info: "bg-info-subtle text-info",
  neutral: "bg-surface-muted text-text-secondary",
};

// Component
/** Icon chip is optional and decorative only — matches the Figma-approved "label + big number + icon chip" KPI card pattern, never the trend-delta that sits next to it in the same reference (that stays out of scope). Phase 10.2: restructured into a compact, roughly square tile (icon top, value centered/prominent, label below) instead of a short wide strip, with a min-height so a row of tiles aligns regardless of value/label length. */
export function MetricCard({ label, value, icon, tone = "neutral", sample = false }: MetricCardProps) {
  return (
    <Card className="flex min-h-[104px] flex-col items-center justify-center gap-2 p-4 text-center transition-shadow hover:border-border-strong hover:shadow-md">
      {icon ? (
        <span
          className={cn(
            "flex h-7 w-7 shrink-0 items-center justify-center rounded",
            CHIP_TONE_CLASSES[tone],
          )}
        >
          {icon}
        </span>
      ) : null}
      <span className="text-2xl font-semibold text-text-primary">{value}</span>
      <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">{label}</span>
      {sample ? (
        <Badge tone="neutral" dot={false} className="px-2 py-0.5 text-[10px]">
          Sample data
        </Badge>
      ) : null}
    </Card>
  );
}
