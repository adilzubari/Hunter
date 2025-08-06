# Main orchestration for the scraping process.
# - Loads domain settings and initializes the browser.
# - Uses TabPoolManager to process requests, always reusing tabs for the same domain.
# - Waits up to 60 seconds for new requests before closing the browser.
# - Persists processed page data.
import sys
import time
import json
from playwright.sync_api import sync_playwright, TimeoutError
from .config import Config
from .browser_manager import BrowserManager
import os
from .tab_pool_manager import TabPoolManager

class Scraper:
    def __init__(self):
        self.browser = None
        self.context = None

    def run_scraper(self):
        SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "domain_settings.json")
        persisted_pages = []
        with open(SETTINGS_FILE, "r") as f:
            settings_data = json.load(f)
        domain_settings = {k: v for k, v in settings_data.items() if k != "persisted_pages"}

        try:
            with sync_playwright() as p:
                print("Starting Playwright...", file=sys.stdout, flush=True)
                browser_manager = BrowserManager(p)
                self.browser, self.context = browser_manager.setup()
                print("Scraper started.", file=sys.stdout, flush=True)

                tab_manager = TabPoolManager(self.context, domain_settings, persisted_pages)
                processed = set()
                wait_time = 60

                def all_queues_empty():
                    # Check if global queue is empty (all processed)
                    global_empty = all(id(obj) in processed for obj in Config.GLOBAL_QUEUE)
                    # No change needed for search_type, just ensure all tasks are processed
                    return global_empty

                # Wait until all queues are empty before starting shutdown timer
                print("Checking if all queues are empty before shutdown timer...", file=sys.stdout, flush=True)
                while not all_queues_empty():
                    print("Waiting for all queues to be empty...", file=sys.stdout, flush=True)
                    time.sleep(2)
                    # Process any new requests that came in
                    new_requests = [obj for obj in Config.GLOBAL_QUEUE if id(obj) not in processed]
                    for obj in new_requests:
                        # Now each obj may have 'search_type' for section-specific logic
                        tab_manager.process_request(obj)
                        processed.add(id(obj))
                    if new_requests and persisted_pages:
                        try:
                            with open(SETTINGS_FILE, "r") as f:
                                settings_data = json.load(f)
                            settings_data["persisted_pages"] = persisted_pages
                            with open(SETTINGS_FILE, "w") as f:
                                json.dump(settings_data, f, indent=2)
                            print(f"Persisted info for {len(persisted_pages)} pages to {SETTINGS_FILE}", file=sys.stdout, flush=True)
                        except Exception as e:
                            print(f"Failed to persist page info: {e}", file=sys.stdout, flush=True)

                print("All queues are empty. Starting 60s shutdown timer...", file=sys.stdout, flush=True)
                last_activity = time.time()
                while True:
                    print(f"Waiting up to {wait_time} seconds for new requests before closing browser...", file=sys.stdout, flush=True)
                    while time.time() - last_activity < wait_time:
                        time.sleep(1)
                        new_requests = [obj for obj in Config.GLOBAL_QUEUE if id(obj) not in processed]
                        if new_requests:
                            for obj in new_requests:
                                # Now each obj may have 'search_type' for section-specific logic
                                tab_manager.process_request(obj)
                                processed.add(id(obj))
                            if persisted_pages:
                                try:
                                    with open(SETTINGS_FILE, "r") as f:
                                        settings_data = json.load(f)
                                    settings_data["persisted_pages"] = persisted_pages
                                    with open(SETTINGS_FILE, "w") as f:
                                        json.dump(settings_data, f, indent=2)
                                    print(f"Persisted info for {len(persisted_pages)} pages to {SETTINGS_FILE}", file=sys.stdout, flush=True)
                                except Exception as e:
                                    print(f"Failed to persist page info: {e}", file=sys.stdout, flush=True)
                            print("Processed new requests. Resetting shutdown timer.", file=sys.stdout, flush=True)
                            last_activity = time.time()
                            break
                    else:
                        print(f"No new requests for {wait_time} seconds. Closing browser...", file=sys.stdout, flush=True)
                        break

                tab_manager.close_all_tabs()
                self.context.storage_state(path=Config.SESSION_FILE)
                self.browser.close()
        except TimeoutError:
            import traceback
            print("Timeout while trying to reach the page.", file=sys.stdout, flush=True)
            traceback.print_exc()
        except Exception as e:
            import traceback
            print(f"Unhandled error: {e}", file=sys.stdout, flush=True)
            traceback.print_exc()
