"""Generate public developer API endpoints, RSS feed, and country partitions.

Endpoints generated:
- Global:
  - docs/api/latest.json : Newly added/reopened internships globally.
  - docs/api/active.json : All active verified internships globally.
  - docs/feed.xml        : Global RSS 2.0 feed.
  - docs/metrics.json    : Live platform metrics per country for the homepage.
- Country Partitions:
  - docs/<country>/jobs.json       : Direct active jobs JSON for client web app.
  - docs/<country>/api/active.json : Country active internships REST endpoint.
  - docs/<country>/api/latest.json : Country latest internships REST endpoint.
  - docs/<country>/feed.xml        : Country RSS 2.0 feed.
"""
from datetime import datetime, timezone
from email.utils import format_datetime
import html
import json
import os
from typing import Dict, List, Optional

from . import __version__
from .countries import COUNTRY_METADATA, SUPPORTED_COUNTRIES, get_companies_for_country

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
API_DIR = os.path.join(DOCS_DIR, "api")
FEED_PATH = os.path.join(DOCS_DIR, "feed.xml")
LATEST_API_PATH = os.path.join(API_DIR, "latest.json")
ACTIVE_API_PATH = os.path.join(API_DIR, "active.json")
METRICS_PATH = os.path.join(DOCS_DIR, "metrics.json")

SITE_URL = "https://vishnunandan555.github.io/internscan/"


def _clean_job_for_api(job_dict: dict) -> dict:
    """Format job record into clean, consistent public API shape."""
    return {
        "company": job_dict.get("company", ""),
        "title": job_dict.get("title", ""),
        "url": job_dict.get("url", ""),
        "locations": job_dict.get("locations", []),
        "city_tag": job_dict.get("city_tag") or "India",
        "country": job_dict.get("country") or "in",
        "region": job_dict.get("region") or "APAC",
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
    """Build global and country-partitioned API endpoints, metrics, and RSS feeds."""
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

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_items = added if added is not None else [
        j for j in active_jobs if j.get("first_seen") == today_str
    ]
    reopened_items = reopened if reopened is not None else []

    cleaned_active = [_clean_job_for_api(j) for j in active_jobs]
    cleaned_new = [_clean_job_for_api(j) for j in new_items]
    cleaned_reopened = [_clean_job_for_api(j) for j in reopened_items]

    # 1. Global Active API endpoint (docs/api/active.json)
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

    # 2. Global Latest API endpoint (docs/api/latest.json)
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

    # 3. Global RSS 2.0 Feed (docs/feed.xml)
    _generate_rss_feed(
        active_jobs,
        updated_at,
        target_path=FEED_PATH,
        title="InternScan Global — Tech & Software Internships",
        description="Live, verified engineering, AI/ML, data, and systems internships worldwide.",
        site_url=SITE_URL,
    )

    # 4. Country Partitions (docs/<country>/...)
    country_metrics = {}
    for country_code in SUPPORTED_COUNTRIES:
        c_meta = COUNTRY_METADATA.get(country_code, {})
        c_active = [j for j in active_jobs if j.get("country") == country_code]
        c_new = [j for j in new_items if j.get("country") == country_code]
        c_reopened = [j for j in reopened_items if j.get("country") == country_code]

        c_dir = os.path.join(DOCS_DIR, country_code)
        c_api_dir = os.path.join(c_dir, "api")
        os.makedirs(c_api_dir, exist_ok=True)

        c_cleaned_active = [_clean_job_for_api(j) for j in c_active]
        c_cleaned_new = [_clean_job_for_api(j) for j in c_new]
        c_cleaned_reopened = [_clean_job_for_api(j) for j in c_reopened]

        # docs/<country>/jobs.json (client-side web load)
        c_jobs_path = os.path.join(c_dir, "jobs.json")
        with open(c_jobs_path, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "updated_at": updated_at,
                    "jobs": {j["uid"]: j for j in c_active},
                },
                fh,
                indent=2,
                ensure_ascii=False,
            )
            fh.write("\n")

        # docs/<country>/api/active.json
        with open(os.path.join(c_api_dir, "active.json"), "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "version": __version__,
                    "country": country_code,
                    "updated_at": updated_at,
                    "total_active": len(c_cleaned_active),
                    "jobs": c_cleaned_active,
                },
                fh,
                indent=2,
                ensure_ascii=False,
            )
            fh.write("\n")

        # docs/<country>/api/latest.json
        with open(os.path.join(c_api_dir, "latest.json"), "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "version": __version__,
                    "country": country_code,
                    "updated_at": updated_at,
                    "new_count": len(c_cleaned_new),
                    "reopened_count": len(c_cleaned_reopened),
                    "total_active": len(c_cleaned_active),
                    "new_jobs": c_cleaned_new,
                    "reopened_jobs": c_cleaned_reopened,
                },
                fh,
                indent=2,
                ensure_ascii=False,
            )
            fh.write("\n")

        # docs/<country>/feed.xml
        c_feed_path = os.path.join(c_dir, "feed.xml")
        c_name = c_meta.get("name", country_code.upper())
        _generate_rss_feed(
            c_active,
            updated_at,
            target_path=c_feed_path,
            title=f"InternScan {c_name} — Tech Internships",
            description=f"Live, verified tech internships across top employers in {c_name}.",
            site_url=f"{SITE_URL}{country_code}/",
        )

        country_metrics[country_code] = {
            "name": c_name,
            "flag": c_meta.get("flag", "🌐"),
            "currency": c_meta.get("currency", "USD"),
            "active_count": len(c_cleaned_active),
            "tracked_companies": len(get_companies_for_country(country_code, include_fallback=True)),
            "hubs": c_meta.get("hubs", []),
        }

    # 5. Live metrics file for homepage (docs/metrics.json)
    with open(METRICS_PATH, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "version": __version__,
                "updated_at": updated_at,
                "total_active_global": len(cleaned_active),
                "countries": country_metrics,
            },
            fh,
            indent=2,
            ensure_ascii=False,
        )
        fh.write("\n")

    return {
        "active_count": len(cleaned_active),
        "new_count": len(cleaned_new),
        "reopened_count": len(cleaned_reopened),
        "countries": {k: v["active_count"] for k, v in country_metrics.items()},
    }


