// Internal imports
import type { Tone } from "@/components/workflow/StatusBadge";
import { EmptyState } from "@/components/feedback/EmptyState";
import { formatAmount } from "@/lib/formatters";

// Types
type BarDatum = {
  label: string;
  value: number;
  tone: Tone;
};

type VerticalBucketBarChartProps = {
  data: BarDatum[];
  subtitle: string;
};

const BAR_FILL_CLASSES: Record<Tone, string> = {
  success: "bg-success",
  warning: "bg-warning",
  danger: "bg-danger",
  info: "bg-info",
  neutral: "bg-text-muted",
};

const GUIDE_LINES = [25, 50, 75];

/** Plain CSS bar chart — no charting library. Values always shown above each bar, never bar-only. */
export function VerticalBucketBarChart({ data, subtitle }: VerticalBucketBarChartProps) {
  const max = Math.max(0, ...data.map((datum) => datum.value));

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs text-text-muted">{subtitle}</p>
      {max === 0 ? (
        <EmptyState title="No outstanding amounts to show." />
      ) : (
        <div className="relative flex h-32 items-end justify-between gap-3">
          {GUIDE_LINES.map((percent) => (
            <span
              key={percent}
              aria-hidden="true"
              className="absolute inset-x-0 border-t border-border"
              style={{ bottom: `${percent}%` }}
            />
          ))}
          {data.map((datum) => (
            <div key={datum.label} className="relative flex h-full flex-1 flex-col items-center justify-end gap-1">
              <span className="text-[10px] font-medium tabular-nums text-text-secondary">
                {formatAmount(datum.value)}
              </span>
              <div
                className={`w-full rounded-t-md ${BAR_FILL_CLASSES[datum.tone]}`}
                style={{ height: `${(datum.value / max) * 100}%` }}
              />
            </div>
          ))}
        </div>
      )}
      {max > 0 ? (
        <div className="flex justify-between gap-3">
          {data.map((datum) => (
            <span key={datum.label} className="flex-1 text-center text-[10px] text-text-secondary">
              {datum.label}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}
