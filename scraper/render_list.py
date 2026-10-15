"""Render LIST.md and country-specific lists/in.md, lists/us.md tracking scraper status."""
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, Optional
from .countries import (
    COUNTRY_METADATA,
    SUPPORTED_COUNTRIES,
    get_companies_for_country,
    get_unsupported_for_country,
    has_fallback_keys,
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LISTS_DIR = os.path.join(ROOT_DIR, "lists")
GLOBAL_LIST_PATH = os.path.join(ROOT_DIR, "LIST.md")
IST = timezone(timedelta(hours=5, minutes=30))


def _to_ist_str(iso_utc: Optional[str] = None) -> str:
    """Convert UTC ISO timestamp to formatted IST timestamp string."""
    try:
        if iso_utc:
            dt = datetime.strptime(iso_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            return dt.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        pass
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")


def _render_country_list(
    country_code: str,
    succeeded: Optional[Iterable[str]] = None,
    failed: Optional[Dict[str, str]] = None,
    updated_at: Optional[str] = None,
) -> str:
    """Render localized company list for a specific country."""
    failed = failed or {}
    meta = COUNTRY_METADATA.get(country_code, {})
    c_name = meta.get("name", country_code.upper())
    c_flag = meta.get("flag", "🌐")

    direct_companies = get_companies_for_country(country_code, include_fallback=False)
    all_companies = get_companies_for_country(country_code, include_fallback=True)
    fallback_companies = [c for c in all_companies if c not in direct_companies]
    unsupported_items = sorted(get_unsupported_for_country(country_code).items())

    all_configured = {c["name"] for c in direct_companies}
    if succeeded:
        active_scraped = (set(succeeded) & all_configured) if succeeded else all_configured
    else:
        active_scraped = all_configured
    active_scraped = active_scraped - set(failed.keys())
    succeeded_list = sorted(active_scraped)

    updated_str = _to_ist_str(updated_at)

    lines = [
        f"# {c_flag} {c_name} Companies List\n\n",
        f"> 🕐 Last updated: **{updated_str}**\n\n",
        f"A quick reference list of companies tracked by the scraper in **{c_name}** and their latest status.\n\n",
        f"## Scraped Companies ({len(succeeded_list)})\n\n",
    ]

    for c in succeeded_list:
        lines.append(f"- {c}\n")
    lines.append("\n")

    lines.append(f"## Bot-Protected Companies (Google Jobs Fallback) ({len(fallback_companies)})\n\n")
    status_note = "Active" if has_fallback_keys() else "Standby (Requires SERP_API_KEY / RAPIDAPI_KEY in environment)"
    lines.append(f"> Integration Status: **{status_note}**\n\n")
    if fallback_companies:
        for c in sorted(fallback_companies, key=lambda x: x["name"]):
            lines.append(f"- **{c['name']}** — *Indexed via Google Jobs / JSearch fallback adapter*\n")
    else:
        lines.append("*None*\n")
    lines.append("\n")

    lines.append(f"## Unsupported / Campus-Only Companies ({len(unsupported_items)})\n\n")
    if unsupported_items:
        for name, reason in unsupported_items:
            lines.append(f"- **{name}** — *{reason}*\n")
    else:
        lines.append("*None documented*\n")
    lines.append("\n")

    return "".join(lines)


def render_list(
    succeeded: Optional[Iterable[str]] = None,
    failed: Optional[Dict[str, str]] = None,
    updated_at: Optional[str] = None,
) -> None:
    """Generate lists/in.md, lists/us.md, and global master LIST.md."""
    os.makedirs(LISTS_DIR, exist_ok=True)
    updated_str = _to_ist_str(updated_at)

    # 1. Country-specific files
    for code in ("in", "us", "ca", "uk", "eu"):
        content = _render_country_list(code, succeeded, failed, updated_at)
        target_path = os.path.join(LISTS_DIR, f"{code}.md")
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 2. Master Global LIST.md
    lines = [
        "# Tracked Companies Directory (Global)\n\n",
        f"> 🕐 Last updated: **{updated_str}**\n\n",
        "InternScan tracks engineering, AI/ML, and data internships across premier global tech employers.\n\n",
        "## Country Directories\n\n",
        "Select a country directory for the complete list of tracked employers, fallback adapters, and campus policies:\n\n",
        "- [🇮🇳 **India Companies Directory (lists/in.md)**](lists/in.md) — *60 Tracked Employers, 5 Fallbacks, 32 Documented Limitations*\n",
        "- [🇺🇸 **United States Companies Directory (lists/us.md)**](lists/us.md) — *54 Tracked Employers, High-Growth Innovators*\n\n",
        "## Summary by Country\n\n",
        "| Country | Flag | Tracked Employers | Primary Tech Hubs | Direct Directory |\n",
        "| :--- | :---: | :---: | :--- | :---: |\n",
    ]

    for c_code in ("in", "us", "ca", "uk", "eu"):
        meta = COUNTRY_METADATA.get(c_code, {})
        cos = get_companies_for_country(c_code, include_fallback=True)
        flag = meta.get("flag", "🌐")
        name = meta.get("name", c_code.upper())
        hubs = ", ".join(meta.get("hubs", [])[:4])
        doc_link = f"[View {c_code.upper()}](lists/{c_code}.md)" if os.path.exists(os.path.join(LISTS_DIR, f"{c_code}.md")) else "Included in Global"
        lines.append(f"| **{name}** | {flag} | {len(cos)} | {hubs} | {doc_link} |\n")

    lines.append("\n---\n*Maintained automatically by the InternScan scrapers.* \n")

    with open(GLOBAL_LIST_PATH, "w", encoding="utf-8") as f:
        f.write("".join(lines))


render = render_list
