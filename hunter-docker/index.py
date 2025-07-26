import sys
import time
import random
import logging
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError
import schedule
from src.core.storage.smanager import SManager
from src.core.actions.mouse import human_like_mouse_move
from src.core.actions.typing import human_like_typing

s = SManager()

TARGET_URLS = [
    # {
    #     "URL": "https://maps.google.com",
    # },
    # {
    #     "URL": "https://www.linkedin.com/jobs/search/?currentJobId=4268976586&keywords=software%20engineer&origin=JOBS_HOME_SEARCH_BUTTON",
    # },
    # {
    #     "URL": "https://www.google.com",
    # },
    {
        "URL": "https://news.yahoo.com",
    },
]

def browser_setup(p):
    try:
        browser = p.chromium.launch(headless=s.HEADLESS, slow_mo=random.randint(150, 300), args=["--disable-dev-shm-usage"])
        context = browser.new_context(
            user_agent=random.choice(s.USER_AGENTS),
            viewport=random.choice(s.VIEWPORTS),
            locale=random.choice(s.LOCALES),
            timezone_id=random.choice(s.TIMEZONES),
            geolocation={"longitude": -74.0060, "latitude": 40.7128},
            permissions=["geolocation"],
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
            storage_state="auth.json"
        )
        return browser, context
    except TimeoutError:
        print("Timeout while trying to reach the page.", file=sys.stdout, flush=True)
    except Exception as e:
        print(f"Unhandled error: {e}", file=sys.stdout, flush=True)

def run_scraper():
    try:
        with sync_playwright() as p:
            print("Starting Playwright...", file=sys.stdout, flush=True)
            browser, context = browser_setup(p)
            print("Scraper started.", file=sys.stdout, flush=True)

            def load_page(obj):
                try:
                    TARGET_URL = obj['URL']
                    print(f"Visiting {TARGET_URL}", file=sys.stdout, flush=True)
                    page = context.new_page()
                    # page2 = context.new_page()
                    page.goto(TARGET_URL, timeout=10000, wait_until="domcontentloaded")
                    # page2.goto("https://news.yahoo.com", timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_load_state("networkidle")

                    if "google.com" in TARGET_URL:
                        # try:
                            print("Performing Google search interaction...", file=sys.stdout, flush=True)

                            search_query = "Indian news"
                            print(f"Typing search query: {search_query}", file=sys.stdout, flush=True)

                            search_box_selector = "textarea:visible"
                            # page.wait_for_selector(search_box_selector, timeout=2000)
                            time.sleep(random.uniform(0.5, 1.5))  # wait for the search box to be ready

                            human_like_mouse_move(page, search_box_selector)
                            page.click(search_box_selector, delay=random.randint(100, 300))

                            time.sleep(random.uniform(0.4, 1.0))  # small pause before typing

                            human_like_typing(search_query, page)

                            page.keyboard.press("Enter")
                            # page.wait_for_timeout(random.randint(3000, 4000))
                            time.sleep(random.uniform(1.5, 3.0))  # wait for search results to load

                            # Extract <a> links inside element with id 'center-col' and role 'main'
                            print("Extracting search result links...", file=sys.stdout, flush=True)
                            # Find all <a> tags under the element with id 'search' (or 'center-col') and role 'main'
                            search_result_selector = "#search a"
                            print(f"Using selector: {search_result_selector}", file=sys.stdout, flush=True)
                            links = page.locator(search_result_selector).all()
                            print("Google search result links inside #center-col[role='main']:", file=sys.stdout, flush=True)
                            for link in links:
                                print(link.get_attribute("href"), file=sys.stdout, flush=True)

                        #     print("⚠️ Solve the CAPTCHA manually in the browser...", file=sys.stdout, flush=True)
                        #     input("✅ Press Enter after solving it...")
                        # except Exception as e:
                        #     page.screenshot(path="google_debug.png", full_page=True)
                        #     with open("google_debug.html", "w", encoding="utf-8") as f:
                        #         f.write(page.content())
                        #     print("Captured screenshot and HTML for debugging.", file=sys.stdout, flush=True)



                    # Human-like interaction
                    # page.wait_for_timeout(random.randint(1000, 3000))
                    # page.mouse.move(random.randint(300, 600), random.randint(300, 600))
                    # page.mouse.wheel(0, random.randint(1000, 2000))
                    # page.keyboard.press("PageDown")
                    # page.wait_for_timeout(random.randint(1000, 2500))

                    # Get HTML content
                    html = page.content()
                except TimeoutError:
                    print(f"Timeout while trying to reach {obj['URL']}.", file=sys.stdout, flush=True)
                    return None
            
            tasks = [load_page(target) for target in TARGET_URLS]
            # await asyncio.gather(*tasks)

            # for TARGET in TARGET_URLS:
            #     load_page(TARGET)
                # TARGET_URL = TARGET['URL']
                # print(f"Visiting {TARGET_URL}", file=sys.stdout, flush=True)
                # page = context.new_page()
                # page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")

                # # Human-like interaction
                # page.wait_for_timeout(random.randint(1000, 3000))
                # page.mouse.move(random.randint(300, 600), random.randint(300, 600))
                # page.mouse.wheel(0, random.randint(1000, 2000))
                # page.keyboard.press("PageDown")
                # page.wait_for_timeout(random.randint(1000, 2500))

                # Get HTML content
                # html = page.content()

                # 💡 Save the page for debugging
                # with open("debug_page.html", "w", encoding="utf-8") as f:
                #     f.write(html)

                # df = extract_data_from_html(html)

                # if df.empty:
                #     logging.warning("No data extracted. Possibly blocked or structure changed.")
                # else:
                #     try:
                #         existing = pd.read_csv(s.OUTPUT_FILE)
                #         df = pd.concat([existing, df]).drop_duplicates(subset='url', keep='last')
                #     except FileNotFoundError:
                #         print("CSV file not found. Creating new.", file=sys.stdout, flush=True)

                #     df.to_csv(s.OUTPUT_FILE, index=False)
                #     print(f"Saved {len(df)} unique records.", file=sys.stdout, flush=True)

            print("Waiting for 10 seconds before closing the browser...", file=sys.stdout, flush=True)
            time.sleep(10)

            # Save browser context (cookies + localStorage)
            context.storage_state(path="auth.json")
            browser.close()

    except TimeoutError:
        print("Timeout while trying to reach the page.", file=sys.stdout, flush=True)
    except Exception as e:
        print(f"Unhandled error: {e}", file=sys.stdout, flush=True)

# Schedule
# schedule.every().day.at("08:00").do(run_scraper)

if __name__ == "__main__":
    try:
        print("Starting execution...", file=sys.stdout, flush=True)
        run_scraper()
        # while True:
            # schedule.run_pending()
            # time.sleep(60)
            # run_scraper()
    except KeyboardInterrupt:
        print("Exiting script.", file=sys.stdout, flush=True)

