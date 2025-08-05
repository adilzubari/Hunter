import asyncio
import random
import time
from playwright.async_api import async_playwright, TimeoutError
from .TabManager import TabManager
from .TabConfig import TabConfig

class BrowserManager:
    def __init__(self, s_manager):
        self.s = s_manager
        self.browser = None
        self.context = None
        self.tab_manager = TabManager()

    async def setup(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.s.HEADLESS,
            slow_mo=random.randint(150, 300),
            args=["--disable-dev-shm-usage"]
        )
        self.context = await self.browser.new_context(
            user_agent=random.choice(self.s.USER_AGENTS),
            viewport=random.choice(self.s.VIEWPORTS),
            locale=random.choice(self.s.LOCALES),
            timezone_id=random.choice(self.s.TIMEZONES),
            geolocation={"longitude": -74.0060, "latitude": 40.7128},
            permissions=["geolocation"],
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
            # storage_state="auth.json"
        )
        await self.context.new_page()  # To avoid empty browser screen

    async def open_tab(self, url):
        tab = self.tab_manager.get_or_create_tab(url)

        print(tab)
        print(f"Opening tab for URL: {url} on domain: {tab['domain']}")

        if not tab['page']:
            tab['page'] = await self.context.new_page()
            asyncio.create_task(self.process_tab(tab))

        await tab['sub_queue'].put(url)

    async def process_tab(self, tab: TabConfig):
        tab.active = True
        while True:
            if tab.sub_queue.empty():
                if tab.persist:
                    if time.time() - tab.last_active > tab.idle_timeout:
                        print(f"🕒 Tab for {tab.domain} idle timeout. Closing.")
                        break
                    await asyncio.sleep(5)
                    continue
                else:
                    break

            url = await tab.sub_queue.get()
            try:
                print(f"🌐 Navigating to {url} on domain tab {tab.domain}")
                await tab.page.goto("about:blank")
                await asyncio.sleep(1)
                await tab.page.goto(url, timeout=10000, wait_until="domcontentloaded")
                tab.last_active = time.time()
                await asyncio.sleep(10)  # simulate processing
            except TimeoutError:
                print(f"⚠️ Timeout loading {url}")
            except Exception as e:
                print(f"❌ Error loading {url}: {e}")

        if not tab.persist:
            try:
                await tab.page.close()
            except:
                pass
            tab.page = None
            self.tab_manager.remove_tab(tab)

    async def shutdown(self):
        await self.browser.close()
        await self.playwright.stop()
