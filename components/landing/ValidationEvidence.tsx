import { Section, SectionLabel, SectionHeading } from "@/components/landing/Section";
import { landingValidationEvidence } from "@/lib/content/landing-evidence";
import type { PortfolioValidationEvidence } from "@/types/portfolio-content";

// Server Component — must stay one. lib/content/landing-evidence.ts must
// never be imported into a Client Component (see decisions.md #10). All
// prose fragments come from `evidence` (content/portfolio JSON); all
// verified facts (message text, row/order counts) come from
// landingValidationEvidence, checked at build time against lib/mock-data.ts.
// Neither this component nor the loader invents copy — see
// docs/architect/landing-page-evidence-and-technical-credibility/decisions.md
// #1-3.
export function ValidationEvidence({ evidence }: { evidence: PortfolioValidationEvidence }) {
  const verified = landingValidationEvidence;

  return (
    <Section id="evidence">
      <SectionLabel>Real Output</SectionLabel>
      <SectionHeading>{evidence.heading}</SectionHeading>
      <div className="max-w-2xl">
        <p className="text-sm leading-relaxed text-text-secondary">
          <span className="font-medium text-text-primary">{verified.orderId}</span> {evidence.duplicateStatement}{" "}
          {evidence.messageLead} <span className="font-medium text-danger">&quot;{verified.errorMessage}&quot;</span>
        </p>
        <p className="mt-3 text-sm leading-relaxed text-text-secondary">
          {evidence.summaryLead}{" "}
          <span className="font-medium text-text-primary">
            {verified.invalidOrders} of {verified.totalOrders}
          </span>{" "}
          {evidence.summaryOutcome}
        </p>
      </div>
    </Section>
  );
}
