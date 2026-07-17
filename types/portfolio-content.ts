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

export type PortfolioWorkflow = {
  tag: string;
  title: string;
  description: string;
  icon: PortfolioIconName;
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

export type PortfolioContent = {
  hero: PortfolioHero;
  workflows: PortfolioWorkflow[];
  workflowSequence: PortfolioWorkflowSequenceRow[];
  businessValues: PortfolioBusinessValue[];
  techTags: string[];
  boundaryPoints: string[];
};
