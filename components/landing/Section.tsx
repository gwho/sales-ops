import { type ReactNode } from "react";

import { cn } from "@/lib/utils";

// Shared structural pieces for the public landing page's editorial layout --
// flat, border-divided sections with no rounded corners or shadows, visually
// distinct from the app's Card-based dashboard style (see ui-registry.md's
// "Landing" entry). Scoped to components/landing/ only. Uses font-sans
// (Inter) throughout -- the reference prototype's --font-mono/--font-display
// CSS variables were never defined anywhere in this project's token set and
// are not introduced here; the "label" look is approximated with tracking
// and weight instead of a second font family.

export function Section({
  id,
  children,
  className,
}: {
  id?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section id={id} className={cn("scroll-mt-16 border-b border-border", className)}>
      <div className="mx-auto max-w-5xl px-6 py-12 md:py-16">{children}</div>
    </section>
  );
}

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <p className="mb-5 text-[10px] font-medium uppercase tracking-widest text-text-secondary">{children}</p>
  );
}

export function SectionHeading({ children }: { children: ReactNode }) {
  return <h2 className="mb-6 text-xl font-semibold text-text-primary md:text-2xl">{children}</h2>;
}
