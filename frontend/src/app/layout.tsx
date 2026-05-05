import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Infinity Chat | Autonomous AI Swarm",
  description: "Enterprise-grade autonomous software construction engine.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#0f172a] text-[#f8fafc] font-sans">
        {children}
      </body>
    </html>
  );
}
