import Link from "next/link";

/**
 * Phase 8 stub. Proves routing/tokens only. Phase 9 builds the real screen
 * (PaymentAgingSummary KPIs, aging bucket chart, Follow-up List, Draft Messages,
 * Data Issues) against PaymentAgingResult — see context/ui-contract-plan.md.
 * Badges use direct fields only (aging_bucket, follow_up_priority).
 */
export default function PaymentAgingPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <Link href="/dashboard" className="text-xs font-medium text-accent hover:text-accent-hover">
        ← Dashboard
      </Link>
      <h1 className="mt-3 text-2xl font-semibold text-text-primary">Payment Aging</h1>
      <p className="mt-2 text-sm text-text-secondary">
        Phase 8 scaffold placeholder. The payment aging workflow UI is built in Phase 9.
      </p>
    </main>
  );
}
