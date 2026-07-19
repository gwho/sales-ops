import { Section, SectionLabel, SectionHeading } from "@/components/landing/Section";
import type { PortfolioTechnicalHighlight } from "@/types/portfolio-content";

// New, standalone — TechSection.tsx stays focused on the tech-tag list only
// and is not extended. One secondary section, placed after the
// business-evidence content, not in the hero. Wording adapted directly from
// CONTEXT.md's vetted glossary (Anonymous Session ID vs. Saved Workflow
// Result) rather than re-derived, to avoid repeating a wording mistake this
// project already made and fixed once — see
// docs/architect/landing-page-evidence-and-technical-credibility/decisions.md
// #5.
export function TechnicalHighlight({ highlight }: { highlight: PortfolioTechnicalHighlight }) {
  return (
    <Section id="technical-highlight">
      <div className="max-w-2xl">
        <SectionLabel>Technical Detail</SectionLabel>
        <SectionHeading>{highlight.heading}</SectionHeading>
        <p className="text-sm leading-relaxed text-text-secondary">{highlight.body}</p>
      </div>
    </Section>
  );
}
