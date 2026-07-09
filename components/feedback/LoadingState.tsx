// Types
type LoadingStateProps = {
  label?: string;
};

// Component
export function LoadingState({ label = "Loading…" }: LoadingStateProps) {
  return (
    <div className="flex items-center justify-center gap-3 rounded-xl border border-border bg-surface p-10">
      <span
        aria-hidden="true"
        className="h-4 w-4 animate-spin rounded-full border-2 border-border border-t-accent"
      />
      <span className="text-sm text-text-secondary">{label}</span>
    </div>
  );
}
