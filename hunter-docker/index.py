import sys
import time
import random
import logging
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError
import schedule
from src.core.storage.smanager import SManager
from src.core.actions.mouse import human_like_mouse_move
from src.core.actions.typing import human_like_typing

s = SManager()



MAX_CONCURRENT_TABS = 5
QUEUE_EMPTY_TIMEOUT = 60  # seconds
POLL_INTERVAL = 2  # seconds between new task checks

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
    },{
        "URL": "https://news.google.com/",
    },{
        "URL": "https://www.youtube.com/",
    },{
        "URL": "https://mail.google.com/",
    },
]

async def handle_page(context, url_obj, active_tasks, max_retries=3):
    url = url_obj["URL"]
    task_id = id(asyncio.current_task())
    active_tasks.add(task_id)

    page = await context.new_page()

    for attempt in range(1, max_retries + 1):
        try:
            if attempt == 1:
                print(f"🟢 Task {task_id} [{attempt}/{max_retries}] Opening tab: {url}")
                await page.goto(url, timeout=10000, wait_until="domcontentloaded")
            else:
                print(f"🔄 Task {task_id} [{attempt}/{max_retries}] Reloading tab: {url}")
                await page.reload(timeout=10000, wait_until="domcontentloaded")

            await page.wait_for_load_state("networkidle")

            print(f"✅ Task {task_id} Loaded: {url}")
            html = await page.content()
            # 🔍 Process HTML if needed

            await asyncio.sleep(10)  # Let it stay open for 30 sec or process something
            break  # Success

        except TimeoutError:
            print(f"⚠️ Task {task_id} Timeout [{attempt}/{max_retries}] at: {url}")
        except PlaywrightError as e:
            print(f"🌐 Task {task_id} Playwright error [{attempt}/{max_retries}] on: {url} — {e}")
        except Exception as e:
            print(f"❌ Task {task_id} Other error [{attempt}/{max_retries}] on: {url} — {e}")

        await asyncio.sleep(random.uniform(2, 5))  # ⏳ Backoff
    else:
        print(f"❌ Task {task_id} Gave up on: {url} after {max_retries} retries")

    try:
        active_tasks.remove(task_id)
        await page.close()
    except:
        pass

async def task_manager(context, queue):
    active_tasks = set()
    idle_time = 0

    while True:
        # Cleanup finished tasks
        if not queue.empty() and len(active_tasks) < MAX_CONCURRENT_TABS:
            while not queue.empty() and len(active_tasks) < MAX_CONCURRENT_TABS:
                url_obj = await queue.get()
                asyncio.create_task(handle_page(context, url_obj, active_tasks))
                queue.task_done()
                idle_time = 0  # reset on activity
        elif queue.empty() and len(active_tasks) < 1:
            idle_time += POLL_INTERVAL
            if idle_time >= QUEUE_EMPTY_TIMEOUT:
                print("⌛ Queue idle timeout reached. Stopping.")
                break
        print(f"Active tasks: {len(active_tasks)}")
        print(f"Queue Idle time: {idle_time} seconds")
        await asyncio.sleep(POLL_INTERVAL)

async def run_scraper():
    queue = asyncio.Queue()
    for url in TARGET_URLS:
        await queue.put(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=s.HEADLESS,
            slow_mo=random.randint(150, 300),
            args=["--disable-dev-shm-usage"]
        )

        context = await browser.new_context(
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

        # open an blank tab
        await context.new_page()

        await task_manager(context, queue)

        await context.storage_state(path="auth.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())

