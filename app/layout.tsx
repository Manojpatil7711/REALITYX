import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "REALITYX — Verify What’s Real",
  description: "Evidence-based digital reality verification with a future-ready security and trust architecture.",
  keywords: ["REALITYX","digital verification","media authenticity","AI trust","evidence","provenance","cryptographic attestation"],
};

export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>{children}</body></html>;
}
