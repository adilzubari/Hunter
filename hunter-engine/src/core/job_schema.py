from typing import TypedDict, Optional

class JobData(TypedDict, total=False):
    job_id: str
    job_url: str
    title: str
    description: str
    company_name: str
    company_url: str
    company_image_url: str
    company_followers: str
    location: str
    workplace_type: str
    time_posted: str
    is_easy_apply: bool
    redirect_url: str

# List of all job fields for reference
JOB_FIELDS = [
    "job_id", "job_url", "title", "description", "company_name", "company_url", "company_image_url",
    "company_followers", "location", "workplace_type", "time_posted", "is_easy_apply", "redirect_url"
]
