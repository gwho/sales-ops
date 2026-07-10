// External imports
import { type HTMLAttributes } from "react";

// Internal imports
import { cn } from "@/lib/utils";

// Types
type CardProps = HTMLAttributes<HTMLDivElement>;

// Component
export function Card({ className, ...props }: CardProps) {
  return (
    <div
      className={cn("rounded-xl border border-border bg-surface p-6 shadow-sm", className)}
      {...props}
    />
  );
}
