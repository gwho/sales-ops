"use client";

// External imports
import { type ReactNode } from "react";

// Types
type FilterToolbarProps = {
  search?: {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
  };
  children: ReactNode; // FilterSelect instances
  onClear: () => void;
  hasActiveFilters: boolean;
};

/**
 * Compact toolbar above a DataTable: optional search input + FilterSelect
 * dropdowns + a clear action. Purely client-side filtering against already-
 * loaded mock data — never a new fetch, never a new business field.
 */
export function FilterToolbar({ search, children, onClear, hasActiveFilters }: FilterToolbarProps) {
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3">
      {search ? (
        <input
          type="text"
          value={search.value}
          onChange={(event) => search.onChange(event.target.value)}
          placeholder={search.placeholder ?? "Search…"}
          aria-label={search.placeholder ?? "Search"}
          className="w-56 rounded-md border border-border bg-background px-3 py-1.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
        />
      ) : null}
      {children}
      {hasActiveFilters ? (
        <button
          type="button"
          onClick={onClear}
          className="ml-auto text-xs font-medium text-accent hover:text-accent-hover"
        >
          Clear filters
        </button>
      ) : null}
    </div>
  );
}
