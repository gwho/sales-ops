// External imports
import { type ReactNode } from "react";

// Types
type TableSectionHeadingProps = {
  icon: ReactNode;
  title: string;
  caption?: string;
};

/** Icon + title + one-line business-readable caption, used above every table/panel section. */
export function TableSectionHeading({ icon, title, caption }: TableSectionHeadingProps) {
  return (
    <div>
      <h2 className="flex items-center gap-2 text-base font-semibold text-text-primary">
        <span className="text-text-secondary" aria-hidden="true">
          {icon}
        </span>
        {title}
      </h2>
      {caption ? <p className="mt-1 text-xs text-text-muted">{caption}</p> : null}
    </div>
  );
}
