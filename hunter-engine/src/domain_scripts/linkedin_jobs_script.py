def linkedin_jobs_script(page, HumanActions, time, sys, request):
    print("LinkedIn Jobs Script loaded.", file=sys.stdout, flush=True)
    search_params = request.get("search_params", {})
    search_query = search_params.get("query", "")
    location = search_params.get("location")
    workplace_type = search_params.get("workplace_type")  # remote, onsite, hybrid
    time_posted = search_params.get("time_posted")  # past_24_hours, past_week, past_month

    # Compose URL for jobs with location, workplace type, and time posted if provided
    base_url = "https://www.linkedin.com"
    from urllib.parse import quote_plus
    section_url = f"{base_url}/jobs/search/?keywords={quote_plus(search_query)}"
    if location:
        section_url += f"&location={quote_plus(location)}"
    # LinkedIn uses 'f_WT' param for workplace type: 1=On-site, 2=Remote, 3=Hybrid
    wt_map = {"onsite": "1", "remote": "2", "hybrid": "3"}
    if workplace_type in wt_map:
        section_url += f"&f_WT={wt_map[workplace_type]}"
    # LinkedIn uses 'f_TPR' param for time posted: r86400=24h, r604800=week, r2592000=month
    tpr_map = {"past_24_hours": "r86400", "past_week": "r604800", "past_month": "r2592000"}
    if time_posted in tpr_map:
        section_url += f"&f_TPR={tpr_map[time_posted]}"
    print(f"Navigating to LinkedIn jobs section: {section_url}", file=sys.stdout, flush=True)
    try:
        page.goto(section_url, timeout=10000, wait_until="domcontentloaded")
        from src.blocker_wait import wait_for_human_resolution
        wait_for_human_resolution(page)
        # UI fallback for location, workplace type, and time posted if not reflected in the page
        import re
        current_url = page.url if hasattr(page, 'url') else None
        location_set = False
        # if current_url and location:
        #     encoded_loc = quote_plus(location)
        #     if re.search(r"[?&]location=(" + re.escape(encoded_loc) + r"|" + re.escape(location) + r")", current_url):
        #         location_set = True
        # if search_query:
        #     try:
        #         job_box_selector = "input[aria-label='Search by title, skill, or company']"
        #         HumanActions.mouse_move(page, job_box_selector)
        #         page.click(job_box_selector)
        #         time.sleep(0.7)
        #         HumanActions.typing(search_query, page)
        #     except Exception:
        #         pass
        # if location and not location_set:
        #     try:
        #         location_box_selector = "input[aria-label='City, state, or zip code']"
        #         HumanActions.mouse_move(page, location_box_selector)
        #         page.click(location_box_selector)
        #         time.sleep(0.7)
        #         page.fill(location_box_selector, "")
        #         HumanActions.typing(location, page)
        #     except Exception:
        #         pass
        # # UI interaction for workplace type and time posted if not reflected in URL (selectors may need adjustment)
        # if workplace_type:
        #     try:
        #         filter_button_selector = "button[aria-label='Workplace type filter. Clicking this button displays all Workplace type filter options.']"
        #         HumanActions.mouse_move(page, filter_button_selector)
        #         page.click(filter_button_selector)
        #         time.sleep(0.5)
        #         option_selector = f"input[name='workplaceTypeFilter'][value='{wt_map.get(workplace_type, '')}']"
        #         page.check(option_selector)
        #         time.sleep(0.5)
        #     except Exception:
        #         pass
        # if time_posted:
        #     try:
        #         filter_button_selector = "button[aria-label='Date posted filter. Clicking this button displays all Date posted filter options.']"
        #         HumanActions.mouse_move(page, filter_button_selector)
        #         page.click(filter_button_selector)
        #         time.sleep(0.5)
        #         option_selector = f"input[name='timePostedRange'][value='{tpr_map.get(time_posted, '')}']"
        #         page.check(option_selector)
        #         time.sleep(0.5)
        #     except Exception:
        #         pass
        try:
            page.keyboard.press("Enter")
            # page.wait_for_load_state("networkidle")
            wait_for_human_resolution(page)
        except Exception:
            pass
        print("Extracting jobs...", file=sys.stdout, flush=True)
        from src.domain_scripts.linkedin_jobs_extractor import extract_linkedin_jobs
        extract_linkedin_jobs(page, HumanActions)
    except Exception as e:
        print(f"Error navigating LinkedIn jobs section: {e}", file=sys.stdout, flush=True)
