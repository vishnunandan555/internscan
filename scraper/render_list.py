"""Render regional company lists inside regions/{code}/companies.md tracking scraper status."""
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
REGIONS_DIR = os.path.join(ROOT_DIR, "regions")
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


def _render_country_companies(
    country_code: str,
    succeeded: Optional[Iterable[str]] = None,
    failed: Optional[Dict[str, str]] = None,
    updated_at: Optional[str] = None,
) -> str:
    """Render localized company list for a specific country/region."""
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
        f"<a id=\"top\"></a>\n\n",
        f"# {c_flag} {c_name} — Tracked Employers & ATS Coverage\n\n",
        f"> 🕐 Last updated: **{updated_str}**\n\n",
        f"[💼 **View Active Openings (jobs.md)**](jobs.md) · "
        f"[🌐 **Global Project README**](../../README.md) · "
        f"[💻 **Live Web Portal**](https://vishnunandan555.github.io/internscan/{country_code}/)\n\n",
        f"This registry tracks employer coverage, ATS integrations, fallback adapters, and campus recruitment policies for **{c_name}**.\n\n",
        f"## 🟢 Directly Scraped Employers ({len(succeeded_list)})\n\n",
        f"Official careers portals synced automatically via direct API adapters (Workday, Greenhouse, Lever, SmartRecruiters, Oracle HCM, Eightfold, custom APIs):\n\n",
    ]

    for c in succeeded_list:
        lines.append(f"- {c}\n")
    lines.append("\n")

    lines.append(f"## 🟡 Bot-Protected Employers (Google Jobs Fallback) ({len(fallback_companies)})\n\n")
    status_note = "Active" if has_fallback_keys() else "Standby (Requires SERP_API_KEY / RAPIDAPI_KEY in environment)"
    lines.append(f"> Integration Status: **{status_note}**\n\n")
    if fallback_companies:
        for c in sorted(fallback_companies, key=lambda x: x["name"]):
            lines.append(f"- **{c['name']}** — *Indexed via Google Jobs / JSearch fallback adapter*\n")
    else:
        lines.append("*None*\n")
    lines.append("\n")

    lines.append(f"## ⚪ Unsupported / Campus-Only Employers ({len(unsupported_items)})\n\n")
    if unsupported_items:
        lines.append(f"Employers that do not host public ATS internship listings for {c_name} (e.g. exclusive university placement cell hiring, internal referrals only, or closed portals):\n\n")
        for name, reason in unsupported_items:
            lines.append(f"- **{name}** — *{reason}*\n")
    else:
        lines.append("*None documented*\n")
    lines.append("\n---\n\n")
    lines.append(f"[⬆️ Back to Top](#top) · [💼 View {c_name} Jobs](jobs.md) · [🌐 Global Directory](../../README.md)\n")

    return "".join(lines)


def render_list(
    succeeded: Optional[Iterable[str]] = None,
    failed: Optional[Dict[str, str]] = None,
    updated_at: Optional[str] = None,
) -> None:
    """Generate regions/{code}/companies.md for each supported region atomically."""
    os.makedirs(REGIONS_DIR, exist_ok=True)

    for code in SUPPORTED_COUNTRIES:
        country_dir = os.path.join(REGIONS_DIR, code)
        os.makedirs(country_dir, exist_ok=True)
        content = _render_country_companies(code, succeeded, failed, updated_at)
        target_path = os.path.join(country_dir, "companies.md")
        tmp_path = target_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, target_path)
        except Exception as exc:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            raise IOError(f"Failed to atomically render {target_path}: {exc}") from exc


render = render_list
