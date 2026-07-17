import { Section, SectionLabel } from "@/components/landing/Section";

export function TechSection({ tags }: { tags: string[] }) {
  return (
    <Section id="tech">
      <SectionLabel>Technical Stack</SectionLabel>
      <p className="mb-4 text-sm font-medium text-text-primary">Built with</p>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-block border border-border bg-background px-2.5 py-1 text-xs font-medium text-text-secondary"
          >
            {tag}
          </span>
        ))}
      </div>
    </Section>
  );
}
