import type { Metadata } from "next"
import "./globals.css";
import { Button } from "@/components/ui/button";

export const metadata: Metadata = {
  title: "Flooq Underwriter",
  description: "Supports you to create an underwriting report.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-gray-50">
        {children}
      </body>
    </html>
  );
}
