"use client";

// External imports
import { useMemo, useState, type ReactNode } from "react";

// Internal imports
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from "@/components/ui/Table";
import { EmptyState } from "@/components/feedback/EmptyState";
import { cn } from "@/lib/utils";

// Types
export type DataTableColumn<T> = {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  sortable?: boolean;
  sortValue?: (row: T) => string | number;
  /** Allows this column's cell to wrap — reserve for long free text (error messages, suggested actions). Every other column stays single-line. */
  wrap?: boolean;
  /** Right-aligns header + cell — use for numeric/quantity/amount columns. */
  align?: "left" | "right";
};

type DataTableProps<T> = {
  columns: DataTableColumn<T>[];
  data: T[];
  getRowKey: (row: T) => string;
  emptyTitle: string;
  emptyDescription?: string;
};

type SortState = { key: string; direction: "asc" | "desc" } | null;

/**
 * Always a Client Component (single file, no server fallback). Sorting only
 * activates on columns with sortable: true; other tables just render without
 * the sort affordance. Still no pagination/TanStack Table — mock fixtures
 * are small enough that it has nothing to demonstrate. Column-def shape is
 * kept close to what TanStack Table would want for an easy Phase 10 swap.
 *
 * DataTable itself still knows nothing about filtering — pages own filter
 * state (via FilterToolbar/FilterSelect) and pass an already-filtered `data`
 * array in. This revises Phase 9's original "sort only, no filtering"
 * decision (Phase 9.1) but keeps DataTable's own responsibility narrow: it
 * renders whatever rows it's given, sorts them, and falls back to
 * `emptyTitle`/`emptyDescription` when that array is empty — callers decide
 * whether "empty" means "no data at all" or "no rows match the filter."
 */
export function DataTable<T>({
  columns,
  data,
  getRowKey,
  emptyTitle,
  emptyDescription,
}: DataTableProps<T>) {
  const [sort, setSort] = useState<SortState>(null);

  const sortedData = useMemo(() => {
    if (!sort) return data;
    const column = columns.find((c) => c.key === sort.key);
    if (!column?.sortValue) return data;
    const sortValue = column.sortValue;
    const sorted = [...data].sort((a, b) => {
      const va = sortValue(a);
      const vb = sortValue(b);
      if (va < vb) return -1;
      if (va > vb) return 1;
      return 0;
    });
    return sort.direction === "asc" ? sorted : sorted.reverse();
  }, [data, sort, columns]);

  if (data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  function toggleSort(column: DataTableColumn<T>) {
    if (!column.sortable) return;
    setSort((prev) => {
      if (prev?.key !== column.key) return { key: column.key, direction: "asc" };
      return { key: column.key, direction: prev.direction === "asc" ? "desc" : "asc" };
    });
  }

  return (
    <Table>
      <TableHead>
        <TableRow>
          {columns.map((column) => (
            <TableHeaderCell key={column.key} className={column.align === "right" ? "text-right" : undefined}>
              {column.sortable ? (
                <button
                  type="button"
                  onClick={() => toggleSort(column)}
                  className={cn(
                    "inline-flex items-center gap-1 uppercase tracking-wide text-text-secondary hover:text-text-primary",
                    column.align === "right" && "flex-row-reverse",
                  )}
                >
                  {column.header}
                  {sort?.key === column.key ? (sort.direction === "asc" ? "▲" : "▼") : null}
                </button>
              ) : (
                column.header
              )}
            </TableHeaderCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {sortedData.map((row, index) => (
          <TableRow key={getRowKey(row)} className={index % 2 === 1 ? "bg-surface-muted" : undefined}>
            {columns.map((column) => (
              <TableCell
                key={column.key}
                className={cn(
                  !column.wrap && "whitespace-nowrap",
                  column.align === "right" && "text-right tabular-nums",
                )}
              >
                {column.render(row)}
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
