// Types
type EmptyStateProps = {
  title: string;
  description?: string;
};

// Component
export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-border bg-surface-subtle p-10 text-center">
      <p className="text-sm font-medium text-text-primary">{title}</p>
      {description ? <p className="text-sm text-text-secondary">{description}</p> : null}
    </div>
  );
}
