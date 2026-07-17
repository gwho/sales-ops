import { Info } from "lucide-react";

import { Section, SectionLabel, SectionHeading } from "@/components/landing/Section";

export function BoundaryNote({ points }: { points: string[] }) {
  return (
    <Section>
      <div className="max-w-2xl">
        <SectionLabel>Scope Note</SectionLabel>
        <SectionHeading>What this demo is and is not</SectionHeading>
        <div className="flex items-start gap-4 border border-border bg-surface-muted px-5 py-4">
          <Info size={16} className="mt-0.5 flex-shrink-0 text-text-secondary" aria-hidden="true" />
          <ul className="flex flex-col gap-1">
            {points.map((point) => (
              <li key={point} className="text-sm leading-relaxed text-text-secondary">
                {point}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Section>
  );
}
