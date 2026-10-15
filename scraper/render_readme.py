"""Render README.md from data/jobs.json. The README is generated — never hand-edit."""
import os
from datetime import datetime, timedelta, timezone

README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
_TMP_README_PATH = README_PATH + ".tmp"
NEW_BADGE_DAYS = 7
IST = timezone(timedelta(hours=5, minutes=30))


def _to_ist_str(iso_utc: str) -> str:
    """Convert UTC ISO timestamp to formatted IST timestamp string."""
    try:
        dt = datetime.strptime(iso_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")


HEADER = """\
<a id="top"></a>
# 🇮🇳 InternScan India — Software Engineering & Tech Internship Tracker

Auto-updated directory of verified **tech & software-engineering internships in India** —
AI/ML, Data, Full-Stack, Backend, Frontend, Mobile, QA/SDET, and Security roles — at
{n_companies} top tech companies, GCCs, and high-growth Indian unicorns. Scraped directly
from official careers APIs daily (at 03:00 AM IST) by GitHub Actions.

[![Live Web Dashboard](https://img.shields.io/badge/Live_Dashboard-InternScan_India-f97316?style=for-the-badge&logo=googlechrome&logoColor=white)](https://vishnunandan555.github.io/internscan/)
[![Version](https://img.shields.io/badge/Version-v2.0.0-blue?style=for-the-badge&logo=semver&logoColor=white)](https://github.com/vishnunandan555/internscan/releases)
[![Telegram Bot Guide](https://img.shields.io/badge/Telegram_Bot-Deploy_in_3_mins-0088cc?style=for-the-badge&logo=telegram&logoColor=white)](bot/README.md)
[![Public API](https://img.shields.io/badge/Public_API-REST_&_RSS-10b981?style=for-the-badge&logo=fastapi&logoColor=white)](#-public-api--telegram-bot-integration)
[![Tracked Companies](https://img.shields.io/badge/Tracked_Companies-59_Active-2563eb?style=for-the-badge&logo=airplay&logoColor=white)](LIST.md)
[![Developer Guide](https://img.shields.io/badge/Developer_Guide-GUIDE.md-475569?style=for-the-badge&logo=readme&logoColor=white)](GUIDE.md)
[![Scrape Logs](https://img.shields.io/badge/Scrape_Logs-logs%2F-334155?style=for-the-badge&logo=files&logoColor=white)](logs/)

> 🕐 Last updated: **{updated}** · 📌 **{n_open}** open internships
> · ✨ = added in the last {new_days} days

⭐ Star this repository to keep track of new openings — or watch *Activity* for commits titled “new internship(s)”.

"""

FOOTER = """
---

## 🤖 Public API & Telegram Bot Integration

InternScan India provides **free, open, high-speed developer APIs** and a **ready-to-deploy Telegram Bot** (< 35 MB RAM) to easily automate internship notifications for campus clubs, placement groups, and personal channels.

### 1. Ready-to-Deploy Telegram Bot (`bot/`)

Our pre-built bot runs 24/7 on minimal cloud servers (**< 35 MB RAM**, perfect for ₹10/mo Nano nodes or Raspberry Pis):
- **Auto-Broadcasts:** Pushes newly detected internships directly to your Telegram Channel or Group.
- **Interactive Commands:** `/latest` (new roles), `/active` (all roles), `/status` (uptime and memory usage).
- 📖 **Quickstart Guide:** Read **[bot/README.md](bot/README.md)** to launch in 3 minutes.

### 2. Public REST API Endpoints (No Auth, CORS Enabled)

| Endpoint | Method | Format | Description |
|---|---|---|---|
| `https://vishnunandan555.github.io/internscan/api/latest.json` | `GET` | JSON | New and reopened internships from today's scrape. |
| `https://vishnunandan555.github.io/internscan/api/active.json` | `GET` | JSON | Clean array of all currently active verified internships. |
| `https://vishnunandan555.github.io/internscan/feed.xml` | `GET` | RSS 2.0 | Standard RSS feed for no-code bots (like `@FeedManBot`) or Discord webhooks. |

```python
# Quick Python Example
import requests

data = requests.get("https://vishnunandan555.github.io/internscan/api/latest.json").json()
print(f"Discovered {data['new_count']} new openings today!")
for job in data.get("new_jobs", []):
    print(f"• {job['company']}: {job['title']} -> {job['url']}")
```

### 3. Direct GitHub Actions Push (Zero Server / Fork)

If you don't want to host any server:
1. Fork this repository.
2. Add your secrets in **Settings → Secrets and variables → Actions**:
   - `TELEGRAM_BOT_TOKEN`: Your token from `@BotFather`.
   - `TELEGRAM_CHAT_ID`: Your channel (e.g. `@my_channel`) or chat ID.
3. Your GitHub Actions cron runs daily and sends new alerts automatically!

---

## 🤝 Request a Company or Report an Issue

- **Want a company added?** Check **[LIST.md](LIST.md)** first to see if it is already actively scraped or documented as unsupported. If it's missing, [open a Company Request issue](https://github.com/vishnunandan555/internscan/issues/new?title=%5BCompany+Request%5D+<Company+Name>) with the company's official career portal URL!
- **Found a broken link or expired posting?** Please [open a Bug Report issue](https://github.com/vishnunandan555/internscan/issues/new?title=%5BBug%5D+<Issue+Description>) so we can investigate.
- **Looking for developer guides, CLI usage, or scraper architecture?** Read the complete **[Developer & System Guide (GUIDE.md)](GUIDE.md)**.
"""


def _slug(name):
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


def _md_escape(text):
    return text.replace("|", "\\|").strip()


def _fmt_locations(locations, limit=2):
    locs = [loc for loc in locations if loc]
    if not locs:
        return "India"
    shown = "; ".join(_md_escape(loc) for loc in locs[:limit])
    extra = len(locs) - limit
    if extra > 0:
        shown += " *(+{} more)*".format(extra)
    return shown


def render(state):
    from .companies import get_companies, UNSUPPORTED
    tracked = [c["name"] for c in get_companies()]
    jobs = [j for j in state["jobs"].values() if j.get("active", True)]
    updated = state.get("updated_at") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=NEW_BADGE_DAYS)).strftime("%Y-%m-%d")

    by_company = {name: [] for name in tracked}
    for j in jobs:
        by_company.setdefault(j["company"], []).append(j)

    companies = sorted(by_company)
    out = [HEADER.format(
        n_companies=len(companies),
        updated=_to_ist_str(updated),
        n_open=len(jobs),
        new_days=NEW_BADGE_DAYS,
    )]

    # Fast jump to active postings
    out.append(f"[⬇️ **Skip directly to Open Internship Postings ({len(jobs)})**](#open-internships)\n\n")

    # summary table with anchors
    out.append("| Company | Open Internships in India |\n|---|:---:|\n")
    for c in companies:
        n = len(by_company[c])
        label = "[{}](#{})".format(c, _slug(c)) if n else c
        out.append("| {} | {} |\n".format(label, f"**{n}**" if n else "—"))
    for name, why in sorted(UNSUPPORTED.items()):
        out.append("| {} | *{}* |\n".format(name, why))
    out.append("\n---\n\n<a id=\"open-internships\"></a>\n\n## 💼 Open Internship Postings\n\n")

    sorted_by_company = {
        c: sorted(
            by_company[c],
            key=lambda j: (j.get("posted") or j.get("first_seen", ""), j["title"]),
            reverse=True,
        )
        for c in companies
        if by_company.get(c)
    }

    for c, rows in sorted_by_company.items():
        out.append("## {}\n\n".format(c))
        out.append("| Role | Category | Hub / Location | Posted | First seen |\n"
                   "|---|---|---|---|---|\n")
        for j in rows:
            is_new = (j.get("first_seen") or "") >= cutoff
            badge = " ✨" if is_new else ""
            title = "[{}]({}){}".format(_md_escape(j["title"]), j["url"], badge)
            cat = j.get("category") or "Software"
            hub = j.get("city_tag") or _fmt_locations(j.get("locations", []))
            posted = j.get("posted") or "—"
            first_seen = j.get("first_seen") or "—"
            out.append("| {} | {} | {} | {} | {} |\n".format(
                title, cat, hub, posted, first_seen))
        out.append("\n[⬆️ Back to Top](#top)\n\n")

    out.append(FOOTER)

    try:
        with open(_TMP_README_PATH, "w", encoding="utf-8") as fh:
            fh.writelines(out)
        os.replace(_TMP_README_PATH, README_PATH)
    except Exception as exc:
        if os.path.exists(_TMP_README_PATH):
            try:
                os.remove(_TMP_README_PATH)
            except OSError:
                pass
        raise IOError(f"Failed to atomically render README to {README_PATH}: {exc}") from exc

