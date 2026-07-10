// Internal imports
import type { PaymentAgingSummary } from "@/types";

// Types
type AgingBucketBarsProps = {
  counts: PaymentAgingSummary["aging_bucket_counts"];
};

/** Compact horizontal bar list, one row per aging bucket. Shared by /dashboard and /payment-aging. */
export function AgingBucketBars({ counts }: AgingBucketBarsProps) {
  const entries = Object.entries(counts) as [keyof PaymentAgingSummary["aging_bucket_counts"], number][];
  const max = Math.max(1, ...entries.map(([, count]) => count));

  return (
    <div className="flex flex-col gap-2">
      {entries.map(([bucket, count]) => (
        <div key={bucket} className="flex items-center gap-3">
          <span className="w-24 shrink-0 text-xs text-text-secondary">{bucket}</span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-muted">
            <div className="h-full rounded-full bg-accent" style={{ width: `${(count / max) * 100}%` }} />
          </div>
          <span className="w-6 shrink-0 text-right text-xs text-text-secondary">{count}</span>
        </div>
      ))}
    </div>
  );
}
