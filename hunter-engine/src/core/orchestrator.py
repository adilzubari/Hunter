# Global Script Orchestrator Middleware for Domain Scripts
# This module standardizes base URL and script selection for each domain/section.

import sys
from urllib.parse import urlparse

# Example registry for base URLs and section URLs per domain
DOMAIN_REGISTRY = {
    "www.linkedin.com": {
        "base_url": "https://www.linkedin.com",
        "sections": {
            "jobs": "/jobs/search/?keywords={query}",
            "companies": "/search/results/companies/?keywords={query}",
            "posts": "/search/results/content/?keywords={query}",
        },
        "scripts": {
            "jobs": "linkedin_jobs_script",
            "posts": "linkedin_posts_script",
            "companies": "linkedin_companies_script"
        },
        "script": "linkedin_script"  # fallback
    },
    # Add more domains as needed
}

def get_domain(url):
    return urlparse(url).netloc.lower()

def get_base_url(domain):
    return DOMAIN_REGISTRY.get(domain, {}).get("base_url", f"https://{domain}")

def get_section_url(domain, section, query):
    section_fmt = DOMAIN_REGISTRY.get(domain, {}).get("sections", {}).get(section)
    if section_fmt:
        return f"{get_base_url(domain)}{section_fmt.format(query=query)}"
    return get_base_url(domain)


def get_script_for_domain(domain, section=None):
    reg = DOMAIN_REGISTRY.get(domain, {})
    if section and "scripts" in reg and section in reg["scripts"]:
        return reg["scripts"][section]
    return reg.get("script", "default_script")

# Middleware to orchestrate script execution
# Usage: orchestrate(page, HumanActions, time, sys, request)
def orchestrate(page, HumanActions, time, sys, request, script_funcs):
    domain = get_domain(request["url"])
    search_type = request.get("search_type", "jobs")
    search_params = request.get("search_params", {})
    search_query = search_params.get("query", "")
    section_url = get_section_url(domain, search_type, search_query)
    # Only log high-level navigation and errors
    try:
        print(f"[Orchestrator] Navigating to {section_url}", file=sys.stdout, flush=True)
        page.goto(section_url, timeout=10000, wait_until="domcontentloaded")
        # page.wait_for_load_state("networkidle")
        from src.blocker_wait import wait_for_human_resolution
        wait_for_human_resolution(page)
        script_name = get_script_for_domain(domain, search_type)
        script_func = script_funcs.get(script_name)
        if script_func:
            script_func(page, HumanActions, time, sys, request)
        else:
            print(f"[Orchestrator] No script found for {domain} section {search_type}", file=sys.stdout, flush=True)
    except Exception as e:
        print(f"[Orchestrator] Error: {e}", file=sys.stdout, flush=True)
