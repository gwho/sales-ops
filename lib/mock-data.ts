/**
 * Typed access point for the Phase 8 build-time mock JSON.
 *
 * Pages import from here, never from `lib/mock-data/*.json` directly, so the
 * JSON shape is asserted against `types/index.ts` in exactly one place. The
 * JSON itself is regenerated from `tests/contract_fixtures.py` by
 * `scripts/generate_mock_data.py` (build-time only, see that script's header).
 */

import orderValidationData from "@/lib/mock-data/order-validation.json";
import inventoryAllocationData from "@/lib/mock-data/inventory-allocation.json";
import paymentAgingData from "@/lib/mock-data/payment-aging.json";
import reportsData from "@/lib/mock-data/reports.json";

import type {
  OrderValidationResult,
  InventoryAllocationResult,
  PaymentAgingResult,
  ReportManifest,
} from "@/types";

export const orderValidationResult = orderValidationData as OrderValidationResult;
export const inventoryAllocationResult = inventoryAllocationData as InventoryAllocationResult;
export const paymentAgingResult = paymentAgingData as PaymentAgingResult;
export const reportManifests = reportsData as ReportManifest[];

/**
 * "90+ Days Amount" KPI (ui-contract-plan.md): PaymentAgingSummary.aging_bucket_counts is a
 * *count* breakdown, not an *amount* breakdown, so this sums outstanding_amount client-side —
 * a derived display-only aggregate, not new business logic.
 */
export function ninetyPlusDaysAmount(result: PaymentAgingResult): number {
  return result.aging_rows
    .filter((row) => row.aging_bucket === "90+ Days")
    .reduce((sum, row) => sum + row.outstanding_amount, 0);
}
