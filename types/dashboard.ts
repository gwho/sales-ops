/**
 * Dashboard Latest Results -- mirrors
 * backend/repositories/workflow_results.py's DashboardLatestResults, NOT
 * src/contracts.py. This is GET /api/dashboard's response shape, a
 * dashboard-read aggregate over Output Contracts, not an Output Contract
 * itself -- see docs/adr/0007-session-scoped-workflow-result-persistence.md.
 * Don't merge this into types/index.ts for symmetry; that file mirrors
 * context/ui-contract-plan.md specifically.
 */

import type { InventoryAllocationResult, OrderValidationResult, PaymentAgingResult } from "@/types";

export type DashboardLatestResults = {
  order_validation: OrderValidationResult | null;
  inventory_allocation: InventoryAllocationResult | null;
  payment_aging: PaymentAgingResult | null;
};

/** The X-Persisted response header's three possible values (see ADR 0007). */
export type PersistenceOutcome = "true" | "false" | "skipped";
