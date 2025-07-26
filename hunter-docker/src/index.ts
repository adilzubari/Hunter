import puppeteer from "puppeteer-extra";
import StealthPlugin from "puppeteer-extra-plugin-stealth";
import UserPrefsPlugin from "puppeteer-extra-plugin-user-preferences";
import proxyChain from "proxy-chain";
import fs from "fs-extra";
import path from "path";
// @ts-ignore
import randomWords from "random-words";
import { applyFingerprint } from "./fingerprints";
import { scrapeGoogleResults } from "./scrapeGoogle";
import { sessionDir, sleep } from "./utils";
import { Listing } from "./types";
import { Page } from "puppeteer";

(async () => {
  const {
    PROXY_URL,
    HEADLESS = "true",
    QUERY = "random",
    LANGUAGE = "en-US,en;q=0.9",
    TIMEZONE = "America/New_York",
    MAX_RESULTS = "10",
  } = process.env;

  puppeteer.use(StealthPlugin());
  puppeteer.use(
    UserPrefsPlugin({
      userPrefs: {
        "profile.default_content_setting_values.notifications": 2,
        "intl.accept_languages": LANGUAGE,
      },
    })
  );

  const launchArgs = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-blink-features=AutomationControlled",
    "--window-size=1920,1080",
    "--lang=" + LANGUAGE.split(",")[0],
  ];

  let proxyUrlToUse = PROXY_URL;
  if (PROXY_URL) {
    proxyUrlToUse = await proxyChain.anonymizeProxy(PROXY_URL);
    launchArgs.push(`--proxy-server=${proxyUrlToUse}`);
  }

  const browser = await puppeteer.launch({
    headless: HEADLESS === "true",
    args: launchArgs,
  });

  const context = browser.defaultBrowserContext();
  // Block certain trackers if needed:
  await context.overridePermissions("https://www.google.com", ["geolocation"]);

  const page = await browser.newPage();

  // Load cookies/session if exists
  const cookiesPath = path.join(sessionDir(), "cookies.json");
  if (fs.existsSync(cookiesPath)) {
    const cookies = await fs.readJSON(cookiesPath);
    await page.setCookie(...cookies);
  }

  await applyFingerprint(page, { language: LANGUAGE, timezone: TIMEZONE });

  // Random query
  const query =
    QUERY === "random" ? randomWords({ exactly: 3, join: " " }) : QUERY;

  const queryStr = Array.isArray(query) ? query.join(" ") : query;
  const url = `https://www.google.com/search?q=${encodeURIComponent(
    queryStr
  )}&hl=${LANGUAGE.split(",")[0]}`;
  console.log("🔎 Query:", queryStr);

  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });

    // Handle consent or "I'm Feeling Lucky" prompts etc.
    await handleConsent(page);

    // If "unusual traffic" / captcha page
    if (await isBlocked(page)) {
      console.error(
        "🚫 Blocked by Google. Try different IP/less aggressive behavior."
      );
      await browser.close();
      process.exit(1);
    }

    // Human-like scroll & wait
    await humanScroll(page);

    const listings: Listing[] = await scrapeGoogleResults(
      page,
      parseInt(MAX_RESULTS, 10)
    );
    console.log("✅ Results:", listings);

    // Save results
    const outPath = path.join(process.cwd(), "google_results.json");
    await fs.writeJSON(outPath, { query, listings }, { spaces: 2 });
    console.log("💾 Saved to", outPath);

    // Save cookies
    const newCookies = await page.cookies();
    await fs.writeJSON(cookiesPath, newCookies, { spaces: 2 });
  } catch (err) {
    console.error("❌ Error:", err);
  } finally {
    try {
      await browser.close();
    } catch {}
    if (PROXY_URL && typeof proxyUrlToUse === "string")
      await proxyChain.closeAnonymizedProxy(proxyUrlToUse, true);
  }
})();

async function handleConsent(page: Page) {
  // Google sometimes shows consent screens.
  const consentSelectors = [
    'button[aria-label="Accept all"]',
    "#L2AGLb", // EU consent
    'button[role="button"][jsname][data-ved]',
  ];
  for (const sel of consentSelectors) {
    const btn = await page.$(sel);
    if (btn) {
      await btn.click();
      await sleep(1000);
      break;
    }
  }
}

async function isBlocked(page: Page): Promise<boolean> {
  const bodyText = await page.evaluate(() => document.body.innerText);
  return /unusual traffic|sorry|verify you're a human|detected unusual/i.test(
    bodyText
  );
}

async function humanScroll(page: Page) {
  const height = (await page.evaluate("document.body.scrollHeight")) as number;
  let scrollY = 0;
  while (scrollY < height) {
    const step = Math.floor(Math.random() * 300) + 200;
    scrollY += step;
    await page.evaluate((y) => window.scrollTo(0, y), scrollY);
    await sleep(Math.floor(Math.random() * 600) + 300);
  }
}
