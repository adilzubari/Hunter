def linkedin_script(page, HumanActions, time, sys, request):
    print("LinkedIn page loaded.", file=sys.stdout, flush=True)
    search_type = request.get("search_type", "jobs")
    search_params = request.get("search_params", {})
    search_query = search_params.get("query", "")
    location = search_params.get("location")
    workplace_type = search_params.get("workplace_type")  # remote, onsite, hybrid
    time_posted = search_params.get("time_posted")  # past_24_hours, past_week, past_month

    # Compose URL for jobs with location, workplace type, and time posted if provided
    base_url = "https://www.linkedin.com"
    from urllib.parse import quote_plus
    if search_type == "jobs":
        section_url = f"{base_url}/jobs/search/?keywords={quote_plus(search_query)}"
        if location:
            section_url += f"&location={quote_plus(location)}"
        # LinkedIn uses 'f_WT' param for workplace type: 1=On-site, 2=Remote, 3=Hybrid
        wt_map = {"onsite": "1", "remote": "2", "hybrid": "3"}
        if workplace_type in wt_map:
            section_url += f"&f_WT={wt_map[workplace_type]}"
        # LinkedIn uses 'f_TP' param for time posted: 1=24h, 2=week, 3=month
        tp_map = {"past_24_hours": "1", "past_week": "2", "past_month": "3"}
        if time_posted in tp_map:
            section_url += f"&f_TP={tp_map[time_posted]}"
    elif search_type == "companies":
        section_url = f"{base_url}/search/results/companies/?keywords={quote_plus(search_query)}"
    elif search_type == "posts":
        section_url = f"{base_url}/search/results/content/?keywords={quote_plus(search_query)}"
    else:
        section_url = base_url
    print(f"Navigating to LinkedIn {search_type} section: {section_url}", file=sys.stdout, flush=True)
    try:
        page.goto(section_url, timeout=10000, wait_until="domcontentloaded")
        from src.blocker_wait import wait_for_human_resolution
        wait_for_human_resolution(page)
        # For jobs, ensure location, workplace type, and time posted are set via UI if not reflected in the page
        if search_type == "jobs":
            import re
            current_url = page.url if hasattr(page, 'url') else None
            location_set = False
            if current_url and location:
                encoded_loc = quote_plus(location)
                if re.search(r"[?&]location=(" + re.escape(encoded_loc) + r"|" + re.escape(location) + r")", current_url):
                    location_set = True
            if search_query:
                try:
                    job_box_selector = "input[aria-label='Search by title, skill, or company']"
                    HumanActions.mouse_move(page, job_box_selector)
                    page.click(job_box_selector)
                    time.sleep(0.7)
                    HumanActions.typing(search_query, page)
                except Exception:
                    pass
            if location and not location_set:
                try:
                    location_box_selector = "input[aria-label='City, state, or zip code']"
                    HumanActions.mouse_move(page, location_box_selector)
                    page.click(location_box_selector)
                    time.sleep(0.7)
                    page.fill(location_box_selector, "")
                    HumanActions.typing(location, page)
                except Exception:
                    pass
            # UI interaction for workplace type and time posted if not reflected in URL (selectors may need adjustment)
            if workplace_type:
                try:
                    # Example: Click workplace type filter button and select option
                    filter_button_selector = "button[aria-label='Workplace type filter. Clicking this button displays all Workplace type filter options.']"
                    HumanActions.mouse_move(page, filter_button_selector)
                    page.click(filter_button_selector)
                    time.sleep(0.5)
                    option_selector = f"input[name='workplaceTypeFilter'][value='{wt_map.get(workplace_type, '')}']"
                    page.check(option_selector)
                    time.sleep(0.5)
                except Exception:
                    pass
            if time_posted:
                try:
                    # Example: Click time posted filter button and select option
                    filter_button_selector = "button[aria-label='Date posted filter. Clicking this button displays all Date posted filter options.']"
                    HumanActions.mouse_move(page, filter_button_selector)
                    page.click(filter_button_selector)
                    time.sleep(0.5)
                    option_selector = f"input[name='timePostedRange'][value='{tp_map.get(time_posted, '')}']"
                    page.check(option_selector)
                    time.sleep(0.5)
                except Exception:
                    pass
            try:
                page.keyboard.press("Enter")
                page.wait_for_load_state("networkidle")
                wait_for_human_resolution(page)
            except Exception:
                pass
        # Section-specific extraction logic can go here
        if search_type == "jobs":
            print("Extracting jobs...", file=sys.stdout, flush=True)
        elif search_type == "companies":
            print("Extracting companies...", file=sys.stdout, flush=True)
        elif search_type == "posts":
            print("Extracting posts...", file=sys.stdout, flush=True)
        else:
            print("Unknown search_type, loaded homepage.", file=sys.stdout, flush=True)
    except Exception as e:
        print(f"Error navigating LinkedIn section: {e}", file=sys.stdout, flush=True)
