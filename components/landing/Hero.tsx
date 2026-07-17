import Link from "next/link";
import { ArrowRight } from "lucide-react";

import type { PortfolioHero } from "@/types/portfolio-content";

export function Hero({ hero }: { hero: PortfolioHero }) {
  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-5xl px-6 py-14 md:py-20">
        <span className="mb-4 inline-block border border-border px-2 py-1 text-xs font-medium uppercase tracking-widest text-text-secondary">
          {hero.badge}
        </span>

        <h1 className="mb-4 max-w-2xl text-3xl font-semibold leading-tight text-text-primary md:text-4xl">
          {hero.title}
        </h1>

        <p className="mb-8 max-w-xl text-base leading-relaxed text-text-secondary md:text-lg">
          {hero.subtitle}
        </p>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Link
            href={hero.primaryCtaHref}
            className="inline-flex items-center justify-center gap-2 bg-accent px-5 py-2.5 text-sm font-medium text-text-on-accent transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
          >
            {hero.primaryCtaLabel}
            <ArrowRight size={14} aria-hidden="true" />
          </Link>
          <a
            href={`#${hero.secondaryCtaAnchor}`}
            className="inline-flex items-center justify-center gap-2 border border-border px-5 py-2.5 text-sm font-medium text-text-primary transition-colors hover:bg-surface-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
          >
            {hero.secondaryCtaLabel}
          </a>
        </div>
      </div>
    </section>
  );
}
