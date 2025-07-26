import { Page } from "puppeteer";
import { Listing } from "./types.js";

export async function scrapeGoogleResults(
  page: Page,
  maxResults: number
): Promise<Listing[]> {
  // Wait for search results container
  await page.waitForSelector("div#search", { timeout: 15000 });

  // Basic selectors change often; keep them flexible
  const results = await page.$$eval("div#search div.g", (nodes) =>
    nodes.map((el) => {
      const titleEl = el.querySelector("h3");
      const linkEl = el.querySelector("a[href]");
      const snippetEl = el.querySelector(
        "div[style*='-webkit-line-clamp'], div.VwiC3b, div.IsZvec"
      );
      return {
        title: titleEl?.textContent?.trim() || "",
        url: (linkEl as HTMLAnchorElement)?.href || "",
        snippet: snippetEl?.textContent?.trim() || "",
      };
    })
  );

  return results.filter((r) => r.title && r.url).slice(0, maxResults);
}
