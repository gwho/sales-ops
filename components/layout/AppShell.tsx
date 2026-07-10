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
    <div className="flex h-screen overflow-hidden bg-background">
      <SidebarNav />
      <div className="flex h-full flex-1 flex-col overflow-hidden">
        <TopHeader />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
