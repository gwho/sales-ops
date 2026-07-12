// External imports
import { type ReactNode } from "react";

// Types
type TableSectionHeadingProps = {
  icon: ReactNode;
  title: string;
  caption?: string;
  /** Optional compact top-right text link (e.g. "View all") — never a large CTA. */
  action?: ReactNode;
};

/** Icon + title + one-line business-readable caption, used above every table/panel section. */
export function TableSectionHeading({ icon, title, caption, action }: TableSectionHeadingProps) {
  return (
    <div className="flex items-start justify-between gap-3">
      <div>
        <h2 className="flex items-center gap-2 text-base font-semibold text-text-primary">
          <span className="text-text-secondary" aria-hidden="true">
            {icon}
          </span>
          {title}
        </h2>
        {caption ? <p className="mt-1 text-xs text-text-muted">{caption}</p> : null}
      </div>
      {action ? <div className="shrink-0 pt-0.5">{action}</div> : null}
    </div>
  );
}
