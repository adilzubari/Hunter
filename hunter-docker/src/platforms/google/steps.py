import random
import time
from core.actions.mouse import human_like_mouse_move
from core.actions.typing import human_like_typing

async def run_google_workflow(context, url):
    page = await context.new_page()
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(random.uniform(500, 1500))

    search_query = "Indian news"
    search_box_selector = "textarea:visible"

    await human_like_mouse_move(page, search_box_selector)
    await page.click(search_box_selector)
    await human_like_typing(search_query, page)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(random.uniform(1500, 3000))

    links = await page.locator("#search a").all()
    for link in links:
        href = await link.get_attribute("href")
        print(f"[Google] Found link: {href}")