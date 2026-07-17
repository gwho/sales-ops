import {
  ClipboardCheck,
  PackageCheck,
  ReceiptText,
  FileSpreadsheet,
  Upload,
  ClipboardList,
  CheckCircle2,
  Truck,
  Clock,
  AlertCircle,
  type LucideIcon,
} from "lucide-react";

import type { PortfolioIconName } from "@/types/portfolio-content";

// Exhaustive map keyed by PortfolioIconName — a name added to that union
// without an entry here is a type error, not a silently blank icon.
export const PORTFOLIO_ICON_MAP: Record<PortfolioIconName, LucideIcon> = {
  "clipboard-check": ClipboardCheck,
  "package-check": PackageCheck,
  "receipt-text": ReceiptText,
  "file-spreadsheet": FileSpreadsheet,
  upload: Upload,
  "clipboard-list": ClipboardList,
  "check-circle-2": CheckCircle2,
  truck: Truck,
  clock: Clock,
  "alert-circle": AlertCircle,
};
