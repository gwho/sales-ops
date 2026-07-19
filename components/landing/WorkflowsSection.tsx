import Link from "next/link";

import { Section, SectionLabel, SectionHeading } from "@/components/landing/Section";
import { PORTFOLIO_ICON_MAP } from "@/components/landing/icon-map";
import type { PortfolioWorkflow } from "@/types/portfolio-content";

// Each card is a full-card next/link to its real workflow route — see
// docs/architect/landing-page-evidence-and-technical-credibility/decisions.md
// #8. The whole card stays the single focusable element (no nested
// interactive children), so its accessible name is the full title +
// description.
export function WorkflowsSection({ workflows }: { workflows: PortfolioWorkflow[] }) {
  return (
    <Section id="workflows">
      <SectionLabel>Automated Workflows</SectionLabel>
      <SectionHeading>What the toolkit demonstrates</SectionHeading>
      <div className="grid grid-cols-1 gap-px bg-border sm:grid-cols-2 lg:grid-cols-4">
        {workflows.map((workflow) => {
          const Icon = PORTFOLIO_ICON_MAP[workflow.icon];
          return (
            <Link
              key={workflow.title}
              href={workflow.href}
              className="flex flex-col gap-4 bg-background p-5 hover:bg-surface-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center bg-surface-muted text-accent">
                  <Icon size={18} aria-hidden="true" />
                </div>
                <span className="mt-1 text-[10px] font-medium uppercase tracking-wider text-text-secondary">
                  {workflow.tag}
                </span>
              </div>
              <div>
                <h3 className="mb-1.5 text-sm font-semibold text-text-primary">{workflow.title}</h3>
                <p className="text-sm leading-relaxed text-text-secondary">{workflow.description}</p>
              </div>
            </Link>
          );
        })}
      </div>
    </Section>
  );
}
