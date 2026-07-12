"use client";

// External imports
import { useEffect, useRef, useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";

// Internal imports
import { SidebarNav } from "@/components/layout/SidebarNav";
import { TopHeader } from "@/components/layout/TopHeader";

// Types
type AppShellProps = {
  children: ReactNode;
};

// Component
export function AppShell({ children }: AppShellProps) {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const pathname = usePathname();
  const [drawerClosedForPathname, setDrawerClosedForPathname] = useState(pathname);
  const drawerRef = useRef<HTMLDivElement>(null);

  // Close the drawer on route change -- adjusting state during render (React's
  // recommended pattern for "state that depends on a prop changing") rather
  // than in a useEffect, which would cause an extra, avoidable render pass.
  if (pathname !== drawerClosedForPathname) {
    setDrawerClosedForPathname(pathname);
    setIsDrawerOpen(false);
  }

  useEffect(() => {
    if (!isDrawerOpen) return;

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setIsDrawerOpen(false);
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isDrawerOpen]);

  // Move focus into the drawer's first link on open. The drawer renders
  // before TopHeader in the DOM (so it stacks visually above the shell without
  // extra z-index juggling), which means a keyboard user tabbing forward from
  // the header's toggle button would otherwise skip straight past it into
  // <main> -- there's no real focus trap here (see plan), but the entry point
  // still has to land inside the drawer, not behind it.
  useEffect(() => {
    if (isDrawerOpen) {
      drawerRef.current?.querySelector("a")?.focus();
    }
  }, [isDrawerOpen]);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <div className="hidden lg:block">
        <SidebarNav />
      </div>

      {isDrawerOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-overlay/50 lg:hidden"
            aria-hidden="true"
            onClick={() => setIsDrawerOpen(false)}
          />
          <div id="mobile-sidebar-drawer" ref={drawerRef} className="fixed inset-y-0 left-0 z-50 lg:hidden">
            <SidebarNav />
          </div>
        </>
      )}

      <div className="flex h-full flex-1 flex-col overflow-hidden">
        <TopHeader isDrawerOpen={isDrawerOpen} onToggle={() => setIsDrawerOpen((value) => !value)} />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
