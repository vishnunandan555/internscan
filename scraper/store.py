"""Load/save data/jobs.json and diff new scrape results against it.

jobs.json layout:
{
  "updated_at": "2026-07-09T12:00:00Z",
  "jobs": {
    "<uid>": {
      "company": ..., "external_id": ..., "title": ..., "url": ..., "locations": [...],
      "first_seen": "2026-07-09", "last_seen": "2026-07-09", "active": true
    }
  }
}

Jobs are never deleted; when a posting disappears from a successful scrape it is
flagged active=false (so first_seen survives a posting flapping on/off).
If a company's scraper FAILED this run, its existing jobs are left untouched.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

from .regions import classify_location
from .countries import SUPPORTED_COUNTRIES

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DATA_PATH = os.path.join(DATA_DIR, "jobs.json")
_TMP_PATH = DATA_PATH + ".tmp"


def _slugify(name: str) -> str:
    """Normalize company name to kebab-case slug matching Job.uid conventions."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load(country: Optional[str] = None) -> dict:
    """Load jobs database. If country is provided, loads from data/<country>/jobs.json if available.
    Backfills country and region on legacy records if absent."""
    path = DATA_PATH
    if country and country in SUPPORTED_COUNTRIES:
        country_path = os.path.join(DATA_DIR, country, "jobs.json")
        if os.path.exists(country_path):
            path = country_path

    if not os.path.exists(path):
        return {"updated_at": None, "jobs": {}}
    try:
        with open(path, encoding="utf-8") as fh:
            state = json.load(fh)
        if not isinstance(state, dict) or not isinstance(state.get("jobs"), dict):
            raise ValueError("Root state or 'jobs' key is not a dict")
        # Backfill country and region if missing
        for uid, entry in state["jobs"].items():
            if not entry.get("country") or not entry.get("region"):
                c, r, h = classify_location(entry.get("locations", []))
                entry["country"] = entry.get("country") or c
                entry["region"] = entry.get("region") or r
                if not entry.get("city_tag"):
                    entry["city_tag"] = h
        return state
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        print(f"[WARN] jobs.json corrupt ({exc}); starting fresh.", file=sys.stderr)
        corrupt_path = f"{path}.corrupt.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        try:
            os.replace(path, corrupt_path)
            print(f"[INFO] Backup saved to {corrupt_path}", file=sys.stderr)
        except OSError:
            pass
        return {"updated_at": None, "jobs": {}}


def save(state: dict) -> None:
    """Atomically persist master state to data/jobs.json and partitioned slices to data/<country>/jobs.json."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["updated_at"] = now_iso
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Master state
    with open(_TMP_PATH, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(_TMP_PATH, DATA_PATH)  # atomic on POSIX

    # 2. Country partitions (e.g. data/in/jobs.json, data/us/jobs.json)
    jobs_dict = state.get("jobs", {})
    data_dir = os.path.dirname(DATA_PATH)
    for country_code in SUPPORTED_COUNTRIES:
        c_dir = os.path.join(data_dir, country_code)
        os.makedirs(c_dir, exist_ok=True)
        c_jobs = {
            uid: entry for uid, entry in jobs_dict.items()
            if entry.get("country") == country_code
        }
        c_state = {
            "updated_at": now_iso,
            "jobs": c_jobs,
        }
        c_tmp = os.path.join(c_dir, "jobs.json.tmp")
        c_final = os.path.join(c_dir, "jobs.json")
        with open(c_tmp, "w", encoding="utf-8") as fh:
            json.dump(c_state, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(c_tmp, c_final)


def merge(state: dict, scraped_jobs: list, succeeded_companies: set) -> tuple:
    """Merge scraped Job objects into state.

    scraped_jobs: list[Job] from every company whose fetch SUCCEEDED.
    succeeded_companies: set of company display names that fetched without error.
    Returns (added, closed, reopened) lists of job dicts for reporting.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    jobs = state["jobs"]
    seen_uids: set = set()
    added, closed, reopened = [], [], []

    # Build slug set from succeeded company display names and jobs scraped this run.
    succeeded_slugs = {_slugify(n) for n in succeeded_companies}
    scraped_slugs = {job.uid.split(":", 1)[0] for job in scraped_jobs}

    for job in scraped_jobs:
        uid = job.uid
        seen_uids.add(uid)
        if uid in jobs:
            entry = jobs[uid]
            if not entry.get("active", True):
                entry["active"] = True
                reopened.append(entry)
            # Workday's relative "30+ Days Ago" degrades to posted=None once a
            # posting ages past 30 days — keep the date we captured earlier.
            known_posted = entry.get("posted")
            entry.update(job.to_dict())
            if not entry.get("posted") and known_posted:
                entry["posted"] = known_posted
            entry["last_seen"] = today
        else:
            entry = job.to_dict()
            entry["first_seen"] = today
            entry["last_seen"] = today
            entry["active"] = True
            jobs[uid] = entry
            added.append(entry)

    def _matches_succeeded(uid_slug: str, entry_company: str) -> bool:
        if entry_company in succeeded_companies:
            return True
        if uid_slug in scraped_slugs:
            return True
        entry_slug = _slugify(entry_company)
        for s_slug in succeeded_slugs:
            if uid_slug == s_slug or entry_slug == s_slug:
                return True
            # Handle rename variations with word boundaries (e.g. google vs google-llc)
            if s_slug.startswith(uid_slug + "-") or uid_slug.startswith(s_slug + "-"):
                return True
            if entry_slug and (s_slug.startswith(entry_slug + "-") or entry_slug.startswith(s_slug + "-")):
                return True
        return False

    # Close jobs only for companies that scraped successfully this run
    for uid, entry in list(jobs.items()):
        if uid in seen_uids or not entry.get("active", True):
            continue
        uid_slug = uid.split(":", 1)[0]
        entry_company = entry.get("company", "")

        if _matches_succeeded(uid_slug, entry_company):
            entry["active"] = False
            entry["closed"] = today
            closed.append(entry)

    return added, closed, reopened

