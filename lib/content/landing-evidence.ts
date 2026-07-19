/**
 * Build-time-verified data boundary for the landing page's real proof
 * section (ValidationEvidence). Reads its lookup selector from the content
 * JSON (portfolioContent.validationEvidence.orderId/.errorCode) rather than
 * hardcoding it here, so there is exactly one place in the codebase deciding
 * which case is being cited — see
 * docs/architect/landing-page-evidence-and-technical-credibility/decisions.md
 * #2-3.
 *
 * Throws at module-eval time (failing the build) if the cited case no longer
 * matches lib/mock-data.ts's real output — e.g. if sample_data/*.xlsx is
 * regenerated and the flagship duplicate-order case changes shape. This
 * turns future drift into a build failure instead of a stale public claim.
 * No prose lives in this file — only verified facts.
 */

import { orderValidationResult } from "@/lib/mock-data";
import { portfolioContent } from "@/lib/content/portfolio";
import type { ValidationErrorRow } from "@/types";

export type LandingValidationEvidence = {
  orderId: string;
  errorMessage: string;
  rowNumbers: [number, number];
  invalidOrders: number;
  totalOrders: number;
};

function fail(reason: string): never {
  throw new Error(
    `lib/content/landing-evidence.ts: ${reason} — the landing page's ValidationEvidence section can no longer verify its cited claim against lib/mock-data.ts. Update content/portfolio/sales-admin-automation-toolkit.json's validationEvidence selector, or regenerate sample data, so the two stay in sync.`,
  );
}

const { orderId, errorCode } = portfolioContent.validationEvidence;
const { summary, errors } = orderValidationResult;

const matches: ValidationErrorRow[] = errors.filter(
  (row) => row.order_id === orderId && row.error_code === errorCode,
);

if (matches.length !== 2) {
  fail(`expected exactly 2 rows matching order_id "${orderId}" / error_code "${errorCode}", found ${matches.length}`);
}

const [first, second] = matches;

if (first.row_number === second.row_number) {
  fail(`the 2 matching rows for "${orderId}" share the same row_number (${first.row_number}) — expected two distinct source rows`);
}

if (first.error_message !== second.error_message) {
  fail(`the 2 matching rows for "${orderId}" have different error_message values ("${first.error_message}" vs "${second.error_message}")`);
}

const verifiedMessage = first.error_message;

if (typeof summary.duplicate_orders !== "number" || summary.duplicate_orders !== matches.length) {
  fail(`summary.duplicate_orders (${summary.duplicate_orders}) does not equal the verified match count (${matches.length})`);
}

if (typeof summary.invalid_orders !== "number") {
  fail("summary.invalid_orders is missing or not a number");
}

if (typeof summary.total_orders !== "number") {
  fail("summary.total_orders is missing or not a number");
}

export const landingValidationEvidence: LandingValidationEvidence = {
  orderId,
  errorMessage: verifiedMessage,
  rowNumbers: [first.row_number, second.row_number],
  invalidOrders: summary.invalid_orders,
  totalOrders: summary.total_orders,
};
