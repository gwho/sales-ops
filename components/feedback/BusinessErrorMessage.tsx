// Types
type BusinessErrorMessageProps = {
  message: string;
};

// Component
/** Always render business-readable copy here, never a raw exception (see ui-rules.md Error Messages). */
export function BusinessErrorMessage({ message }: BusinessErrorMessageProps) {
  return (
    <div role="alert" className="rounded-xl border border-border bg-danger-subtle p-4 text-sm text-danger">
      {message}
    </div>
  );
}
