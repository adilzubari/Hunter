from playwright.async_api import async_playwright
import random

USER_AGENTS = [...]
VIEWPORTS = [...]
LOCALES = [...]
TIMEZONES = [...]

class browser_session:
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False, slow_mo=random.randint(150, 300))
        self.context = await self.browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport=random.choice(VIEWPORTS),
            locale=random.choice(LOCALES),
            timezone_id=random.choice(TIMEZONES),
            geolocation={"longitude": -74.0060, "latitude": 40.7128},
            permissions=["geolocation"],
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
            storage_state="auth.json"
        )
        return self.context

    async def __aexit__(self, exc_type, exc, tb):
        await self.context.storage_state(path="auth.json")
        await self.browser.close()
        await self.playwright.stop()