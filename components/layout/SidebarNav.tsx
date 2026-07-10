"use client";

// External imports
import Link from "next/link";
import { usePathname } from "next/navigation";

// Internal imports
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/order-validation", label: "Order Validation" },
  { href: "/inventory-allocation", label: "Inventory Allocation" },
  { href: "/payment-aging", label: "Payment Aging" },
  { href: "/reports", label: "Reports" },
] as const;

// Component
export function SidebarNav() {
  const pathname = usePathname();

  return (
    <nav className="flex h-full w-60 shrink-0 flex-col gap-1 overflow-y-auto border-r border-border bg-surface p-4">
      <span className="mb-4 px-2 text-xs font-medium uppercase tracking-wide text-text-secondary">
        Sales Admin Automation Toolkit
      </span>
      {NAV_ITEMS.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "rounded-md px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-accent-subtle text-accent"
                : "text-text-secondary hover:bg-surface-muted hover:text-text-primary",
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
