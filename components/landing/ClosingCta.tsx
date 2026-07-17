import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Section } from "@/components/landing/Section";

const DEMO_LINKS = [
  { href: "/dashboard", label: "Open Dashboard", primary: true },
  { href: "/inventory-allocation", label: "View Inventory Allocation", primary: false },
  { href: "/payment-aging", label: "View Payment Aging", primary: false },
] as const;

export function ClosingCta() {
  return (
    <Section id="demo">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="mb-1 text-lg font-semibold text-text-primary">Explore the live demo</h2>
          <p className="text-sm text-text-secondary">
            All data is fictional. The dashboard and workflows are fully interactive.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          {DEMO_LINKS.map((link) =>
            link.primary ? (
              <Link
                key={link.href}
                href={link.href}
                className="inline-flex items-center gap-2 bg-accent px-5 py-2.5 text-sm font-medium text-text-on-accent transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
              >
                {link.label}
                <ArrowRight size={14} aria-hidden="true" />
              </Link>
            ) : (
              <Link
                key={link.href}
                href={link.href}
                className="inline-flex items-center gap-2 border border-border px-4 py-2.5 text-sm font-medium text-text-primary transition-colors hover:bg-surface-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
              >
                {link.label}
              </Link>
            ),
          )}
        </div>
      </div>
    </Section>
  );
}
