// Internal imports
import { cn } from "@/lib/utils";
import type { Tone } from "@/components/workflow/StatusBadge";

// Types
type MiniBarProps = {
  value: number;
  max: number;
  tone?: Tone;
};

const BAR_TONE_CLASSES: Record<Tone, string> = {
  success: "bg-success",
  warning: "bg-warning",
  danger: "bg-danger",
  info: "bg-info",
  neutral: "bg-border-strong",
};

/**
 * Compact quantity/progress indicator for table cells — always supplemental
 * to the numeric value, never a replacement for it (render both together).
 * No charting library; a token-styled div bar.
 */
export function MiniBar({ value, max, tone = "info" }: MiniBarProps) {
  const percent = max > 0 ? Math.min(100, Math.max(0, (value / max) * 100)) : 0;

  return (
    <div className="h-1.5 w-14 shrink-0 overflow-hidden rounded-full bg-surface-muted">
      <div className={cn("h-full rounded-full", BAR_TONE_CLASSES[tone])} style={{ width: `${percent}%` }} />
    </div>
  );
}
