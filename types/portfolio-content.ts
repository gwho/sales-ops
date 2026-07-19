/**
 * Public portfolio landing page content contract.
 *
 * Backs content/portfolio/sales-admin-automation-toolkit.json — every field
 * here must stay in sync with that file's shape. This content is public
 * (deployed, unauthenticated) and reviewed for accuracy separately from
 * code review; see docs/plan/portfolio-landing-page/ for the review note.
 */

// Exhaustive icon-name union — the landing content JSON can't hold JSX, so
// icons are referenced by name and mapped to lucide-react components in
// components/landing/icon-map.tsx. Adding a name here without adding it to
// that map is a type error, not a silently blank icon.
export type PortfolioIconName =
  | "clipboard-check"
  | "package-check"
  | "receipt-text"
  | "file-spreadsheet"
  | "upload"
  | "clipboard-list"
  | "check-circle-2"
  | "truck"
  | "clock"
  | "alert-circle";

export type PortfolioHero = {
  badge: string;
  title: string;
  subtitle: string;
  primaryCtaLabel: string;
  primaryCtaHref: string;
  secondaryCtaLabel: string;
  secondaryCtaAnchor: string; // element id on the landing page, no leading "#"
};

// Closed union of real internal routes — an invalid workflow destination is a
// compile-time error, not a runtime dead link. Added for the Landing Page
// Evidence and Technical Credibility pass (see
// docs/architect/landing-page-evidence-and-technical-credibility/decisions.md
// #8) when WorkflowsSection's cards became real next/link destinations.
export type PortfolioWorkflowHref =
  | "/order-validation"
  | "/inventory-allocation"
  | "/payment-aging"
  | "/reports";

export type PortfolioWorkflow = {
  tag: string;
  title: string;
  description: string;
  icon: PortfolioIconName;
  href: PortfolioWorkflowHref;
};

export type PortfolioWorkflowSequenceStep = {
  icon: PortfolioIconName;
  label: string;
};

export type PortfolioWorkflowSequenceRow = {
  id: string;
  steps: PortfolioWorkflowSequenceStep[];
};

export type PortfolioBusinessValue = {
  heading: string;
  body: string;
};

// Durable, permanent-fact statements only — never a metric that requires an
// update cadence (test counts, ROI). See decisions.md #4.
export type PortfolioProofStrip = string[];

// Prose fragments only. orderId/errorCode are the evidence *selector* — the
// verified message text and counts they resolve to come from
// lib/content/landing-evidence.ts at build time, never hardcoded here or in
// the loader. See decisions.md #1-3.
export type PortfolioValidationEvidence = {
  heading: string;
  orderId: string;
  errorCode: string;
  duplicateStatement: string;
  messageLead: string;
  summaryLead: string;
  summaryOutcome: string;
};

export type PortfolioTechnicalHighlight = {
  heading: string;
  body: string;
};

export type PortfolioContent = {
  hero: PortfolioHero;
  workflows: PortfolioWorkflow[];
  workflowSequence: PortfolioWorkflowSequenceRow[];
  businessValues: PortfolioBusinessValue[];
  proofStrip: PortfolioProofStrip;
  validationEvidence: PortfolioValidationEvidence;
  technicalHighlight: PortfolioTechnicalHighlight;
  techTags: string[];
  boundaryPoints: string[];
};
