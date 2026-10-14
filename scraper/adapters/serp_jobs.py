"""Universal Google Jobs / SERP API Adapter.

CLI-only universal fallback adapter invoked via `--search` flag.
Intentionally excluded from the COMPANIES registry because it requires
external API credits (SerpApi / RapidAPI) and is intended for ad-hoc queries.

Bypasses Cloudflare, Akamai, and login walls by querying Google Jobs
(via SerpApi or RapidAPI JSearch) for any company and role.

Requires SERP_API_KEY or RAPIDAPI_KEY in the environment.
"""
import os
from typing import List

from ..http import request_json
from ..models import Job

SERPAPI_URL = "https://serpapi.com/search.json"
RAPIDAPI_URL = "https://jsearch.p.rapidapi.com/search"


def fetch_serpapi(company: str, query: str = None, api_key: str = None) -> List[Job]:
    """Query Google Jobs via SerpApi engine."""
    key = api_key or os.environ.get("SERP_API_KEY")
    if not key:
        raise ValueError("SERP_API_KEY environment variable is required for SerpApi searches.")

    search_query = query or f"internship software engineer India {company}"
    params = {
        "engine": "google_jobs",
        "q": search_query,
        "hl": "en",
        "gl": "in",
        "api_key": key,
    }

    data = request_json("GET", SERPAPI_URL, params=params)
    results = data.get("jobs_results", [])
    jobs = []

    for r in results:
        job_id = r.get("job_id", "")
        title = r.get("title", "")
        comp = r.get("company_name", company)
        loc = r.get("location", "India")
        # Apply link or Google Jobs share link
        url = r.get("share_link") or (r.get("apply_options", [{}])[0].get("link")) or ""

        # Extensions (e.g. "Internship", "3 days ago")
        ext = r.get("detected_extensions", {})
        is_intern = "intern" in str(ext.get("schedule_type", "")).lower() or "intern" in title.lower()

        jobs.append(Job(
            company=comp,
            external_id=job_id,
            title=title,
            url=url,
            locations=[loc],
            is_intern=is_intern,
        ))

    return jobs


def fetch_rapidapi(company: str, query: str = None, api_key: str = None) -> List[Job]:
    """Query RapidAPI JSearch engine."""
    key = api_key or os.environ.get("RAPIDAPI_KEY")
    if not key:
        raise ValueError("RAPIDAPI_KEY environment variable is required for RapidAPI searches.")

    search_query = query or f"{company} software engineer intern India"
    params = {
        "query": search_query,
        "page": "1",
        "num_pages": "1",
        "country": "IN",
    }
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    data = request_json("GET", RAPIDAPI_URL, params=params, headers=headers)
    results = data.get("data", [])
    jobs = []

    for r in results:
        job_id = r.get("job_id", "")
        title = r.get("job_title", "")
        comp = r.get("employer_name", company)
        city = r.get("job_city", "")
        state = r.get("job_state", "")
        loc = f"{city}, {state}, India" if city else "India"
        url = r.get("job_apply_link") or r.get("job_google_link") or ""

        jobs.append(Job(
            company=comp,
            external_id=job_id,
            title=title,
            url=url,
            locations=[loc],
            is_intern="intern" in str(r.get("job_employment_type", "")).lower() or "intern" in title.lower(),
        ))

    return jobs


def fetch(cfg):
    """Adapter fetch entrypoint."""
    company = cfg["name"]
    query = cfg.get("query")
    if os.environ.get("SERP_API_KEY"):
        return fetch_serpapi(company, query)
    if os.environ.get("RAPIDAPI_KEY"):
        return fetch_rapidapi(company, query)
    raise ValueError(f"{company} requires SERP_API_KEY or RAPIDAPI_KEY in environment to fetch via Google Jobs fallback.")

