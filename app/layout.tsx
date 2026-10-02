import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "REALITYX — Verify What’s Real",
  description: "Fast, evidence-based verification for digital content.",
};

export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>{children}</body></html>;
}
