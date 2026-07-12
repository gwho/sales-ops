"use client";

// External imports
import { Menu, X } from "lucide-react";

// Types
type TopHeaderProps = {
  isDrawerOpen: boolean;
  onToggle: () => void;
};

// Component
export function TopHeader({ isDrawerOpen, onToggle }: TopHeaderProps) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-surface px-6">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={isDrawerOpen}
          aria-controls="mobile-sidebar-drawer"
          aria-label={isDrawerOpen ? "Close navigation menu" : "Open navigation menu"}
          className="-ml-2 rounded-md p-2 text-text-primary hover:bg-surface-muted lg:hidden"
        >
          {isDrawerOpen ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}
        </button>
        <span className="text-sm font-medium text-text-primary">
          Sales Admin Automation Toolkit
        </span>
      </div>
      <span className="rounded-full bg-info-subtle px-3 py-1 text-xs font-medium text-info">
        Demo Mode — fictional sample data
      </span>
    </header>
  );
}
