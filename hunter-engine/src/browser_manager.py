# Handles browser and context setup using Playwright.
# - Launches the browser with randomized user agent and viewport.
# - Returns the browser and context objects for use in scraping.
import random
from playwright.sync_api import TimeoutError
from .config import Config

class BrowserManager:
    def __init__(self, playwright):
        self.playwright = playwright
        self.browser = None
        self.context = None

    def setup(self):
        try:
            self.browser = self.playwright.chromium.launch(
                headless=Config.HEADLESS,
                slow_mo=random.randint(150, 300),
                args=["--disable-dev-shm-usage"]
            )
            self.context = self.browser.new_context(
                user_agent=random.choice(Config.USER_AGENTS),
                viewport=random.choice(Config.VIEWPORTS),
                locale=random.choice(Config.LOCALES),
                timezone_id=random.choice(Config.TIMEZONES),
                geolocation={"longitude": -74.0060, "latitude": 40.7128},
                permissions=["geolocation"],
                java_script_enabled=True,
                bypass_csp=True,
                ignore_https_errors=True,
                # storage_state=Config.SESSION_FILE
            )
            return self.browser, self.context
        except TimeoutError:
            print("Timeout while trying to reach the page.")
        except Exception as e:
            print(f"Unhandled error: {e}")
