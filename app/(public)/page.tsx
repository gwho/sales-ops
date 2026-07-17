import type { Metadata } from "next";

import { Hero } from "@/components/landing/Hero";
import { WorkflowsSection } from "@/components/landing/WorkflowsSection";
import { WorkflowSequence } from "@/components/landing/WorkflowSequence";
import { Section } from "@/components/landing/Section";
import { ValueSection } from "@/components/landing/ValueSection";
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
      <WorkflowsSection workflows={portfolioContent.workflows} />
      <Section id="how-it-connects">
        <WorkflowSequence rows={portfolioContent.workflowSequence} />
      </Section>
      <ValueSection values={portfolioContent.businessValues} />
      <BoundaryNote points={portfolioContent.boundaryPoints} />
      <TechSection tags={portfolioContent.techTags} />
      <ClosingCta />
    </>
  );
}
