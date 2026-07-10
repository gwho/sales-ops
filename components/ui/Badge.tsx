// External imports
import { type HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";

// Internal imports
import { cn } from "@/lib/utils";

// Types
const badgeVariants = cva("inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold", {
  variants: {
    tone: {
      success: "bg-success-subtle text-success",
      warning: "bg-warning-subtle text-warning",
      danger: "bg-danger-subtle text-danger",
      info: "bg-info-subtle text-info",
      neutral: "bg-surface-muted text-text-secondary",
    },
  },
  defaultVariants: {
    tone: "neutral",
  },
});

const DOT_TONE_CLASSES = {
  success: "bg-success",
  warning: "bg-warning",
  danger: "bg-danger",
  info: "bg-info",
  neutral: "bg-text-muted",
} as const;

type BadgeProps = HTMLAttributes<HTMLSpanElement> &
  VariantProps<typeof badgeVariants> & {
    /** Leading tone-colored dot — on by default, matches every current status/priority/severity usage. */
    dot?: boolean;
  };

// Component
export function Badge({ className, tone, dot = true, children, ...props }: BadgeProps) {
  const resolvedTone = tone ?? "neutral";
  return (
    <span className={cn(badgeVariants({ tone: resolvedTone }), className)} {...props}>
      {dot ? <span className={cn("h-1.5 w-1.5 shrink-0 rounded-full", DOT_TONE_CLASSES[resolvedTone])} /> : null}
      {children}
    </span>
  );
}
