"""Render LIST.md tracking all scraped companies and scraping failures."""
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, Optional
from .companies import COMPANIES, FALLBACK_COMPANIES, UNSUPPORTED, has_fallback_keys

LIST_PATHS = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "LIST.md")),
]
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


def render_list(
    succeeded: Optional[Iterable[str]] = None,
    failed: Optional[Dict[str, str]] = None,
    updated_at: Optional[str] = None,
) -> None:
    """Generate a simple, minimal LIST.md tracking scraped companies and issues."""
    failed = failed or {}
    all_configured = {c["name"] for c in COMPANIES}

    if succeeded:
        active_scraped = set(succeeded) | all_configured
    else:
        active_scraped = all_configured

    # Ensure any company in failed is not shown as successfully scraped
    active_scraped = active_scraped - set(failed.keys())

    succeeded_list = sorted(active_scraped)
    failed_items = sorted(failed.items())
    updated_str = _to_ist_str(updated_at)

    lines = [
        "# Companies List\n\n",
        f"> 🕐 Last updated: **{updated_str}**\n\n",
        "A quick reference list of companies tracked by the scraper and their latest status.\n\n",
        f"## Scraped Companies ({len(succeeded_list)})\n\n",
    ]

    if succeeded_list:
        for c in succeeded_list:
            lines.append(f"- {c}\n")
    else:
        lines.append("*None*\n")
    lines.append("\n")

    lines.append(f"## Scraping Failed ({len(failed_items)})\n\n")
    if failed_items:
        for name, err in failed_items:
            short_err = str(err).split("\n")[0].strip()
            lines.append(f"- **{name}**: `{short_err}`\n")
    else:
        lines.append("*None*\n")
    lines.append("\n")

    unsupported_items = sorted(UNSUPPORTED.items())
    lines.append(f"## Bot-Protected Companies (Google Jobs Fallback) ({len(FALLBACK_COMPANIES)})\n\n")
    status_note = "Active" if has_fallback_keys() else "Standby (Requires SERP_API_KEY / RAPIDAPI_KEY in environment)"
    lines.append(f"> Integration Status: **{status_note}**\n\n")
    for c in sorted(FALLBACK_COMPANIES, key=lambda x: x["name"]):
        lines.append(f"- **{c['name']}** — *Indexed via Google Jobs / JSearch fallback adapter*\n")
    lines.append("\n")

    lines.append(f"## Unsupported / Campus-Only Companies ({len(unsupported_items)})\n\n")
    for name, reason in unsupported_items:
        lines.append(f"- **{name}** — *{reason}*\n")
    lines.append("\n")

    content = "".join(lines)

    for path in LIST_PATHS:
        try:
            if os.path.exists(os.path.dirname(path)):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
        except Exception as e:
            print(f"Warning: could not write to {path}: {e}")
