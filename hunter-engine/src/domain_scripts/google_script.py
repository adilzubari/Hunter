from src.navigation_utils import safe_click, safe_press
from src.blocker_wait import wait_for_human_resolution

def google_script(page, HumanActions, time, sys, request):
    print("Performing Google search interaction...", file=sys.stdout, flush=True)
    search_query = "Indian news"
    print(f"Typing search query: {search_query}", file=sys.stdout, flush=True)
    search_box_selector = "textarea:visible"
    time.sleep(1)
    HumanActions.mouse_move(page, search_box_selector)
    safe_click(page, search_box_selector, delay=200)
    time.sleep(0.7)
    HumanActions.typing(search_query, page)
    try:
        with page.expect_navigation(timeout=10000):
            safe_press(page, "Enter")
    except Exception as e:
        print(f"[google_script] No navigation detected after Enter: {e}", file=sys.stdout, flush=True)
    # After navigation, wait for any captcha/login/modal to be resolved by human
    wait_for_human_resolution(page)
    print("Extracting search result links...", file=sys.stdout, flush=True)
    search_result_selector = "#search a"
    print(f"Using selector: {search_result_selector}", file=sys.stdout, flush=True)
    links = page.locator(search_result_selector).all()
    print("Google search result links inside #center-col[role='main']:", file=sys.stdout, flush=True)
    for link in links:
        print(link.get_attribute("href"), file=sys.stdout, flush=True)
