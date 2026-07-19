import { Check } from "lucide-react";

import type { PortfolioProofStrip } from "@/types/portfolio-content";

// Durable, permanent-fact statements only — never a metric that requires an
// update cadence (test counts, ROI). See
// docs/architect/landing-page-evidence-and-technical-credibility/decisions.md
// #4. Deliberately a thin strip, not a full Section — sits directly under
// Hero, before WorkflowsSection.
export function ProofStrip({ items }: { items: PortfolioProofStrip }) {
  return (
    <div className="border-b border-border bg-surface-muted">
      <div className="mx-auto flex max-w-5xl flex-col gap-3 px-6 py-4 sm:flex-row sm:flex-wrap sm:gap-x-8 sm:gap-y-2">
        {items.map((item) => (
          <p key={item} className="flex items-start gap-2 text-xs text-text-secondary">
            <Check size={14} className="mt-0.5 shrink-0 text-accent" aria-hidden="true" />
            {item}
          </p>
        ))}
      </div>
    </div>
  );
}
