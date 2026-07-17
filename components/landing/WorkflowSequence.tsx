import { ArrowRight } from "lucide-react";

import { SectionLabel, SectionHeading } from "@/components/landing/Section";
import { PORTFOLIO_ICON_MAP } from "@/components/landing/icon-map";
import type { PortfolioWorkflowSequenceRow } from "@/types/portfolio-content";

// Same icon-chip + arrow pattern as the dashboard's original "How the
// Workflows Connect" section (see ui-registry.md, Phase 9.1 notes) --
// content-driven here instead of hardcoded, and relocated to the public
// landing page per the /architect decision to move conceptual/demo-scope
// explanations out of the operational dashboard.
export function WorkflowSequence({ rows }: { rows: PortfolioWorkflowSequenceRow[] }) {
  return (
    <div>
      <SectionLabel>How the Workflows Connect</SectionLabel>
      <SectionHeading>One direction, start to finish</SectionHeading>
      <div className="flex flex-col gap-3">
        {rows.map((row) => (
          <div key={row.id} className="flex flex-wrap items-center gap-2">
            {row.steps.map((step, index) => {
              const Icon = PORTFOLIO_ICON_MAP[step.icon];
              return (
                <div key={`${row.id}-${step.label}`} className="flex items-center gap-2">
                  <span className="flex items-center gap-1.5 border border-border bg-surface-muted px-2.5 py-1.5 text-xs font-medium text-text-primary">
                    <Icon size={14} className="text-text-secondary" aria-hidden="true" />
                    {step.label}
                  </span>
                  {index < row.steps.length - 1 ? (
                    <ArrowRight size={14} className="shrink-0 text-text-muted" aria-hidden="true" />
                  ) : null}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
