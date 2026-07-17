import { Check } from "lucide-react";

import { Section, SectionLabel, SectionHeading } from "@/components/landing/Section";
import type { PortfolioBusinessValue } from "@/types/portfolio-content";

export function ValueSection({ values }: { values: PortfolioBusinessValue[] }) {
  return (
    <Section id="value">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-[1fr_2fr] md:gap-16">
        <div>
          <SectionLabel>Business Value</SectionLabel>
          <SectionHeading>Operational improvements these workflows support</SectionHeading>
          <p className="text-sm leading-relaxed text-text-secondary">
            Each workflow addresses a specific friction point in a typical sales operations environment.
          </p>
        </div>
        <div className="border-t border-border">
          {values.map((value) => (
            <div key={value.heading} className="flex gap-4 border-b border-border py-4 last:border-b-0">
              <div className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center text-accent">
                <Check size={16} aria-hidden="true" />
              </div>
              <div>
                <p className="mb-0.5 text-sm font-medium text-text-primary">{value.heading}</p>
                <p className="text-sm leading-relaxed text-text-secondary">{value.body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
