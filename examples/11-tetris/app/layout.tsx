import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tetris - Full-Stack Game",
  description: "Classic Tetris game with FastAPI backend and Next.js frontend",
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
