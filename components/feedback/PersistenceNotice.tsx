// Types
type PersistenceNoticeProps = {
  className?: string;
};

/**
 * The X-Persisted: false caveat -- not BusinessErrorMessage. The workflow
 * result the user came for is completely fine; only the best-effort save to
 * the dashboard didn't land this run. Never rendered for "true" or
 * "skipped" (see docs/adr/0007-session-scoped-workflow-result-persistence.md's
 * "Write-side UI surfacing" -- status appears only when actionable, matching
 * this project's existing convention of no success chrome).
 */
export function PersistenceNotice({ className }: PersistenceNoticeProps) {
  return (
    <div
      className={`rounded-xl border border-border bg-surface-subtle p-3 text-xs text-text-secondary ${className ?? ""}`}
    >
      Result calculated, but it wasn&apos;t saved to the dashboard. The dashboard may still show your
      last saved result. Run again to retry saving.
    </div>
  );
}
