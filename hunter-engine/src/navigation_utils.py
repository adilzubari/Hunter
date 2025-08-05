from src.blocker_wait import wait_for_human_resolution

def safe_goto(page, url, **kwargs):
    try:
        page.goto(url, **kwargs)
        page.wait_for_load_state("networkidle")
        page.wait_for_load_state("domcontentloaded")
        wait_for_human_resolution(page)
    except Exception as e:
        import traceback
        print(f"[safe_goto] Error during navigation to {url}: {e}")
        traceback.print_exc()

def safe_click(page, selector, **kwargs):
    try:
        page.click(selector, **kwargs)
        page.wait_for_load_state("networkidle")
        page.wait_for_load_state("domcontentloaded")
        wait_for_human_resolution(page)
    except Exception as e:
        import traceback
        print(f"[safe_click] Error during click on {selector}: {e}")
        traceback.print_exc()

def safe_press(page, key, **kwargs):
    try:
        page.keyboard.press(key, **kwargs)
        page.wait_for_load_state("networkidle")
        page.wait_for_load_state("domcontentloaded")
        wait_for_human_resolution(page)
    except Exception as e:
        import traceback
        print(f"[safe_press] Error during key press {key}: {e}")
        traceback.print_exc()

def check_blockers_after_delay(page, delay=2):
    import time
    time.sleep(delay)
    try:
        page.wait_for_load_state("networkidle")
        page.wait_for_load_state("domcontentloaded")
        wait_for_human_resolution(page)
    except Exception as e:
        import traceback
        print(f"[check_blockers_after_delay] Error after delay: {e}")
        traceback.print_exc()
