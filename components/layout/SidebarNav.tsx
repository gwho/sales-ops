"use client";

// External imports
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, ClipboardList, PackageCheck, Clock, FileSpreadsheet } from "lucide-react";

// Internal imports
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/order-validation", label: "Order Validation", icon: ClipboardList },
  { href: "/inventory-allocation", label: "Inventory Allocation", icon: PackageCheck },
  { href: "/payment-aging", label: "Payment Aging", icon: Clock },
  { href: "/reports", label: "Reports", icon: FileSpreadsheet },
] as const;

// Component
export function SidebarNav() {
  const pathname = usePathname();

  return (
    <nav className="flex h-full w-60 shrink-0 flex-col gap-1 overflow-y-auto bg-surface-inverse p-4">
      <span className="mb-4 px-2 text-xs font-medium uppercase tracking-wide text-text-on-inverse-muted">
        Sales Admin Automation Toolkit
      </span>
      {NAV_ITEMS.map((item) => {
        const active = pathname === item.href;
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-accent text-text-on-accent"
                : "text-text-on-inverse-muted hover:bg-surface-inverse-hover hover:text-text-on-inverse",
            )}
          >
            <Icon size={16} className="shrink-0" aria-hidden="true" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
