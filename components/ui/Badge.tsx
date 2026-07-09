// External imports
import { type HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";

// Internal imports
import { cn } from "@/lib/utils";

// Types
const badgeVariants = cva("inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium", {
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

type BadgeProps = HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>;

// Component
export function Badge({ className, tone, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ tone }), className)} {...props} />;
}
