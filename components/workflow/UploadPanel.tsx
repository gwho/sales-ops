"use client";

// External imports
import { useId, useState } from "react";

// Internal imports
import { Card } from "@/components/ui/Card";
import { buttonVariants } from "@/components/ui/Button";
import { getSampleFileUrl } from "@/lib/api-client";
import { cn } from "@/lib/utils";

// Types
type UploadPanelProps = {
  label: string;
  requiredColumns: string[];
  accept?: string;
  /** Allowlisted backend/routers/templates.py key, e.g. "orders" -- omit to hide the Sample file link. */
  sampleFileName?: string;
  /** Hands the selected File to the parent page so it can be submitted with the Workflow Request. */
  onFileChange?: (file: File | null) => void;
  /**
   * Displayed filename, controlled by the parent's own file state. Pages hold
   * the File as the source of truth (native pick or "Run sample data" both
   * flow through the same onFileChange -> parent state), so passing this down
   * keeps the panel's display in sync regardless of which path set the file --
   * "Run sample data" bypasses the native <input>, so without this the panel
   * would keep showing "Choose a file..." even after a sample file was loaded
   * and submitted.
   */
  selectedFileName?: string | null;
};

/**
 * Real file picker: accepts a file, shows the filename, and (Phase 10) hands
 * the File object up to the parent page via onFileChange for submission. This
 * component itself still never parses the file -- that stays a FastAPI
 * concern. See ui-rules.md's Upload Panel rules.
 */
export function UploadPanel({
  label,
  requiredColumns,
  accept = ".xlsx",
  sampleFileName,
  onFileChange,
  selectedFileName,
}: UploadPanelProps) {
  const inputId = useId();
  const [fileName, setFileName] = useState<string | null>(null);
  const displayedFileName = selectedFileName !== undefined ? selectedFileName : fileName;

  return (
    <Card className="flex h-full flex-col gap-3">
      <div>
        <span className="text-sm font-semibold text-text-primary">{label}</span>
        <p className="mt-1 text-xs text-text-muted">Accepted file type: {accept}</p>
      </div>

      <p className="text-xs text-text-secondary">
        <span className="font-medium text-text-secondary">Required columns:</span>{" "}
        {requiredColumns.join(", ")}
      </p>

      <div className="mt-auto flex flex-col gap-3">
        <label
          htmlFor={inputId}
          className="flex cursor-pointer items-center justify-between gap-3 rounded-md border border-dashed border-border-strong bg-surface-subtle px-3 py-2 text-sm text-text-secondary hover:border-accent"
        >
          <span className="truncate">{displayedFileName ?? "Choose a file…"}</span>
          <span className="shrink-0 rounded-md bg-accent px-3 py-1 text-xs font-medium text-text-on-accent">
            Browse
          </span>
          <input
            id={inputId}
            type="file"
            accept={accept}
            className="sr-only"
            onChange={(event) => {
              const file = event.target.files?.[0] ?? null;
              setFileName(file?.name ?? null);
              onFileChange?.(file);
            }}
          />
        </label>

        {sampleFileName ? (
          <div className="flex items-center justify-between gap-3">
            <span className="min-w-0 text-xs text-text-muted">Need a starting point? Use the sample file.</span>
            <a
              href={getSampleFileUrl(sampleFileName)}
              download
              className={cn(buttonVariants({ variant: "dark" }), "shrink-0 whitespace-nowrap")}
            >
              Sample file
            </a>
          </div>
        ) : null}
      </div>
    </Card>
  );
}
