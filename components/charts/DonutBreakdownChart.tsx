"use client";

// External imports
import { useState } from "react";

// Internal imports
import type { Tone } from "@/components/workflow/StatusBadge";
import { formatNumber } from "@/lib/formatters";

// Types
type DonutSegment = {
  label: string;
  value: number;
  tone: Tone;
};

type DonutBreakdownChartProps = {
  segments: DonutSegment[];
  totalLabel: string;
};

const STROKE_TONE_CLASSES: Record<Tone, string> = {
  success: "stroke-success",
  warning: "stroke-warning",
  danger: "stroke-danger",
  info: "stroke-info",
  neutral: "stroke-text-muted",
};

const DOT_TONE_CLASSES: Record<Tone, string> = {
  success: "bg-success",
  warning: "bg-warning",
  danger: "bg-danger",
  info: "bg-info",
  neutral: "bg-text-muted",
};

const RADIUS = 35;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

/**
 * Pure-SVG donut (stacked circle strokes) — no charting library. Tone comes
 * from the caller (see components/workflow/StatusBadge.tsx's tone helpers),
 * never decided here, so a chart segment and a table badge for the same
 * status always match.
 */
export function DonutBreakdownChart({ segments, totalLabel }: DonutBreakdownChartProps) {
  const total = segments.reduce((sum, segment) => sum + segment.value, 0);
  const [hoveredLabel, setHoveredLabel] = useState<string | null>(null);
  const hovered = segments.find((segment) => segment.label === hoveredLabel) ?? null;
  const hoveredPercent = hovered && total > 0 ? Math.round((hovered.value / total) * 100) : null;

  const clearHover = () => setHoveredLabel(null);

  return (
    <div className="flex items-center gap-6">
      <div className="relative h-32 w-32 shrink-0">
        <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
          {total === 0 ? (
            <circle cx="50" cy="50" r={RADIUS} fill="none" strokeWidth="14" className="stroke-border-strong" />
          ) : (
            (() => {
              let offset = 0;
              return segments
                .filter((segment) => segment.value > 0)
                .map((segment) => {
                  const length = (segment.value / total) * CIRCUMFERENCE;
                  const dashArray = `${length} ${CIRCUMFERENCE - length}`;
                  const dashOffset = -offset;
                  offset += length;
                  const percent = total > 0 ? Math.round((segment.value / total) * 100) : 0;
                  const segmentTitle = `${segment.label}: ${formatNumber(segment.value)} (${percent}%)`;
                  return (
                    <circle
                      key={segment.label}
                      cx="50"
                      cy="50"
                      r={RADIUS}
                      fill="none"
                      strokeWidth="14"
                      strokeDasharray={dashArray}
                      strokeDashoffset={dashOffset}
                      tabIndex={0}
                      role="img"
                      aria-label={segmentTitle}
                      onMouseEnter={() => setHoveredLabel(segment.label)}
                      onMouseLeave={clearHover}
                      onFocus={() => setHoveredLabel(segment.label)}
                      onBlur={clearHover}
                      className={`cursor-default transition-opacity duration-150 hover:opacity-70 focus:opacity-70 focus:outline-none ${STROKE_TONE_CLASSES[segment.tone]}`}
                    >
                      <title>{segmentTitle}</title>
                    </circle>
                  );
                });
            })()
          )}
        </svg>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-semibold text-text-primary">{formatNumber(total)}</span>
          <span className="text-[10px] uppercase tracking-wide text-text-muted">{totalLabel}</span>
        </div>
        {hovered ? (
          <div className="pointer-events-none absolute -bottom-3 -left-3 z-10 min-w-[9rem] rounded-lg border border-border bg-surface px-3 py-2 shadow-md">
            <p className="text-sm font-semibold text-text-primary">{hovered.label}</p>
            <p className="text-xs text-text-secondary">
              {formatNumber(hovered.value)} {totalLabel.toLowerCase()} ({hoveredPercent}%)
            </p>
          </div>
        ) : null}
      </div>
      <div className="flex flex-1 flex-col gap-2">
        {segments.map((segment) => {
          const percent = total > 0 ? Math.round((segment.value / total) * 100) : 0;
          const isHovered = hoveredLabel === segment.label;
          return (
            <div
              key={segment.label}
              tabIndex={0}
              onMouseEnter={() => setHoveredLabel(segment.label)}
              onMouseLeave={clearHover}
              onFocus={() => setHoveredLabel(segment.label)}
              onBlur={clearHover}
              className={`flex cursor-default items-center justify-between gap-4 rounded px-1 py-0.5 text-xs text-text-secondary transition-colors focus:outline-none ${isHovered ? "bg-surface-muted" : ""}`}
            >
              <span className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT_TONE_CLASSES[segment.tone]}`} />
                {segment.label}
              </span>
              <span className="font-semibold tabular-nums text-text-primary">
                {formatNumber(segment.value)}
                {isHovered ? <span className="ml-1 font-normal text-text-muted">({percent}%)</span> : null}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
