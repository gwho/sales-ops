import Link from "next/link";

const NAV_ANCHORS = [
  { href: "#workflows", label: "Workflows" },
  { href: "#value", label: "Value" },
  { href: "#tech", label: "Tech" },
] as const;

// Mobile header fix (locked, no fallback branch) — see
// docs/architect/landing-page-evidence-and-technical-credibility/decisions.md
// #9. Below `sm`: anchors hide entirely, brand swaps to a shorter fixed
// string. Verify at 320px specifically, not just "mobile" generically.
export function PublicHeader() {
  return (
    <header className="sticky top-0 z-10 border-b border-border bg-background">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between gap-3 px-6">
        <span className="min-w-0 whitespace-nowrap text-xs font-medium uppercase tracking-widest text-text-secondary">
          <span className="sm:hidden">Sales Ops Toolkit</span>
          <span className="hidden sm:inline">Sales Admin Automation Toolkit</span>
        </span>
        <nav className="flex items-center gap-5">
          <div className="hidden items-center gap-5 sm:flex">
            {NAV_ANCHORS.map((anchor) => (
              <a
                key={anchor.href}
                href={anchor.href}
                className="text-xs text-text-secondary transition-colors hover:text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-accent"
              >
                {anchor.label}
              </a>
            ))}
          </div>
          <Link
            href="/dashboard"
            className="shrink-0 whitespace-nowrap bg-accent px-3 py-1.5 text-xs font-medium text-text-on-accent transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
          >
            Open Dashboard
          </Link>
        </nav>
      </div>
    </header>
  );
}
