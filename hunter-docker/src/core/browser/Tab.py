import asyncio
import time
from tab_config import TabConfig


class Tab:
    def __init__(self, domain, config, handle_request_cb, close_cb):
        self.domain = domain
        self.config = config
        self.request_queue = asyncio.Queue()
        self.active = True
        self.task = asyncio.create_task(self._run())
        self.handle_request_cb = handle_request_cb  # Injected behavior
        self.close_cb = close_cb  # Callback to TabManager for cleanup

    def is_idle_expired(self):
        return (
            not self.config.get("persist", False)
            or (time.time() - self.config["last_active"] > self.config["idle_timeout"])
        )

    def enqueue_request(self, request):
        self.request_queue.put_nowait(request)
        self.config["last_active"] = time.time()
        self.config["active"] = True

    async def _run(self):
        try:
            while self.active:
                try:
                    request = await asyncio.wait_for(self.request_queue.get(), timeout=10)
                    await self.handle_request_cb(self.domain, request)
                    self.config["last_active"] = time.time()
                except asyncio.TimeoutError:
                    if self.is_idle_expired():
                        break
        finally:
            await self.close()

    async def close(self):
        self.active = False
        self.config["active"] = False
        await self.close_cb(self.domain)
