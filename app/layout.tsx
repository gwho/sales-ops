import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Sales Admin Automation Toolkit",
  description:
    "Order validation, inventory allocation, payment aging, and report export dashboard.",
};

// Global providers only -- (public) and (workspace) route groups each supply
// their own chrome (public header/footer vs. AppShell's sidebar/top header).
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body
        className="min-h-screen bg-background font-sans text-text-primary"
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
