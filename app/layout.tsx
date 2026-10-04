import type { Metadata } from "next";
import "./globals.css";

function siteUrl() {
  const configured = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  const production = process.env.VERCEL_PROJECT_PRODUCTION_URL?.trim();
  const value = configured || production || "localhost:3000";
  return value.startsWith("http") ? value : `https://${value}`;
}

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl()),
  title: {
    default: "REALITYX — Verify What’s Real",
    template: "%s | REALITYX",
  },
  description: "Evidence-based digital reality verification with a future-ready security and trust architecture.",
  keywords: ["REALITYX", "digital verification", "media authenticity", "AI trust", "evidence", "provenance", "cryptographic attestation"],
  alternates: { canonical: "/" },
  robots: { index: true, follow: true },
};

export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>{children}</body></html>;
}
