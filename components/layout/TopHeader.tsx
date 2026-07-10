// Component
export function TopHeader() {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-surface px-6">
      <span className="text-sm font-medium text-text-primary">
        Sales Admin Automation Toolkit
      </span>
      <span className="rounded-full bg-info-subtle px-3 py-1 text-xs font-medium text-info">
        Demo Mode — fictional sample data
      </span>
    </header>
  );
}
