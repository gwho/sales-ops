import Link from "next/link";

/**
 * Phase 8 stub. Proves routing/tokens only. Phase 9 builds the real screen
 * (UploadPanel ×2, ValidationSummary KPIs, Validation Errors + Valid Orders
 * tables) against OrderValidationResult — see context/ui-contract-plan.md.
 */
export default function OrderValidationPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <Link href="/dashboard" className="text-xs font-medium text-accent hover:text-accent-hover">
        ← Dashboard
      </Link>
      <h1 className="mt-3 text-2xl font-semibold text-text-primary">Order Validation</h1>
      <p className="mt-2 text-sm text-text-secondary">
        Phase 8 scaffold placeholder. The validation workflow UI is built in Phase 9.
      </p>
    </main>
  );
}
