"""Workday CXS job search.

POST https://{tenant}.wd{n}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
body: {"appliedFacets": {...}, "limit": 20, "offset": N, "searchText": "..."}
Job URL: https://{host}/en-US/{site}{externalPath}

Gotcha (observed on nvidia/intel): under rapid sequential POSTs Workday
rate-limits by silently returning {"total": 0, "jobPostings": []} with HTTP
200. Treating that as truth would make the store close every listing for the
company, so empty pages are retried and a still-empty first page raises.
"""
import random
import re
import time
from datetime import datetime, timedelta, timezone

from ..http import request_json
from ..models import Job

POSTED_RE = re.compile(r"Posted (Today|Yesterday|(\d+)(\+?) Days? Ago)", re.IGNORECASE)


def _posted_date(posted_on):
    """Workday only gives relative text ("Posted 14 Days Ago", "Posted 30+ Days Ago").
    Map relative days to YYYY-MM-DD so older listings do not falsely fall back to today's crawl date."""
    m = POSTED_RE.search(posted_on or "")
    if not m:
        return None
    word, days, plus = m.group(1), m.group(2), m.group(3)
    if word.lower() == "today":
        delta = 0
    elif word.lower() == "yesterday":
        delta = 1
    else:
        delta = int(days)
    return (datetime.now(timezone.utc) - timedelta(days=delta)).strftime("%Y-%m-%d")

PAGE = 20  # CXS hard limit per request
DEFAULT_MAX_PAGES = 15
EMPTY_RETRIES = 4


def _page(api, facets, search_text, offset):
    body = {"appliedFacets": facets, "limit": PAGE, "offset": offset,
            "searchText": search_text}
    for attempt in range(EMPTY_RETRIES):
        data = request_json("POST", api, json_body=body,
                            headers={"Content-Type": "application/json"})
        if data.get("jobPostings") or data.get("total", 0) > 0:
            return data
        delay = min(8 * (attempt + 1), 20) * random.uniform(0.8, 1.2)
        time.sleep(delay)  # likely the silent rate-limit response; apply jitter
    return data


def fetch(cfg):
    host = cfg["host"]  # e.g. "nvidia.wd5.myworkdayjobs.com"
    tenant = cfg.get("tenant") or host.split(".")[0]
    site = cfg["site"]
    api = "https://{}/wday/cxs/{}/{}/jobs".format(host, tenant, site)
    search_text = cfg.get("search_text", "intern")
    facets = cfg.get("applied_facets", {})
    max_pages = cfg.get("max_pages", DEFAULT_MAX_PAGES)

    jobs, offset, total = [], 0, None
    for page_no in range(max_pages):
        data = _page(api, facets, search_text, offset)
        postings = data.get("jobPostings", [])
        if total is None:
            # Workday only reports the real total on the first page; later
            # pages say total=0 while still returning postings.
            total = data.get("total", 0)
        if page_no == 0 and not postings:
            # A fuzzy "intern" search returning nothing is almost certainly the
            # rate limiter; fail the company rather than wipe its listings.
            raise RuntimeError("workday returned empty first page for {}".format(cfg["name"]))
        for p in postings:
            path = p.get("externalPath", "")
            bullet = p.get("bulletFields") or []
            loc_raw = p.get("locationsText", "")
            locs = [loc_raw] if loc_raw else []
            if path:
                parts = path.strip("/").split("/")
                if len(parts) >= 2 and parts[0] == "job":
                    slug_loc = parts[1].replace("---", ", ").replace("-", " ")
                    if slug_loc and slug_loc not in locs:
                        locs.append(slug_loc)
            jobs.append(Job(
                company=cfg["name"],
                external_id=str(bullet[0]) if bullet else path,
                title=p.get("title", ""),
                url="https://{}/en-US/{}{}".format(host, site, path),
                locations=locs,
                posted=_posted_date(p.get("postedOn")),
            ))
        offset += PAGE
        if offset >= total or not postings or page_no == max_pages - 1:
            break
        time.sleep(0.8)
    return jobs
