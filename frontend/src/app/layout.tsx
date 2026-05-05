import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-[#0f172a] text-[#f8fafc]">
        {children}
      </body>
    </html>
  );
}
