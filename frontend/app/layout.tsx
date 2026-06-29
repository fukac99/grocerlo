import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Grocerlo",
  description: "Minimal grocery price comparison for supported retailer data.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
