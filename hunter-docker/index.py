import sys
import time
import random
import logging
import asyncio
import schedule
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from src.core.storage.smanager import SManager
from src.core.actions.typing import human_like_typing
from src.core.actions.mouse import human_like_mouse_move
from playwright.async_api import async_playwright, TimeoutError
from src.core.browser.BrowserManager import BrowserManager

TARGET_URLS = [
    {"URL": "https://news.yahoo.com"},
    {"URL": "https://news.google.com/"},
    {"URL": "https://www.youtube.com/"},
    {"URL": "https://mail.google.com/"},
]

# class BrowserManager:
#     def __init__(self, s_manager):
#         self.s = s_manager
#         self.browser = None
#         self.context = None
#         self.tab_manager = TabManager()

#     async def setup(self):
#         self.playwright = await async_playwright().start()
#         self.browser = await self.playwright.chromium.launch(
#             headless=self.s.HEADLESS,
#             slow_mo=random.randint(150, 300),
#             args=["--disable-dev-shm-usage"]
#         )
#         self.context = await self.browser.new_context(
#             user_agent=random.choice(self.s.USER_AGENTS),
#             viewport=random.choice(self.s.VIEWPORTS),
#             locale=random.choice(self.s.LOCALES),
#             timezone_id=random.choice(self.s.TIMEZONES),
#             geolocation={"longitude": -74.0060, "latitude": 40.7128},
#             permissions=["geolocation"],
#             java_script_enabled=True,
#             bypass_csp=True,
#             ignore_https_errors=True,
#             storage_state="auth.json"
#         )
#         await self.context.new_page()  # To avoid empty browser screen

#     async def open_tab(self, url):
#         tab = self.tab_manager.get_or_create_tab(url)

#         if not tab.page:
#             tab.page = await self.context.new_page()
#             asyncio.create_task(self.process_tab(tab))

#         await tab.sub_queue.put(url)

#     async def process_tab(self, tab: TabConfig):
#         tab.active = True
#         while True:
#             if tab.sub_queue.empty():
#                 if tab.persist:
#                     if time.time() - tab.last_active > tab.idle_timeout:
#                         print(f"🕒 Tab for {tab.domain} idle timeout. Closing.")
#                         break
#                     await asyncio.sleep(5)
#                     continue
#                 else:
#                     break

#             url = await tab.sub_queue.get()
#             try:
#                 print(f"🌐 Navigating to {url} on domain tab {tab.domain}")
#                 await tab.page.goto("about:blank")
#                 await asyncio.sleep(1)
#                 await tab.page.goto(url, timeout=10000, wait_until="domcontentloaded")
#                 tab.last_active = time.time()
#                 await asyncio.sleep(10)  # simulate processing
#             except TimeoutError:
#                 print(f"⚠️ Timeout loading {url}")
#             except Exception as e:
#                 print(f"❌ Error loading {url}: {e}")

#         if not tab.persist:
#             try:
#                 await tab.page.close()
#             except:
#                 pass
#             tab.page = None
#             self.tab_manager.remove_tab(tab)

#     async def shutdown(self):
#         await self.browser.close()
#         await self.playwright.stop()

