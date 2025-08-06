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
        # Use orchestrator middleware for standardized script execution and URL selection
        from src.core import orchestrator
        import importlib
        domain = self._get_domain(obj['url'])
        if domain not in self.tabs:
            self.tabs[domain] = self.context.new_page()
        page = self.tabs[domain]
        # Dynamically load all available domain scripts
        script_funcs = {}
        scripts_dir = os.path.join(os.path.dirname(__file__), "domain_scripts")
        for fname in os.listdir(scripts_dir):
            if fname.endswith("_script.py"):
                script_name = fname[:-3]
                script_path = os.path.join(scripts_dir, fname)
                spec = importlib.util.spec_from_file_location(script_name, script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                func = getattr(module, script_name, None)
                if func:
                    script_funcs[script_name] = func
        try:
            orchestrator.orchestrate(page, HumanActions, time, sys, obj, script_funcs)
            # Optionally persist page info
            script_name, persist = self.get_script_and_persist(domain)
            if persist:
                self.persisted_pages.append({
                    "url": obj['url'],
                    "domain": domain,
                    "timestamp": time.time()
                })
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
