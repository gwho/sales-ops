import type { Metadata } from "next";

import { Hero } from "@/components/landing/Hero";
import { ProofStrip } from "@/components/landing/ProofStrip";
import { WorkflowsSection } from "@/components/landing/WorkflowsSection";
import { ValidationEvidence } from "@/components/landing/ValidationEvidence";
import { WorkflowSequence } from "@/components/landing/WorkflowSequence";
import { Section } from "@/components/landing/Section";
import { ValueSection } from "@/components/landing/ValueSection";
import { TechnicalHighlight } from "@/components/landing/TechnicalHighlight";
import { TechSection } from "@/components/landing/TechSection";
import { BoundaryNote } from "@/components/landing/BoundaryNote";
import { ClosingCta } from "@/components/landing/ClosingCta";
import { portfolioContent } from "@/lib/content/portfolio";

export const metadata: Metadata = {
  title: "Sales Admin Automation Toolkit | Portfolio Case Study",
  description:
    "Order validation, inventory allocation, and payment aging workflows automated with Python and a Next.js dashboard — a portfolio case study.",
};

export default function LandingPage() {
  return (
    <>
      <Hero hero={portfolioContent.hero} />
      <ProofStrip items={portfolioContent.proofStrip} />
      <WorkflowsSection workflows={portfolioContent.workflows} />
      <ValidationEvidence evidence={portfolioContent.validationEvidence} />
      <Section id="how-it-connects">
        <WorkflowSequence rows={portfolioContent.workflowSequence} />
      </Section>
      <ValueSection values={portfolioContent.businessValues} />
      <BoundaryNote points={portfolioContent.boundaryPoints} />
      <TechnicalHighlight highlight={portfolioContent.technicalHighlight} />
      <TechSection tags={portfolioContent.techTags} />
      <ClosingCta />
    </>
  );
}
