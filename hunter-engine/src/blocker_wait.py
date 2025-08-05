# blocker_wait.py
"""
Reusable utility to wait for human intervention if any blocker (captcha, login, modal/overlay) is present.
Call wait_for_human_resolution(page) to pause until all blockers are resolved.
"""
def wait_for_human_resolution(page, check_interval=1):
    """
    Waits until there are no blocking captchas, logins, or overlays on the page.
    Prints progress and only returns when all blockers are resolved.
    """
    import sys
    import time
    def is_blocking_overlay():
        selectors = [
            '[role="dialog"]', '.modal', '.overlay', '.backdrop', '.blocker', '.captcha',
            '[aria-modal="true"]', '[data-overlay]', '[data-blocker]'
        ]
        overlays = []
        for sel in selectors:
            found = page.query_selector_all(sel)
            print(f"[DEBUG] Overlay selector '{sel}' found {len(found)} elements.", file=sys.stdout, flush=True)
            overlays += found
        for overlay in overlays:
            try:
                tag = overlay.evaluate('el => el.tagName')
                outer = overlay.evaluate('el => el.outerHTML.slice(0, 200)')
                print(f"[DEBUG] Overlay candidate: tag={tag}, outerHTML={outer}", file=sys.stdout, flush=True)
                box = overlay.bounding_box()
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
            found = page.query_selector_all(sel)
            print(f"[DEBUG] Login selector '{sel}' found {len(found)} elements.", file=sys.stdout, flush=True)
            login_forms += found
        for form in login_forms:
            try:
                tag = form.evaluate('el => el.tagName')
                outer = form.evaluate('el => el.outerHTML.slice(0, 200)')
                print(f"[DEBUG] Login candidate: tag={tag}, outerHTML={outer}", file=sys.stdout, flush=True)
                box = form.bounding_box()
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
            '#rc-anchor-container', '.rc-anchor', '.recaptcha-checkbox', '#recaptcha-anchor',
            'label#recaptcha-anchor-label', 'label:has-text("I\'m not a robot")',
            'div:has-text("I\'m not a robot")', 'div:has-text("robot")', 'div:has-text("verify")', 'div:has-text("security check")'
        ]
        captchas = []
        for sel in selectors:
            try:
                found = page.query_selector_all(sel)
                print(f"[DEBUG] Captcha selector '{sel}' found {len(found)} elements.", file=sys.stdout, flush=True)
                captchas += found
            except Exception as e:
                print(f"[DEBUG] Exception in captcha selector '{sel}': {e}", file=sys.stdout, flush=True)
        for captcha in captchas:
            try:
                tag = captcha.evaluate('el => el.tagName')
                outer = captcha.evaluate('el => el.outerHTML.slice(0, 200)')
                print(f"[DEBUG] Captcha candidate: tag={tag}, outerHTML={outer}", file=sys.stdout, flush=True)
                box = captcha.bounding_box()
                if box:
                    viewport = page.viewport_size
                    if viewport and box['width'] * box['height'] > 0.3 * viewport['width'] * viewport['height']:
                        return True
            except Exception as e:
                print(f"[DEBUG] Exception in captcha check: {e}", file=sys.stdout, flush=True)
                continue
        return False

    wait_counter = 0
    while True:
        found = False
        if is_blocking_captcha():
            print("[BLOCKER] Blocking captcha detected on page. Waiting for resolution...", file=sys.stdout, flush=True)
            found = True
        if is_blocking_login():
            print("[BLOCKER] Blocking login page detected. Waiting for resolution...", file=sys.stdout, flush=True)
            found = True
        if is_blocking_overlay():
            print("[BLOCKER] Blocking modal/overlay detected. Waiting for resolution...", file=sys.stdout, flush=True)
            found = True
        if not found:
            break
        wait_counter += 1
        print(f"[BLOCKER] Still waiting for human intervention... ({wait_counter} seconds elapsed)", file=sys.stdout, flush=True)
        time.sleep(check_interval)
    if wait_counter > 0:
        print("[BLOCKER] Blocker resolved. Continuing process...", file=sys.stdout, flush=True)
