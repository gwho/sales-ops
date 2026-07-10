// Internal imports
import type { Tone } from "@/components/workflow/StatusBadge";
import { formatNumber } from "@/lib/formatters";

// Types
type DonutSegment = {
  label: string;
  value: number;
  tone: Tone;
};

type DonutBreakdownChartProps = {
  segments: DonutSegment[];
  totalLabel: string;
};

const STROKE_TONE_CLASSES: Record<Tone, string> = {
  success: "stroke-success",
  warning: "stroke-warning",
  danger: "stroke-danger",
  info: "stroke-info",
  neutral: "stroke-text-muted",
};

const DOT_TONE_CLASSES: Record<Tone, string> = {
  success: "bg-success",
  warning: "bg-warning",
  danger: "bg-danger",
  info: "bg-info",
  neutral: "bg-text-muted",
};

const RADIUS = 35;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

/**
 * Pure-SVG donut (stacked circle strokes) — no charting library. Tone comes
 * from the caller (see components/workflow/StatusBadge.tsx's tone helpers),
 * never decided here, so a chart segment and a table badge for the same
 * status always match.
 */
export function DonutBreakdownChart({ segments, totalLabel }: DonutBreakdownChartProps) {
  const total = segments.reduce((sum, segment) => sum + segment.value, 0);

  return (
    <div className="flex items-center gap-6">
      <div className="relative h-32 w-32 shrink-0">
        <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
          {total === 0 ? (
            <circle cx="50" cy="50" r={RADIUS} fill="none" strokeWidth="14" className="stroke-border-strong" />
          ) : (
            (() => {
              let offset = 0;
              return segments
                .filter((segment) => segment.value > 0)
                .map((segment) => {
                  const length = (segment.value / total) * CIRCUMFERENCE;
                  const dashArray = `${length} ${CIRCUMFERENCE - length}`;
                  const dashOffset = -offset;
                  offset += length;
                  return (
                    <circle
                      key={segment.label}
                      cx="50"
                      cy="50"
                      r={RADIUS}
                      fill="none"
                      strokeWidth="14"
                      strokeDasharray={dashArray}
                      strokeDashoffset={dashOffset}
                      className={STROKE_TONE_CLASSES[segment.tone]}
                    />
                  );
                });
            })()
          )}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-semibold text-text-primary">{formatNumber(total)}</span>
          <span className="text-[10px] uppercase tracking-wide text-text-muted">{totalLabel}</span>
        </div>
      </div>
      <div className="flex flex-col gap-1.5">
        {segments.map((segment) => (
          <span key={segment.label} className="flex items-center gap-1.5 text-xs text-text-secondary">
            <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT_TONE_CLASSES[segment.tone]}`} />
            {segment.label}: <span className="font-medium text-text-primary">{formatNumber(segment.value)}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