class ScraperApp:
    def __init__(self):
        self.s = SManager()
        self.MAX_CONCURRENT_TABS = 5
        self.QUEUE_EMPTY_TIMEOUT = 10
        self.POLL_INTERVAL = 2
        self.queue = asyncio.Queue()
        self.active_tasks = set()
        self.context = None
        self.browser = BrowserManager(self.s)

    # async def setup(self):
    #     self.playwright = await async_playwright().start()
    #     self.browser = await self.playwright.chromium.launch(
    #         headless=self.s.HEADLESS,
    #         slow_mo=random.randint(150, 300),
    #         args=["--disable-dev-shm-usage"]
    #     )
    #     self.context = await self.browser.new_context(
    #         user_agent=random.choice(self.s.USER_AGENTS),
    #         viewport=random.choice(self.s.VIEWPORTS),
    #         locale=random.choice(self.s.LOCALES),
    #         timezone_id=random.choice(self.s.TIMEZONES),
    #         geolocation={"longitude": -74.0060, "latitude": 40.7128},
    #         permissions=["geolocation"],
    #         java_script_enabled=True,
    #         bypass_csp=True,
    #         ignore_https_errors=True,
    #         storage_state="auth.json"
    #     )
    #     await self.context.new_page()  # To avoid empty browser screen
    #     for url in TARGET_URLS:
    #         await self.queue.put(url)

    # async def handle_page(self, url_obj, max_retries=3):
    #     url = url_obj["URL"]
    #     task_id = id(asyncio.current_task())
    #     self.active_tasks.add(task_id)
    #     page = await self.context.new_page()

    #     for attempt in range(1, max_retries + 1):
    #         try:
    #             print(f"[{task_id}] Attempt {attempt}: Loading {url}")
    #             await page.goto("about:blank")
    #             await asyncio.sleep(1)
    #             await page.goto(url, timeout=10000, wait_until="domcontentloaded")

    #             print(f"[{task_id}] ✅ Loaded: {url}")
    #             html = await page.content()
    #             await asyncio.sleep(10)
    #             break
    #         except TimeoutError:
    #             print(f"[{task_id}] ⚠️ Timeout on attempt {attempt}")
    #         except PlaywrightError as e:
    #             print(f"[{task_id}] ❌ PlaywrightError: {e}")
    #         except Exception as e:
    #             print(f"[{task_id}] ❌ Other Error: {e}")
    #         await asyncio.sleep(random.uniform(2, 5))
    #     else:
    #         print(f"[{task_id}] ❌ Gave up after {max_retries} retries")

    #     self.active_tasks.remove(task_id)
    #     try:
    #         await page.close()
    #     except:
    #         pass

    # async def task_manager(self):
    #     idle_time = 0
    #     while True:
    #         if not self.queue.empty() and len(self.active_tasks) < self.MAX_CONCURRENT_TABS:
    #             while not self.queue.empty() and len(self.active_tasks) < self.MAX_CONCURRENT_TABS:
    #                 url_obj = await self.queue.get()
    #                 asyncio.create_task(self.handle_page(url_obj))
    #                 self.queue.task_done()
    #                 idle_time = 0
    #         elif self.queue.empty() and len(self.active_tasks) == 0:
    #             idle_time += self.POLL_INTERVAL
    #             if idle_time >= self.QUEUE_EMPTY_TIMEOUT:
    #                 print("⌛ Idle timeout reached.")
    #                 break
    #         await asyncio.sleep(self.POLL_INTERVAL)

    # async def shutdown(self):
    #     await self.s.save_clean_storage_state(self.context, path=self.s.SESSION_FILE)
    #     await self.browser.close()
    #     await self.playwright.stop()
    #     print("✅ Shutdown complete.")

    async def populate_queue(self, urls):
        for url in urls:
            await self.queue.put(url)

    async def task_manager(self):
        idle_time = 0
        while True:
            if not self.queue.empty() and len(self.active_tasks) < self.MAX_CONCURRENT_TABS:
                while not self.queue.empty() and len(self.active_tasks) < self.MAX_CONCURRENT_TABS:
                    url_obj = await self.queue.get()
                    await self.browser.open_tab(url_obj["URL"])
                    idle_time = 0
            elif self.queue.empty() and len(self.active_tasks) == 0:
                idle_time += self.POLL_INTERVAL
                if idle_time >= self.QUEUE_EMPTY_TIMEOUT:
                    print("⌛ Idle timeout reached.")
                    break
            await asyncio.sleep(self.POLL_INTERVAL)

    async def run(self):
        try:
            await self.browser.setup()
            await self.populate_queue(TARGET_URLS)
            await self.task_manager()
        finally:
            await self.browser.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(ScraperApp().run())
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        print("🔚 Exiting.")
