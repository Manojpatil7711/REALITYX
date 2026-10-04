import type { MetadataRoute } from "next";

const DEFAULT_SITE_URL = "https://realityx-mv4w-manox.vercel.app";

function siteUrl() {
  const configured = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  const production = process.env.VERCEL_PROJECT_PRODUCTION_URL?.trim();
  const value = configured || production || DEFAULT_SITE_URL;
  return value.startsWith("http") ? value : `https://${value}`;
}

export default function sitemap(): MetadataRoute.Sitemap {
  const base = siteUrl().replace(/\/$/, "");

  return [
    {
      url: base,
      lastModified: new Date("2026-10-05"),
      changeFrequency: "weekly",
      priority: 1,
    },
  ];
}
