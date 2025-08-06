
import sys
import time
import json
from src.core.job_schema import JobData, JOB_FIELDS

def extract_linkedin_jobs(page, HumanActions, output_file="linkedin_jobs_output.json"):
    print("[Extractor] Starting job extraction...", file=sys.stdout, flush=True)
    # Use a more robust selector for job cards (fallback to li with job-card-container class)
    job_selector = 'ul.jobs-search__results-list li.job-card-container, ul.jobs-search__results-list li'
    # Wait up to 60 seconds for jobs list to appear, checking every 2 seconds
    max_wait = 60
    interval = 2
    waited = 0
    jobs_list_found = False
    while waited < max_wait:
        try:
            page.wait_for_selector(job_selector, timeout=interval * 1000)
            jobs_list_found = True
            break
        except Exception:
            time.sleep(interval)
            waited += interval
    if not jobs_list_found:
        print(f"[Extractor] Jobs list did not appear after {max_wait} seconds.", file=sys.stdout, flush=True)
        return

    # Scroll to load all jobs (simulate user scrolling)
    jobs_loaded = set()
    scroll_attempts = 0
    max_scrolls = 10
    while scroll_attempts < max_scrolls:
        jobs = page.query_selector_all(job_selector)
        # Use job link href or job title as a unique identifier fallback
        new_ids = set()
        for job in jobs:
            link = job.query_selector('a.job-card-list__title, a')
            if link:
                href = link.get_attribute('href')
                if href:
                    new_ids.add(href)
        if new_ids.issubset(jobs_loaded):
            break
        jobs_loaded.update(new_ids)
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(1)
        scroll_attempts += 1
    print(f"[Extractor] Total jobs found after scrolling: {len(jobs_loaded)}", file=sys.stdout, flush=True)

    # Re-query jobs after scrolling
    jobs = page.query_selector_all(job_selector)
    seen_job_ids = set()
    results = []


    for idx, job in enumerate(jobs):
        try:
            link = job.query_selector('a.job-card-list__title, a')
            job_id = link.get_attribute('href') if link else None
            if not job_id or job_id in seen_job_ids:
                continue
            seen_job_ids.add(job_id)
            # Click anywhere on the screen to make it active, then send Escape key (to close any modal)
            try:
                page.click('body')
                time.sleep(0.2)
            except Exception:
                pass
            try:
                page.keyboard.press('Escape')
                time.sleep(0.3)
            except Exception:
                pass
            job.click()
            time.sleep(1.5)
            # Expand job description if 'see more' is present
            see_more_btn = page.query_selector('button[aria-label="See more, Job description"], button.show-more-less-html__button')
            if see_more_btn:
                try:
                    see_more_btn.click()
                    time.sleep(0.5)
                except Exception:
                    pass
            # Extract job details
            job_url = page.url
            title_el = page.query_selector('h2.topcard__title')
            desc_el = page.query_selector('div.description__text, div.show-more-less-html__markup')
            company_el = page.query_selector('a.topcard__org-name-link, span.topcard__flavor')
            company_url_el = page.query_selector('a.topcard__org-name-link')
            company_img_el = page.query_selector('img.topcard__org-logo-image')
            followers_el = page.query_selector('span.topcard__flavor--metadata')
            easy_apply_btn = page.query_selector('button.jobs-apply-button')
            redirect_btn = page.query_selector('a.topcard__apply-button')

            title = title_el.inner_text().strip() if title_el else ''
            description = desc_el.inner_text().strip() if desc_el else ''
            company_name = company_el.inner_text().strip() if company_el else ''
            company_url = company_url_el.get_attribute('href') if company_url_el else ''
            company_image_url = company_img_el.get_attribute('src') if company_img_el else ''
            company_followers = followers_el.inner_text().strip() if followers_el else ''
            is_easy_apply = bool(easy_apply_btn)
            redirect_url = redirect_btn.get_attribute('href') if redirect_btn else ''

            # Try to extract location and workplace type from visible elements
            location_el = page.query_selector('span.topcard__flavor--bullet')
            location = location_el.inner_text().strip() if location_el else ''
            workplace_type_el = page.query_selector('span.topcard__flavor--workplace-type')
            workplace_type = workplace_type_el.inner_text().strip() if workplace_type_el else ''
            # Time posted
            time_posted_el = page.query_selector('span.posted-time-ago__text')
            time_posted = time_posted_el.inner_text().strip() if time_posted_el else ''

            job_data = {
                "job_id": job_id,
                "job_url": job_url,
                "title": title,
                "description": description,
                "company_name": company_name,
                "company_url": company_url,
                "company_image_url": company_image_url,
                "company_followers": company_followers,
                "location": location,
                "workplace_type": workplace_type,
                "time_posted": time_posted,
                "is_easy_apply": is_easy_apply,
                "redirect_url": redirect_url
            }
            results.append(job_data)
            print(f"[Extractor] Fetched job {idx+1}: {title}", file=sys.stdout, flush=True)
        except Exception as e:
            print(f"[Extractor] Error fetching job {idx+1}: {e}", file=sys.stdout, flush=True)

    # Retry if 0 jobs found
    if not results:
        print("[Extractor] No jobs extracted, retrying after 3 seconds...", file=sys.stdout, flush=True)
        time.sleep(3)
        jobs = page.query_selector_all(job_selector)
        for idx, job in enumerate(jobs):
            try:
                job_id = job.get_attribute('data-occludable-job-id')
                if not job_id or job_id in seen_job_ids:
                    continue
                seen_job_ids.add(job_id)
                job.click()
                time.sleep(3)
                # Extract job details (same as above)
                job_url = page.url
                title_el = page.query_selector('h2.topcard__title')
                desc_el = page.query_selector('div.description__text, div.show-more-less-html__markup')
                company_el = page.query_selector('a.topcard__org-name-link, span.topcard__flavor')
                company_url_el = page.query_selector('a.topcard__org-name-link')
                company_img_el = page.query_selector('img.topcard__org-logo-image')
                followers_el = page.query_selector('span.topcard__flavor--metadata')
                easy_apply_btn = page.query_selector('button.jobs-apply-button')
                redirect_btn = page.query_selector('a.topcard__apply-button')

                title = title_el.inner_text().strip() if title_el else ''
                description = desc_el.inner_text().strip() if desc_el else ''
                company_name = company_el.inner_text().strip() if company_el else ''
                company_url = company_url_el.get_attribute('href') if company_url_el else ''
                company_image_url = company_img_el.get_attribute('src') if company_img_el else ''
                company_followers = followers_el.inner_text().strip() if followers_el else ''
                is_easy_apply = bool(easy_apply_btn)
                redirect_url = redirect_btn.get_attribute('href') if redirect_btn else ''

                location_el = page.query_selector('span.topcard__flavor--bullet')
                location = location_el.inner_text().strip() if location_el else ''
                workplace_type_el = page.query_selector('span.topcard__flavor--workplace-type')
                workplace_type = workplace_type_el.inner_text().strip() if workplace_type_el else ''
                time_posted_el = page.query_selector('span.posted-time-ago__text')
                time_posted = time_posted_el.inner_text().strip() if time_posted_el else ''

                job_data = {
                    "job_id": job_id,
                    "job_url": job_url,
                    "title": title,
                    "description": description,
                    "company_name": company_name,
                    "company_url": company_url,
                    "company_image_url": company_image_url,
                    "company_followers": company_followers,
                    "location": location,
                    "workplace_type": workplace_type,
                    "time_posted": time_posted,
                    "is_easy_apply": is_easy_apply,
                    "redirect_url": redirect_url
                }
                results.append(job_data)
                print(f"[Extractor] Fetched job (retry) {idx+1}: {title}", file=sys.stdout, flush=True)
            except Exception as e:
                print(f"[Extractor] Error fetching job (retry) {idx+1}: {e}", file=sys.stdout, flush=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[Extractor] Extraction complete. {len(results)} unique jobs written to {output_file}", file=sys.stdout, flush=True)
    # Wait 5 seconds before moving to a blank page
    time.sleep(5)
    try:
        page.goto('about:blank')
    except Exception:
        pass
