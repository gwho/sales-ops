// Internal imports
import { cn } from "@/lib/utils";

// Types
type WorkflowStepperProps = {
  steps: string[];
  currentStep: number; // 0-indexed
};

/** Server Component — Phase 9 has no live progress to track, so this renders one fixed step. */
export function WorkflowStepper({ steps, currentStep }: WorkflowStepperProps) {
  return (
    <ol className="flex flex-wrap items-center gap-2">
      {steps.map((step, index) => {
        const state = index < currentStep ? "done" : index === currentStep ? "current" : "upcoming";
        return (
          <li key={step} className="flex items-center gap-2">
            <span
              className={cn(
                "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-medium",
                state === "done" && "bg-success text-text-on-accent",
                state === "current" && "bg-accent text-text-on-accent",
                state === "upcoming" && "bg-surface-muted text-text-secondary",
              )}
            >
              {index + 1}
            </span>
            <span className={cn("text-sm", state === "upcoming" ? "text-text-muted" : "text-text-primary")}>
              {step}
            </span>
            {index < steps.length - 1 ? (
              <span className="mx-1 h-px w-6 bg-border" aria-hidden="true" />
            ) : null}
          </li>
        );
      })}
    </ol>
  );
}
