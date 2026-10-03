import type { MetadataRoute } from "next";

function siteUrl() {
  const configured = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  const production = process.env.VERCEL_PROJECT_PRODUCTION_URL?.trim();
  const value = configured || production || "localhost:3000";
  return value.startsWith("http") ? value : `https://${value}`;
}

export default function sitemap(): MetadataRoute.Sitemap {
  const base = siteUrl().replace(/\/$/, "");
  return [
    {
      url: base,
      changeFrequency: "weekly",
      priority: 1,
    },
  ];
}
