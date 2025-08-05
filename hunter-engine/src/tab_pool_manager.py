from src.blocker_wait import wait_for_human_resolution
# Manages browser tabs for each domain.
# - Keeps a mapping of open tabs by domain.
# - Processes requests by reusing the tab for the same domain.
# - Loads and calls the correct script for each domain.
# - Handles persistence of processed page info.
import os
import importlib.util
import time
import sys
from collections import defaultdict
from playwright.sync_api import TimeoutError
from .human_actions import HumanActions

class TabPoolManager:
    def __init__(self, context, domain_settings, persisted_pages):
        self.context = context
        self.domain_settings = domain_settings
        self.persisted_pages = persisted_pages
        self.tabs = {}  # domain -> page

    def get_script_and_persist(self, domain):
        if domain in self.domain_settings:
            return self.domain_settings[domain]["script"], self.domain_settings[domain]["persist"]
        return self.domain_settings["default"]["script"], self.domain_settings["default"]["persist"]

    def process_request(self, obj):
        import inspect
        domain = self._get_domain(obj['url'])
        if domain not in self.tabs:
            self.tabs[domain] = self.context.new_page()
        page = self.tabs[domain]
        script_name, persist = self.get_script_and_persist(domain)
        script_path = os.path.join(os.path.dirname(__file__), "domain_scripts", f"{script_name}.py")
        script_func = None
        if os.path.exists(script_path):
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            script_func = getattr(module, script_name, None)
            if script_func:
                sig = inspect.signature(script_func)
                if len(sig.parameters) != 5:
                    print(f"Error: Script function '{script_name}' in {script_path} must accept exactly 5 parameters (page, HumanActions, time, sys, request).", file=sys.stdout, flush=True)
                    script_func = None
        else:
            print(f"Script {script_name} not found for domain {domain}", file=sys.stdout, flush=True)
        try:
            TARGET_URL = obj['url']
            print(f"Visiting {TARGET_URL}", file=sys.stdout, flush=True)
            page.goto(TARGET_URL, timeout=10000, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            # Wait for captcha, login, or modal/alert to be resolved before continuing
            wait_for_human_resolution(page)
            if script_func:
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
        except Exception as e:
            print(f"Unhandled error for {obj['url']}: {e}", file=sys.stdout, flush=True)

    def close_all_tabs(self):
        for page in self.tabs.values():
            try:
                page.close()
            except Exception:
                pass
        self.tabs.clear()

    @staticmethod
    def _get_domain(url):
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower()
