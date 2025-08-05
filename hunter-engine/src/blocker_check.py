"""
Reusable utility to check for captcha, login, or modal/alert popups on a Playwright page.
Prints debug info and returns True if any blocker is present, otherwise False.
"""

def check_page_blockers(page):
    """
    Checks for captcha, login, or modal/alert popups on the page.
    Logs to console if any are found, and waits until resolved before continuing.
    Returns True if any blocker is present, otherwise False.
    """
    import sys
    def is_blocking_overlay():
        selectors = [
            '[role="dialog"]', '.modal', '.overlay', '.backdrop', '.blocker', '.captcha',
            '[aria-modal="true"]', '[data-overlay]', '[data-blocker]'
        ]
        overlays = []
        for sel in selectors:
            overlays += page.query_selector_all(sel)
        print(f"[DEBUG] Found {len(overlays)} overlay candidates.", file=sys.stdout, flush=True)
        for overlay in overlays:
            try:
                box = overlay.bounding_box()
                print(f"[DEBUG] Overlay candidate: selector={overlay._impl_obj._selector if hasattr(overlay, '_impl_obj') else 'unknown'}, box={box}", file=sys.stdout, flush=True)
                if box:
                    viewport = page.viewport_size
                    if viewport and box['width'] * box['height'] > 0.5 * viewport['width'] * viewport['height']:
                        return True
            except Exception as e:
                print(f"[DEBUG] Exception in overlay check: {e}", file=sys.stdout, flush=True)
                continue
        return False

    def is_blocking_login():
        selectors = [
            'form[action*="login"]', 'input[type="password"]', '[id*="login"]', '[class*="login"]', '[name*="login"]',
            'form[action*="signin"]', '[id*="signin"]', '[class*="signin"]', '[name*="signin"]'
        ]
        login_forms = []
        for sel in selectors:
            login_forms += page.query_selector_all(sel)
        print(f"[DEBUG] Found {len(login_forms)} login candidates.", file=sys.stdout, flush=True)
        for form in login_forms:
            try:
                box = form.bounding_box()
                print(f"[DEBUG] Login candidate: selector={form._impl_obj._selector if hasattr(form, '_impl_obj') else 'unknown'}, box={box}", file=sys.stdout, flush=True)
                if box:
                    viewport = page.viewport_size
                    if viewport and box['width'] * box['height'] > 0.3 * viewport['width'] * viewport['height']:
                        return True
            except Exception as e:
                print(f"[DEBUG] Exception in login check: {e}", file=sys.stdout, flush=True)
                continue
        return False

    def is_blocking_captcha():
        selectors = [
            'iframe[src*="captcha"]', '[id*="captcha"]', '[class*="captcha"]', '[src*="recaptcha"]', '[src*="hcaptcha"]',
            '[id*="recaptcha"]', '[class*="recaptcha"]', '[id*="hcaptcha"]', '[class*="hcaptcha"]',
            'div:has-text("I\'m not a robot")', 'div:has-text("robot")', 'div:has-text("verify")', 'div:has-text("security check")'
        ]
        captchas = []
        for sel in selectors:
            try:
                found = page.query_selector_all(sel)
                captchas += found
            except Exception as e:
                print(f"[DEBUG] Exception in captcha selector '{sel}': {e}", file=sys.stdout, flush=True)
        print(f"[DEBUG] Found {len(captchas)} captcha candidates.", file=sys.stdout, flush=True)
        for captcha in captchas:
            try:
                box = captcha.bounding_box()
                print(f"[DEBUG] Captcha candidate: selector={captcha._impl_obj._selector if hasattr(captcha, '_impl_obj') else 'unknown'}, box={box}", file=sys.stdout, flush=True)
                if box:
                    viewport = page.viewport_size
                    if viewport and box['width'] * box['height'] > 0.3 * viewport['width'] * viewport['height']:
                        return True
            except Exception as e:
                print(f"[DEBUG] Exception in captcha check: {e}", file=sys.stdout, flush=True)
                continue
        return False

    found = False
    if is_blocking_captcha():
        print("[BLOCKER] Blocking captcha detected on page.", file=sys.stdout, flush=True)
        found = True
    if is_blocking_login():
        print("[BLOCKER] Blocking login page detected.", file=sys.stdout, flush=True)
        found = True
    if is_blocking_overlay():
        print("[BLOCKER] Blocking modal/overlay detected.", file=sys.stdout, flush=True)
        found = True
    return found
