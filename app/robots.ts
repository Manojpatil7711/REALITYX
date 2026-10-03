import type { MetadataRoute } from "next";

function siteUrl() {
  const configured = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  const production = process.env.VERCEL_PROJECT_PRODUCTION_URL?.trim();
  const value = configured || production || "localhost:3000";
  return value.startsWith("http") ? value : `https://${value}`;
}

export default function robots(): MetadataRoute.Robots {
  const base = siteUrl().replace(/\/$/, "");
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/", "/v1/", "/admin/", "/owner/"],
    },
    sitemap: `${base}/sitemap.xml`,
  };
}
