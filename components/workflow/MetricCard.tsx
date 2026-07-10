// External imports
import { type ReactNode } from "react";

// Internal imports
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import type { Tone } from "@/components/workflow/StatusBadge";

// Types
type MetricCardProps = {
  label: string;
  value: string | number;
  icon?: ReactNode;
  tone?: Tone;
};

const CHIP_TONE_CLASSES: Record<Tone, string> = {
  success: "bg-success-subtle text-success",
  warning: "bg-warning-subtle text-warning",
  danger: "bg-danger-subtle text-danger",
  info: "bg-info-subtle text-info",
  neutral: "bg-surface-muted text-text-secondary",
};

// Component
/** Icon chip is optional and decorative only — matches the Figma-approved "label + big number + icon chip" KPI card pattern, never the trend-delta that sits next to it in the same reference (that stays out of scope). */
export function MetricCard({ label, value, icon, tone = "neutral" }: MetricCardProps) {
  return (
    <Card className="flex flex-col gap-3 p-4">
      <div className="flex items-start justify-between gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">{label}</span>
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
      </div>
      <span className="text-2xl font-semibold text-text-primary">{value}</span>
    </Card>
  );
}
