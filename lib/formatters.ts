/**
 * Shared display formatters for the workflow pages. No contract field carries
 * a currency code (Field Scope Boundary, Phase 5 decision), so amounts are
 * plain numeric formatting only.
 */

export function formatNumber(value: number): string {
  return value.toLocaleString("en-US");
}

export function formatAmount(value: number): string {
  return value.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/** Formats a "YYYY-MM-DD" contract date without shifting across timezones. */
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/** Formats a "YYYY-MM-DDTHH:mm:ss" contract datetime (no timezone suffix, so it's already local). */
export function formatDateTime(isoDateTime: string): string {
  return new Date(isoDateTime).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}
