"""Generate public developer API endpoints and RSS feed into docs/api and docs/.

Endpoints generated:
- docs/api/latest.json : Newly added and reopened internships from the latest sync.
- docs/api/active.json : Clean JSON array of all currently active verified internships.
- docs/feed.xml        : RSS 2.0 syndication feed for bots, webhooks, and RSS readers.
"""
from datetime import datetime, timezone
from email.utils import format_datetime
import html
import json
import os
from typing import Dict, List, Optional

from . import __version__

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
API_DIR = os.path.join(DOCS_DIR, "api")
FEED_PATH = os.path.join(DOCS_DIR, "feed.xml")
LATEST_API_PATH = os.path.join(API_DIR, "latest.json")
ACTIVE_API_PATH = os.path.join(API_DIR, "active.json")

SITE_URL = "https://vishnunandan555.github.io/internscan/"


def _clean_job_for_api(job_dict: dict) -> dict:
    """Format job record into clean, consistent public API shape."""
    return {
        "company": job_dict.get("company", ""),
        "title": job_dict.get("title", ""),
        "url": job_dict.get("url", ""),
        "locations": job_dict.get("locations", []),
        "city_tag": job_dict.get("city_tag") or "India",
        "category": job_dict.get("category") or "Software",
        "posted": job_dict.get("posted"),
        "first_seen": job_dict.get("first_seen"),
        "last_seen": job_dict.get("last_seen"),
    }


def generate_apis(
    state: dict,
    added: Optional[List[dict]] = None,
    reopened: Optional[List[dict]] = None,
) -> dict:
    """Build docs/api/latest.json, docs/api/active.json, and docs/feed.xml."""
    os.makedirs(API_DIR, exist_ok=True)
    updated_at = state.get("updated_at") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_jobs_dict: Dict[str, dict] = state.get("jobs", {})

    # Extract all active jobs sorted by first_seen DESC, then company ASC
    active_jobs = [
        dict(uid=uid, **j)
        for uid, j in all_jobs_dict.items()
        if j.get("active", True)
    ]
    active_jobs.sort(key=lambda x: (x.get("first_seen") or "1970-01-01", x.get("company", "")), reverse=True)

    # 1. Active API endpoint (docs/api/active.json)
    cleaned_active = [_clean_job_for_api(j) for j in active_jobs]
    with open(ACTIVE_API_PATH, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "version": __version__,
                "updated_at": updated_at,
                "total_active": len(cleaned_active),
                "jobs": cleaned_active,
            },
            fh,
            indent=2,
            ensure_ascii=False,
        )
        fh.write("\n")

    # 2. Latest API endpoint (docs/api/latest.json)
    # If run in isolation without diff lists, find jobs discovered today
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_items = added if added is not None else [
        j for j in active_jobs if j.get("first_seen") == today_str
    ]
    reopened_items = reopened if reopened is not None else []

    cleaned_new = [_clean_job_for_api(j) for j in new_items]
    cleaned_reopened = [_clean_job_for_api(j) for j in reopened_items]

    with open(LATEST_API_PATH, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "version": __version__,
                "updated_at": updated_at,
                "new_count": len(cleaned_new),
                "reopened_count": len(cleaned_reopened),
                "total_active": len(cleaned_active),
                "new_jobs": cleaned_new,
                "reopened_jobs": cleaned_reopened,
            },
            fh,
            indent=2,
            ensure_ascii=False,
        )
        fh.write("\n")

    # 3. RSS 2.0 Feed (docs/feed.xml)
    _generate_rss_feed(active_jobs, updated_at)

    return {
        "active_count": len(cleaned_active),
        "new_count": len(cleaned_new),
        "reopened_count": len(cleaned_reopened),
    }


def _generate_rss_feed(active_jobs: List[dict], updated_at: str) -> None:
    """Render standard RSS 2.0 XML for top 40 newest active jobs."""
    now_dt = datetime.now(timezone.utc)
    pub_date_str = format_datetime(now_dt)

    items_xml = []
    # Take the 40 newest active postings for the feed
    for j in active_jobs[:40]:
        title = html.escape(f"[{j.get('company', 'Tech')}] {j.get('title', 'Internship')}")
        link = html.escape(j.get("url", SITE_URL))
        uid = html.escape(str(j.get("uid") or j.get("url", "")))
        cat = html.escape(j.get("category") or "Software")
        loc = html.escape(j.get("city_tag") or ", ".join(j.get("locations", [])) or "India")
        first_seen = j.get("first_seen") or now_dt.strftime("%Y-%m-%d")

        try:
            item_dt = datetime.strptime(first_seen, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            item_pub_date = format_datetime(item_dt)
        except Exception:
            item_pub_date = pub_date_str

        desc = (
            f"&lt;p&gt;&lt;strong&gt;Company:&lt;/strong&gt; {html.escape(j.get('company', ''))}&lt;/p&gt;"
            f"&lt;p&gt;&lt;strong&gt;Location:&lt;/strong&gt; {loc}&lt;/p&gt;"
            f"&lt;p&gt;&lt;strong&gt;Category:&lt;/strong&gt; {cat}&lt;/p&gt;"
            f"&lt;p&gt;&lt;a href=\"{link}\"&gt;Apply directly on official careers portal &amp;rarr;&lt;/a&gt;&lt;/p&gt;"
        )

        items_xml.append(f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="false">{uid}</guid>
      <category>{cat}</category>
      <pubDate>{item_pub_date}</pubDate>
      <description>{desc}</description>
    </item>""")

    feed_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>InternScan India — Tech &amp; Software Internships</title>
    <link>{SITE_URL}</link>
    <description>Live, verified software engineering, AI/ML, data, and systems internships across 59+ tech employers in India.</description>
    <language>en-in</language>
    <lastBuildDate>{pub_date_str}</lastBuildDate>
    <atom:link href="{SITE_URL}feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    with open(FEED_PATH, "w", encoding="utf-8") as fh:
        fh.write(feed_content)
