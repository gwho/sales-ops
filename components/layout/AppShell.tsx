// External imports
import { type ReactNode } from "react";

// Internal imports
import { SidebarNav } from "@/components/layout/SidebarNav";
import { TopHeader } from "@/components/layout/TopHeader";

// Types
type AppShellProps = {
  children: ReactNode;
};

// Component
export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex min-h-screen bg-background">
      <SidebarNav />
      <div className="flex min-h-screen flex-1 flex-col">
        <TopHeader />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
