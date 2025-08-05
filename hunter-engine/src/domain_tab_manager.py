# (Legacy/alternative) Manages processing of requests grouped by domain.
# - Opens one tab per domain and processes all requests for that domain in sequence.
# - Loads and calls the correct script for each domain.
# - Handles persistence of processed page info.
import os
import importlib.util
import time
import sys
from collections import defaultdict
from playwright.sync_api import TimeoutError
from .human_actions import HumanActions

class DomainTabManager:
    def __init__(self, context, domain_settings, persisted_pages):
        self.context = context
        self.domain_settings = domain_settings
        self.persisted_pages = persisted_pages

    def get_script_and_persist(self, domain):
        if domain in self.domain_settings:
            return self.domain_settings[domain]["script"], self.domain_settings[domain]["persist"]
        return self.domain_settings["default"]["script"], self.domain_settings["default"]["persist"]

    def process_requests(self, domain_to_requests):
        import inspect
        for domain, requests in domain_to_requests.items():
            print(f"Processing {len(requests)} requests for domain: {domain}", file=sys.stdout, flush=True)
            page = self.context.new_page()
            script_name, persist = self.get_script_and_persist(domain)
            script_path = os.path.join(os.path.dirname(__file__), "domain_scripts", f"{script_name}.py")
            script_func = None
            if os.path.exists(script_path):
                spec = importlib.util.spec_from_file_location(script_name, script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                script_func = getattr(module, script_name, None)
                # Check function signature
                if script_func:
                    sig = inspect.signature(script_func)
                    if len(sig.parameters) != 5:
                        print(f"Error: Script function '{script_name}' in {script_path} must accept exactly 5 parameters (page, HumanActions, time, sys, request).", file=sys.stdout, flush=True)
                        script_func = None
            else:
                print(f"Script {script_name} not found for domain {domain}", file=sys.stdout, flush=True)

            for obj in requests:
                try:
                    TARGET_URL = obj['url']
                    print(f"Visiting {TARGET_URL}", file=sys.stdout, flush=True)
                    page.goto(TARGET_URL, timeout=10000, wait_until="domcontentloaded")
                    page.wait_for_load_state("networkidle")
                    if script_func:
                        # Always call with (page, HumanActions, time, sys, obj)
                        script_func(page, HumanActions, time, sys, obj)
                    if persist:
                        self.persisted_pages.append({
                            "url": TARGET_URL,
                            "domain": domain,
                            "timestamp": time.time()
                        })
                    html = page.content()
                except TimeoutError:
                    print(f"Timeout while trying to reach {obj['url']}.", file=sys.stdout, flush=True)
                    continue
                except Exception as e:
                    print(f"Unhandled error for {obj['url']}: {e}", file=sys.stdout, flush=True)
                    continue
            page.close()
