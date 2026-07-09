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

// Types
export type DataTableColumn<T> = {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  sortable?: boolean;
  sortValue?: (row: T) => string | number;
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
 * Always a Client Component in Phase 9 (single file, no server fallback).
 * Sorting only activates on columns with sortable: true; other tables just
 * render without the sort affordance. No filtering/pagination/TanStack Table
 * yet — mock fixtures are 1-2 rows, nothing to demonstrate. Column-def shape
 * is kept close to what TanStack Table would want for an easy Phase 10 swap.
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
            <TableHeaderCell key={column.key}>
              {column.sortable ? (
                <button
                  type="button"
                  onClick={() => toggleSort(column)}
                  className="inline-flex items-center gap-1 uppercase tracking-wide text-text-secondary hover:text-text-primary"
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
        {sortedData.map((row) => (
          <TableRow key={getRowKey(row)}>
            {columns.map((column) => (
              <TableCell key={column.key}>{column.render(row)}</TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
