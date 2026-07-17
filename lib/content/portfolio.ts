import rawContent from "@/content/portfolio/sales-admin-automation-toolkit.json";
import type { PortfolioContent } from "@/types/portfolio-content";

// TypeScript widens JSON-imported string properties (e.g. `icon`) to `string`,
// not to the narrower PortfolioIconName union -- there's no way to get literal-
// union inference from a checked-in .json import without either duplicating
// this content as a .ts const or adding a runtime schema validator, neither of
// which a static, hand-authored, code-reviewed content file warrants. This
// assertion is safe on that basis; every *consumer* of `portfolioContent`
// still gets the narrow, exhaustively-checked types from PortfolioContent.
export const portfolioContent = rawContent as PortfolioContent;
