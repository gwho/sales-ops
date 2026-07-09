import Link from "next/link";

/**
 * Phase 8 stub. Proves routing, layout, and semantic-token rendering only.
 * Phase 9 replaces this with the read-only aggregate landing page
 * (per-workflow KPI strips + report cards + entry cards) per
 * context/ui-contract-plan.md — no reusable components are built yet.
 */

const WORKFLOWS = [
  { href: "/order-validation", label: "Order Validation" },
  { href: "/inventory-allocation", label: "Inventory Allocation" },
  { href: "/payment-aging", label: "Payment Aging" },
  { href: "/reports", label: "Reports & Export" },
];

export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <p className="text-xs font-medium uppercase tracking-wide text-text-secondary">
        Sales Admin Automation Toolkit
      </p>
      <h1 className="mt-1 text-2xl font-semibold text-text-primary">Dashboard</h1>
      <p className="mt-2 text-sm text-text-secondary">
        Phase 8 foundation scaffold. Routing, tokens, and project setup are in
        place; workflow screens are built in Phase 9.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {WORKFLOWS.map((w) => (
          <Link
            key={w.href}
            href={w.href}
            className="rounded-xl border border-border bg-surface p-6 shadow-sm transition-colors hover:border-accent"
          >
            <span className="text-base font-semibold text-text-primary">
              {w.label}
            </span>
            <span className="mt-1 block text-xs text-text-muted">
              Phase 9 builds this page
            </span>
          </Link>
        ))}
      </div>
    </main>
  );
}
