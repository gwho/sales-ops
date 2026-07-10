// Internal imports
import { cn } from "@/lib/utils";
import type { Tone } from "@/components/workflow/StatusBadge";

// Types
type Segment = {
  label: string;
  value: number;
  tone: Tone;
};

type SegmentedBarProps = {
  segments: Segment[];
};

const FILL_TONE_CLASSES: Record<Tone, string> = {
  success: "bg-success",
  warning: "bg-warning",
  danger: "bg-danger",
  info: "bg-info",
  neutral: "bg-text-muted",
};

/**
 * Multi-category share-of-total bar (e.g. valid vs invalid orders, allocation
 * status mix) plus a labeled legend with the real counts — numeric labels
 * always visible, never a stand-alone bar with no value. No charting library.
 */
export function SegmentedBar({ segments }: SegmentedBarProps) {
  const total = Math.max(
    1,
    segments.reduce((sum, segment) => sum + segment.value, 0),
  );

  return (
    <div className="flex flex-col gap-2">
      <div className="flex h-2 w-full overflow-hidden rounded-full bg-surface-muted">
        {segments.map((segment) => (
          <div
            key={segment.label}
            className={cn("h-full", FILL_TONE_CLASSES[segment.tone])}
            style={{ width: `${(segment.value / total) * 100}%` }}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1">
        {segments.map((segment) => (
          <span key={segment.label} className="flex items-center gap-1.5 text-xs text-text-secondary">
            <span className={cn("h-1.5 w-1.5 shrink-0 rounded-full", FILL_TONE_CLASSES[segment.tone])} />
            {segment.label}: <span className="font-medium text-text-primary">{segment.value}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
