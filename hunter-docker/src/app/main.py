import asyncio
from core.browser.manager import browser_session
from platforms.google.steps import run_google_workflow

TARGETS = [
    {"url": "https://www.google.com", "workflow": run_google_workflow},
    # Add more target workflows here
]

async def run_all():
    async with browser_session() as context:
        tasks = [workflow(context, url) for url, workflow in [(t['url'], t['workflow']) for t in TARGETS]]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run_all())