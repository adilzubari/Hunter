# blocker_wait.py
"""
Reusable utility to wait for human intervention if any blocker (captcha, login, modal/overlay) is present.
Call wait_for_human_resolution(page) to pause until all blockers are resolved.
"""
import logging
from logging.handlers import RotatingFileHandler
import os
import threading

_debug_log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../blocker_debug.log'))
_debug_logger = logging.getLogger("blocker_debug")
_LOG_LINE_LIMIT = 10000
_LOG_TRIM = 2000

class LineLimitedFileHandler(logging.FileHandler):
    _lock = threading.Lock()
    def emit(self, record):
        super().emit(record)
        try:
            with self._lock:
                with open(self.baseFilename, 'r+', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > _LOG_LINE_LIMIT:
                        f.seek(0)
                        f.truncate()
                        f.writelines(lines[-(_LOG_LINE_LIMIT - _LOG_TRIM):])
        except Exception:
            pass

if not _debug_logger.handlers:
    handler = LineLimitedFileHandler(_debug_log_file, mode='a', encoding='utf-8')
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _debug_logger.addHandler(handler)
    _debug_logger.setLevel(logging.DEBUG)

def wait_for_human_resolution(page, check_interval=1):
    """Waits until there are no blocking captchas, logins, or overlays on the page. Prints progress and only returns when all blockers are resolved."""
    import sys
    import time
    def get_domain_from_page():
        try:
            url = page.url
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except Exception:
            return "unknown"

    def get_request_info():
        try:
            # Try to get request/task info if attached to page
            if hasattr(page, 'request_info'):
                return str(page.request_info)
        except Exception:
            pass
        return ""

    domain = get_domain_from_page()
    req_info = get_request_info()

    def is_blocking_overlay():
        selectors = [
            '[role="dialog"]', '.modal', '.overlay', '.backdrop', '.blocker', '.captcha',
            '[aria-modal="true"]', '[data-overlay]', '[data-blocker]'
        ]
        overlays = []
        for sel in selectors:
            found = page.query_selector_all(sel)
            overlays += found
        for overlay in overlays:
            try:
                box = overlay.bounding_box()
                if box:
                    viewport = page.viewport_size
                    if viewport and box['width'] * box['height'] > 0.5 * viewport['width'] * viewport['height']:
                        _debug_logger.debug(f"[domain={domain}] [overlay] Blocking overlay detected. {req_info}")
                        return True
            except Exception:
                continue
        return False

    def is_blocking_login():
        selectors = [
            'form[action*="login"]', 'input[type="password"]', '[id*="login"]', '[class*="login"]', '[name*="login"]',
            'form[action*="signin"]', '[id*="signin"]', '[class*="signin"]', '[name*="signin"]'
        ]
        login_forms = []
        for sel in selectors:
            found = page.query_selector_all(sel)
            login_forms += found
        for form in login_forms:
            try:
                box = form.bounding_box()
                if box:
                    viewport = page.viewport_size
                    if viewport and box['width'] * box['height'] > 0.3 * viewport['width'] * viewport['height']:
                        _debug_logger.debug(f"[domain={domain}] [login] Blocking login detected. {req_info}")
                        return True
            except Exception:
                continue
        return False

    def is_blocking_captcha():
        selectors = [
            'iframe[src*="captcha"]', '[id*="captcha"]', '[class*="captcha"]', '[src*="recaptcha"]', '[src*="hcaptcha"]',
            '[id*="recaptcha"]', '[class*="recaptcha"]', '[id*="hcaptcha"]', '[class*="hcaptcha"]',
            '#rc-anchor-container', '.rc-anchor', '.recaptcha-checkbox', '#recaptcha-anchor'
        ]
        captchas = []
        for sel in selectors:
            try:
                found = page.query_selector_all(sel)
                _debug_logger.debug(f"[domain={domain}] [captcha] Captcha selector '{sel}' found {len(found)} elements. {req_info}")
                captchas += found
            except Exception as e:
                _debug_logger.debug(f"[domain={domain}] [captcha] Exception in captcha selector '{sel}': {e} {req_info}")
        for captcha in captchas:
            try:
                tag = captcha.evaluate('el => el.tagName')
                outer = captcha.evaluate('el => el.outerHTML.slice(0, 200)')
                _debug_logger.debug(f"[domain={domain}] [captcha] Captcha candidate: tag={tag}, outerHTML={outer} {req_info}")
                box = captcha.bounding_box()
                if box:
                    viewport = page.viewport_size
                    if viewport and box['width'] * box['height'] > 0.3 * viewport['width'] * viewport['height']:
                        return True
            except Exception as e:
                _debug_logger.debug(f"[domain={domain}] [captcha] Exception in captcha check: {e} {req_info}")
                continue
        return False

    wait_counter = 0
    last_console = 0
    while True:
        found = False
        blocker_msgs = []
        if is_blocking_captcha():
            blocker_msgs.append("[BLOCKER] Blocking captcha detected on page. Waiting for resolution...")
            found = True
        if is_blocking_login():
            blocker_msgs.append("[BLOCKER] Blocking login page detected. Waiting for resolution...")
            found = True
        if is_blocking_overlay():
            blocker_msgs.append("[BLOCKER] Blocking modal/overlay detected. Waiting for resolution...")
            found = True
        if not found:
            break
        wait_counter += 1
        if wait_counter == 1 or wait_counter % 5 == 0:
            for msg in blocker_msgs:
                print(msg, file=sys.stdout, flush=True)
            print(f"[BLOCKER] Still waiting for human intervention... ({wait_counter} seconds elapsed)", file=sys.stdout, flush=True)
        time.sleep(check_interval)
    if wait_counter > 0:
        print("[BLOCKER] Blocker resolved. Continuing process...", file=sys.stdout, flush=True)