def _generate_rss_feed(
    active_jobs: List[dict],
    updated_at: str,
    target_path: str = FEED_PATH,
    title: str = "InternScan India — Tech & Software Internships",
    description: str = "Live verified tech internships.",
    site_url: str = SITE_URL,
) -> None:
    """Render standard RSS 2.0 XML for top 40 newest active jobs."""
    now_dt = datetime.now(timezone.utc)
    pub_date_str = format_datetime(now_dt)

    items_xml = []
    for j in active_jobs[:40]:
        j_title = html.escape(f"[{j.get('company', 'Tech')}] {j.get('title', 'Internship')}")
        link = html.escape(j.get("url", site_url))
        uid = html.escape(str(j.get("uid") or j.get("url", "")))
        cat = html.escape(j.get("category") or "Software")
        loc = html.escape(j.get("city_tag") or ", ".join(j.get("locations", [])) or "Global")
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
      <title>{j_title}</title>
      <link>{link}</link>
      <guid isPermaLink="false">{uid}</guid>
      <category>{cat}</category>
      <pubDate>{item_pub_date}</pubDate>
      <description>{desc}</description>
    </item>""")

    feed_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{title}</title>
    <link>{site_url}</link>
    <description>{description}</description>
    <language>en</language>
    <lastBuildDate>{pub_date_str}</lastBuildDate>
    <atom:link href="{site_url}feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    with open(target_path, "w", encoding="utf-8") as fh:
        fh.write(feed_content)
