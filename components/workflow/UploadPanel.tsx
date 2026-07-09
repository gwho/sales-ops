"use client";

// External imports
import { useId, useState } from "react";

// Internal imports
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

// Types
type UploadPanelProps = {
  label: string;
  requiredColumns: string[];
  accept?: string;
};

/**
 * Real file picker (accepts a file, shows the filename) but never parses the
 * file and never gates page content — Phase 9 is a static showcase, real
 * parsing/validation is a FastAPI concern (Phase 10). See ui-rules.md's
 * Upload Panel rules.
 */
export function UploadPanel({ label, requiredColumns, accept = ".xlsx" }: UploadPanelProps) {
  const inputId = useId();
  const [fileName, setFileName] = useState<string | null>(null);

  return (
    <Card className="flex flex-col gap-3">
      <div>
        <span className="text-sm font-semibold text-text-primary">{label}</span>
        <p className="mt-1 text-xs text-text-muted">Accepted file type: {accept}</p>
      </div>

      <p className="text-xs text-text-secondary">
        <span className="font-medium text-text-secondary">Required columns:</span>{" "}
        {requiredColumns.join(", ")}
      </p>

      <label
        htmlFor={inputId}
        className="flex cursor-pointer items-center justify-between gap-3 rounded-md border border-dashed border-border-strong bg-surface-subtle px-3 py-2 text-sm text-text-secondary hover:border-accent"
      >
        <span className="truncate">{fileName ?? "Choose a file…"}</span>
        <span className="shrink-0 rounded-md bg-accent px-3 py-1 text-xs font-medium text-text-on-accent">
          Browse
        </span>
        <input
          id={inputId}
          type="file"
          accept={accept}
          className="sr-only"
          onChange={(event) => setFileName(event.target.files?.[0]?.name ?? null)}
        />
      </label>

      <div className="flex items-center justify-between gap-3">
        <span className="text-xs text-text-muted">Need a starting point? Use the sample template.</span>
        <Button
          variant="secondary"
          type="button"
          disabled
          title="Static demo — file parsing arrives with the API layer (Phase 10)"
        >
          Sample template
        </Button>
      </div>
    </Card>
  );
}
