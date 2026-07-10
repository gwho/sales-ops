"use client";

// External imports
import { Filter } from "lucide-react";

// Types
type FilterSelectProps = {
  label: string;
  value: string;
  options: string[]; // first entry is conventionally "All"
  onChange: (value: string) => void;
};

/** One labeled dropdown inside a FilterToolbar. Options come from a typed vocabulary or the data itself — never invented. */
export function FilterSelect({ label, value, options, onChange }: FilterSelectProps) {
  return (
    <label className="flex items-center gap-1.5 text-xs">
      <Filter size={12} className="shrink-0 text-text-muted" aria-hidden="true" />
      <span className="font-medium uppercase tracking-wide text-text-muted">Filter</span>
      <span className="text-text-secondary">{label}:</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-md border border-border bg-surface px-2 py-1 text-sm font-semibold text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
