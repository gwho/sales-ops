import Link from "next/link";

const NAV_ANCHORS = [
  { href: "#workflows", label: "Workflows" },
  { href: "#value", label: "Value" },
  { href: "#tech", label: "Tech" },
] as const;

export function PublicHeader() {
  return (
    <header className="sticky top-0 z-10 border-b border-border bg-background">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
        <span className="text-xs font-medium uppercase tracking-widest text-text-secondary">
          Sales Admin Automation Toolkit
        </span>
        <nav className="flex items-center gap-5">
          {NAV_ANCHORS.map((anchor) => (
            <a
              key={anchor.href}
              href={anchor.href}
              className="text-xs text-text-secondary transition-colors hover:text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              {anchor.label}
            </a>
          ))}
          <Link
            href="/dashboard"
            className="bg-accent px-3 py-1.5 text-xs font-medium text-text-on-accent transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
          >
            Open Dashboard
          </Link>
        </nav>
      </div>
    </header>
  );
}
