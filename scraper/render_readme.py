"""Render root project README.md and regional regions/{code}/jobs.md files atomically."""
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from .countries import (
    COUNTRY_METADATA,
    SUPPORTED_COUNTRIES,
    get_companies_for_country,
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
README_PATH = os.path.join(ROOT_DIR, "README.md")
REGIONS_DIR = os.path.join(ROOT_DIR, "regions")
NEW_BADGE_DAYS = 7
IST = timezone(timedelta(hours=5, minutes=30))

US_STATES_MAP = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
    "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
    "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
    "district of columbia": "DC"
}
US_CODES_SET = set(US_STATES_MAP.values())

CA_PROVINCES_MAP = {
    "ontario": "ON", "quebec": "QC", "british columbia": "BC", "alberta": "AB",
    "manitoba": "MB", "saskatchewan": "SK", "nova scotia": "NS", "new brunswick": "NB",
    "newfoundland and labrador": "NL", "prince edward island": "PE"
}

EU_COUNTRIES_MAP = {
    "esp": "Spain", "fra": "France", "gbr": "UK", "deu": "Germany", "irl": "Ireland",
    "ita": "Italy", "pol": "Poland", "rou": "Romania", "che": "Switzerland", "nor": "Norway",
    "dnk": "Denmark", "swe": "Sweden", "nld": "Netherlands", "bel": "Belgium", "cze": "Czechia",
    "aut": "Austria", "prt": "Portugal", "fin": "Finland"
}

KNOWN_COUNTRIES = {
    "united states", "usa", "us", "u.s.a.", "u.s.", "canada", "united kingdom", "uk",
    "great britain", "england", "scotland", "wales", "ireland", "germany", "france",
    "poland", "spain", "italy", "switzerland", "netherlands", "sweden", "norway",
    "denmark", "czech republic", "czechia", "romania", "belgium", "austria", "portugal",
    "india"
}


def _to_ist_str(iso_utc: str) -> str:
    """Convert UTC ISO timestamp to formatted IST timestamp string."""
    try:
        dt = datetime.strptime(iso_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")


def _slug(name: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|").strip()


def _clean_location(raw_loc: str) -> str:
    if not raw_loc:
        return ""
    s = str(raw_loc).strip()
    if re.match(r"^\d+\s+Locations?$", s, re.IGNORECASE):
        return ""
    if re.search(r"\bmultiple locations?\b", s, re.IGNORECASE):
        return "Multiple Locations"

    s = re.sub(r"^(?:US|USA|UK|India)\s*[-–—, ]\s*", "", s, flags=re.IGNORECASE)

    for st_name, code in US_STATES_MAP.items():
        m_st_city = re.match(r"^" + st_name + r"\s+([A-Za-z\s]+)$", s, re.IGNORECASE)
        if m_st_city:
            return f"{m_st_city.group(1).title()}, {code}"

    m_wm = re.search(r"\b([A-Z]{2})\s+([A-Z\s]+?)\s+Home Office", s, re.IGNORECASE)
    if m_wm:
        return f"{m_wm.group(2).strip().title()}, {m_wm.group(1).upper()}"

    m_mi = re.match(r"^([A-Za-z]+).*?\b([A-Z]{2})\b$", s)
    if m_mi and m_mi.group(2).upper() in US_CODES_SET:
        return f"{m_mi.group(1).title()}, {m_mi.group(2).upper()}"

    m_intel_eu = re.match(r"^(Poland|Ireland|Germany|UK|France|Spain|Italy|Sweden|Romania|Czech Republic)\s+([A-Za-z]+)$", s, re.IGNORECASE)
    if m_intel_eu:
        return f"{m_intel_eu.group(2).title()}, {m_intel_eu.group(1).title()}"

    m_ms = re.match(r"^(?:United States|Czech Republic|Belgium|Netherlands|Poland|Germany|Ireland),\s*([^,]+),\s*([^,]+)$", s, re.IGNORECASE)
    if m_ms:
        p1 = m_ms.group(1).strip()
        p2 = m_ms.group(2).strip()
        if p1.lower() in US_STATES_MAP:
            return f"{p2.title()}, {US_STATES_MAP[p1.lower()]}"
        return f"{p2.title()}, {p1.title()}"

    parts = [p.strip() for p in s.split(",") if p.strip()]
    cleaned = []
    for p in parts:
        if re.match(r"^(?:\d{4,6}(?:-\d{4})?|[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}|H91\s*[A-Z0-9]+)$", p, re.IGNORECASE):
            continue
        if re.match(r"^(?:United States(?: of America)?|USA|U\.S\.A\.|US|Canada|CAN|United Kingdom|UK|Great Britain|ESP|FRA|DEU|India)$", p, re.IGNORECASE):
            continue
        if re.match(r"^(?:N/A|NONE)$", p, re.IGNORECASE):
            continue
        cleaned.append(p)

    if not cleaned:
        return s

    if len(cleaned) >= 2:
        part0 = cleaned[0].replace("_", " ").title()
        part1 = cleaned[1].strip()
        if part0.lower() == "all":
            return part1.title()

        if part0.lower() in KNOWN_COUNTRIES and part1.lower() not in KNOWN_COUNTRIES:
            return f"{part1.title()}, {part0}"

        if part0.lower() in US_STATES_MAP and part1.lower() not in US_STATES_MAP:
            return f"{part1.title()}, {US_STATES_MAP[part0.lower()]}"

        city = part0
        st_lower = part1.lower()
        if st_lower in US_STATES_MAP:
            return f"{city}, {US_STATES_MAP[st_lower]}"
        if st_lower in CA_PROVINCES_MAP:
            return f"{city}, {CA_PROVINCES_MAP[st_lower]}"
        if part1.upper() in US_CODES_SET:
            return f"{city}, {part1.upper()}"
        if st_lower in EU_COUNTRIES_MAP:
            return f"{city}, {EU_COUNTRIES_MAP[st_lower]}"
        return f"{city}, {st_lower.title()}"

    if len(cleaned) == 1:
        c = cleaned[0].replace("_", " ").title()
        if c.upper() in US_CODES_SET:
            return f"{c.upper()}, US"
        if c.lower() in US_STATES_MAP:
            return f"{US_STATES_MAP[c.lower()]}, US"
        return c

    return s


def _fmt_locations(locations: List[str], default_loc: str = "Regional", limit: int = 2) -> str:
    cleaned = []
    for loc in locations:
        if loc:
            c = _clean_location(loc)
            if c and c not in cleaned:
                cleaned.append(c)
    if not cleaned:
        return default_loc
    shown = "; ".join(_md_escape(loc) for loc in cleaned[:limit])
    extra = len(cleaned) - limit
    if extra > 0:
        shown += f" *(+{extra} more)*"
    return shown


def _render_country_jobs_md(code: str, all_jobs: List[dict], updated_iso: str, cutoff: str) -> str:
    """Generate Markdown job listing table for a specific region."""
    meta = COUNTRY_METADATA.get(code, {})
    c_name = meta.get("name", code.upper())
    c_flag = meta.get("flag", "🌐")

    jobs = [j for j in all_jobs if j.get("active", True) and j.get("country", "") == code]
    tracked_cos = [c["name"] for c in get_companies_for_country(code, include_fallback=True)]

    by_company = {name: [] for name in tracked_cos}
    for j in jobs:
        by_company.setdefault(j["company"], []).append(j)

    companies_with_jobs = sorted([c for c, r in by_company.items() if r])
    updated_str = _to_ist_str(updated_iso)

    lines = [
        f"<a id=\"top\"></a>\n\n",
        f"# {c_flag} {c_name} — Active Tech & Software Internship Listings\n\n",
        f"> 🕐 Last updated: **{updated_str}** · 📌 **{len(jobs)}** open verified internships\n",
        f"> · ✨ = added in the last {NEW_BADGE_DAYS} days\n\n",
        f"[📋 **Tracked Employers ({len(tracked_cos)})**](companies.md) · "
        f"[🌐 **Global Project README**](../../README.md) · "
        f"[💻 **Live Web Portal**](https://vishnunandan555.github.io/internscan/{code}/) · "
        f"[⚡ **REST API**](https://vishnunandan555.github.io/internscan/{code}/api/active.json)\n\n",
        f"Verified engineering, AI/ML, data, and systems internships across premier employers in **{c_name}**. "
        f"All postings are scraped directly from official ATS portals every 24 hours.\n\n",
        f"[⬇️ **Skip directly to Open Internship Postings ({len(jobs)})**](#open-internships)\n\n",
        f"## 🏢 Employers with Open Roles\n\n",
        f"| Company | Open Internships in {c_name} |\n|---|:---:|\n",
    ]

    for c in companies_with_jobs:
        n = len(by_company[c])
        label = f"[{c}](#{_slug(c)})" if n else c
        lines.append(f"| {label} | **{n}** |\n")

    lines.append("\n---\n\n<a id=\"open-internships\"></a>\n\n## 💼 Open Internship Postings\n\n")

    if not jobs:
        lines.append(f"*Currently no verified openings are listed for {c_name}. Check back after the next scheduled scrape or browse our [Live Web Portal](https://vishnunandan555.github.io/internscan/{code}/).*\n\n")
    else:
        for c in companies_with_jobs:
            rows = sorted(
                by_company[c],
                key=lambda j: (j.get("posted") or j.get("first_seen", ""), j.get("title", "")),
                reverse=True,
            )
            lines.append(f"### {c}\n\n")
            lines.append("| Role | Category | Hub / Location | Posted | First seen |\n|---|---|---|---|---|\n")
            for j in rows:
                is_new = (j.get("first_seen") or "") >= cutoff
                badge = " ✨" if is_new else ""
                title = f"[{_md_escape(j.get('title', ''))}]({j.get('url', '#')}){badge}"
                cat = j.get("category") or "Software"
                tag = (j.get("city_tag") or "").strip()
                if "other" in tag.lower() or "multiple" in tag.lower() or not tag:
                    hub = _fmt_locations(j.get("locations", []), default_loc=c_name)
                else:
                    hub = tag
                posted = j.get("posted") or "—"
                first_seen = j.get("first_seen") or "—"
                lines.append(f"| {title} | {cat} | {hub} | {posted} | {first_seen} |\n")
            lines.append(f"\n[⬆️ Back to Top](#top) · [📋 View {c_name} Companies](companies.md)\n\n")

    lines.append("---\n\n")
    lines.append(f"[🌐 Global Project README](../../README.md) · [📋 Tracked Companies](companies.md) · [💻 Web Portal](https://vishnunandan555.github.io/internscan/{code}/)\n")
    return "".join(lines)


def _render_global_readme(state: dict, cutoff: str) -> str:
    """Generate root project README.md as a clean GitHub product showcase."""
    jobs_dict = state.get("jobs", {})
    active_jobs = [j for j in jobs_dict.values() if j.get("active", True)]
    total_active = len(active_jobs)
    updated_iso = state.get("updated_at") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updated_ist = _to_ist_str(updated_iso)

    counts: Dict[str, int] = {}
    for code in SUPPORTED_COUNTRIES:
        counts[code] = sum(1 for j in active_jobs if j.get("country") == code)

    content = f"""\
<a id="top"></a>
<p align="center">
  <a href="https://vishnunandan555.github.io/internscan/">
    <img src="docs/icon.png" width="96" height="96" alt="InternScan Logo">
  </a>
</p>
<h1 align="center">InternScan — The Global Directory for Tech Internships</h1>

<p align="center">
  <strong>Automated, open-source directory of verified engineering, AI/ML, and tech internships across top employers worldwide. 100% open source and direct.</strong>
</p>

<p align="center">
  <a href="https://vishnunandan555.github.io/internscan/"><img src="https://img.shields.io/badge/Live_Dashboard-Explore_All_Regions-6366f1?style=for-the-badge&logo=globe&logoColor=white" alt="Live Dashboard"></a>
  <a href="#-regional-internship-trackers"><img src="https://img.shields.io/badge/Verified_Roles-{total_active}_Active-10b981?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Active Roles"></a>
  <a href="#-regional-internship-trackers"><img src="https://img.shields.io/badge/Tracked_Employers-65+_Global-2563eb?style=for-the-badge&logo=airplay&logoColor=white" alt="Tracked Employers"></a>
  <a href="#-regional-internship-trackers"><img src="https://img.shields.io/badge/Supported_Regions-5_Countries-f59e0b?style=for-the-badge&logo=target&logoColor=white" alt="Supported Regions"></a>
  <a href="https://github.com/vishnunandan555/internscan/actions/workflows/update.yml"><img src="https://img.shields.io/badge/Sync_Cadence-Daily_03:00_IST-0ea5e9?style=for-the-badge&logo=githubactions&logoColor=white" alt="Sync Cadence"></a>
  <a href="ARCHITECTURE.md"><img src="https://img.shields.io/badge/Architecture-System_Design-8b5cf6?style=for-the-badge&logo=diagram-next&logoColor=white" alt="Architecture"></a>
  <a href="bot/README_bot.md"><img src="https://img.shields.io/badge/Telegram_Bot-Deploy_in_3_mins-0088cc?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Bot"></a>
  <a href="https://vishnunandan555.github.io/internscan/api/active.json"><img src="https://img.shields.io/badge/Public_API-REST_&_RSS-ec4899?style=for-the-badge&logo=fastapi&logoColor=white" alt="Public API"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/Contributing-Join_Us-14b8a6?style=for-the-badge&logo=github&logoColor=white" alt="Contributing"></a>
</p>

> 🕐 Last synchronized: **{updated_ist}** · 📌 **{total_active}** active verified tech internships worldwide across **5** supported regions.

---

## 🌍 Regional Internship Trackers

InternScan partitions verified listings into dedicated regional portals. Each region features its own Markdown job tracker, company coverage registry, and high-speed web application:

| Region | Flag | Active Roles | Markdown Job Directory | Tracked Employers | Live Web Portal |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **India** | 🇮🇳 | **{counts.get('in', 0)}** | [🇮🇳 **View India Jobs**](regions/in/jobs.md) | [Tracked Companies](regions/in/companies.md) | [Open India Dashboard](https://vishnunandan555.github.io/internscan/in/) |
| **United States** | 🇺🇸 | **{counts.get('us', 0)}** | [🇺🇸 **View US Jobs**](regions/us/jobs.md) | [Tracked Companies](regions/us/companies.md) | [Open US Dashboard](https://vishnunandan555.github.io/internscan/us/) |
| **Canada** | 🇨🇦 | **{counts.get('ca', 0)}** | [🇨🇦 **View Canada Jobs**](regions/ca/jobs.md) | [Tracked Companies](regions/ca/companies.md) | [Open Canada Dashboard](https://vishnunandan555.github.io/internscan/ca/) |
| **United Kingdom** | 🇬🇧 | **{counts.get('uk', 0)}** | [🇬🇧 **View UK Jobs**](regions/uk/jobs.md) | [Tracked Companies](regions/uk/companies.md) | [Open UK Dashboard](https://vishnunandan555.github.io/internscan/uk/) |
| **Europe** | 🇪🇺 | **{counts.get('eu', 0)}** | [🇪🇺 **View Europe Jobs**](regions/eu/jobs.md) | [Tracked Companies](regions/eu/companies.md) | [Open Europe Dashboard](https://vishnunandan555.github.io/internscan/eu/) |

---

## ⚡ Why InternScan? Core Platform Invariants

Unlike generic job scrapers and aggregator boards, InternScan is built on strict engineering invariants:

1. **Zero Ghost Jobs (100% Direct Official ATS Sync):**  
   Every position is pulled directly from official corporate ATS APIs (**Workday, Greenhouse, Lever, SmartRecruiters, Oracle HCM, Eightfold, and custom portals**). Never third-party aggregators or spam recruitment boards.
2. **Jobs Are Never Deleted:**  
   When a posting is closed by an employer, it is marked `active: false` and timestamped with `closed = today`. Historical postings remain searchable for interview preparation and market intelligence.
3. **Strict Memory Budget (< 35 MB RAM):**  
   Both our scraping daemon and Telegram bot run cleanly on minimal cloud nodes (e.g. ₹10/mo Nano nodes or micro VPS). Pure Python standard library with zero headless browser overhead.
4. **POSIX Atomic Persistence:**  
   Every write to master JSON databases, API payloads, and Markdown directories writes first to a `.tmp` file and commits via `os.replace` to prevent data corruption.
5. **Categorized Engineering Buckets:**  
   Rule-based categorization groups roles into Software, AI/ML, Data Engineering, Cloud/Infra, Silicon/Hardware, Mobile, and Security.

---

## 🤖 Public REST & RSS APIs (No Auth, CORS-Enabled)

InternScan provides free public developer APIs updated on every scrape:

| Endpoint | Method | Format | Description |
|---|---|---|---|
| `https://vishnunandan555.github.io/internscan/api/active.json` | `GET` | JSON | All currently active verified internships worldwide. |
| `https://vishnunandan555.github.io/internscan/api/latest.json` | `GET` | JSON | New and reopened internships discovered in today's scrape. |
| `https://vishnunandan555.github.io/internscan/feed.xml` | `GET` | RSS 2.0 | Standard RSS feed for Slack, Discord webhooks, or Feed readers. |
| `https://vishnunandan555.github.io/internscan/metrics.json` | `GET` | JSON | Scraper health, platform metrics, and country breakdowns. |
| `https://vishnunandan555.github.io/internscan/{{region}}/api/active.json` | `GET` | JSON | Regional active postings (`in`, `us`, `ca`, `uk`, `eu`). |

```python
# Quick Python Example
import requests

data = requests.get("https://vishnunandan555.github.io/internscan/api/active.json").json()
print(f"Total active global roles: {{data['total_active']}}")
for job in data.get("jobs", [])[:5]:
    print(f"• [{{job['country'].upper()}}] {{job['company']}}: {{job['title']}} ({{job['city_tag']}})")
```

---

## 📱 Telegram Alert Bot (`bot/`)

Our ultra-lightweight Telegram bot runs 24/7 (**< 35 MB RAM**) to dispatch instant alerts when new roles open:
- **Instant Broadcasts:** Sends structured HTML alert cards with company logos, tech hub tags, and direct application links.
- **Interactive Commands:** `/latest` (recent roles), `/active` (all roles), `/status` (uptime and system stats).
- 📖 **Deployment Guide:** Follow the [bot/README_bot.md](bot/README_bot.md) to launch your own instance in 3 minutes.

---

## 📚 Repository Map & Documentation

| Document | Purpose |
|---|---|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System blueprints, synchronization pipeline, and multi-region persistence |
| **[GUIDE.md](GUIDE.md)** | Developer handbook, CLI flags, ATS onboarding, and local testing |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Guidelines for adding new ATS adapters, company configs, and PR standards |
| **[SECURITY.md](SECURITY.md)** | Vulnerability reporting and ethical crawler access guidelines |
| **[AGENTS.md](AGENTS.md)** | Inviolable architectural invariants and memory rules for AI coding agents |

### 📂 Directory Map
- **[`regions/`](regions/README_regions.md)**: Regional Markdown trackers (`jobs.md` & `companies.md`) for `in/`, `us/`, `ca/`, `uk/`, and `eu/`.
- **[`scraper/`](scraper/)**: Concurrent ThreadPool scraper engine, modular ATS adapters, and regional registries.
- **[`data/`](data/)**: Master and region-partitioned JSON databases with atomic schema persistence.
- **[`docs/`](docs/)**: Production GitHub Pages web application (Vanilla CSS tokens, zero dependencies).
- **[`bot/`](bot/)**: Production Telegram bot daemon (< 35 MB RAM).
- **[`tests/`](tests/)**: Automated unittest regression suite covering models, adapters, and store logic.

---

## 🤝 Community & Support

- **Want an employer added?** Check the region's `companies.md` (e.g. [regions/in/companies.md](regions/in/companies.md)) to see if it is already tracked. If missing, [open a Company Request issue](https://github.com/vishnunandan555/internscan/issues/new?title=%5BCompany+Request%5D+<Company+Name>).
- **Found an expired listing or bug?** [Open a Bug Report](https://github.com/vishnunandan555/internscan/issues/new?title=%5BBug%5D+<Issue+Description>).

---

## 📄 License

InternScan is open-source software licensed under the **[MIT License](LICENSE)**.
"""
    return content


def render(state: dict) -> None:
    """Render root README.md and all regional regions/{code}/jobs.md files atomically."""
    os.makedirs(REGIONS_DIR, exist_ok=True)
    jobs_list = list(state.get("jobs", {}).values())
    updated_iso = state.get("updated_at") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=NEW_BADGE_DAYS)).strftime("%Y-%m-%d")

    # 1. Render regions/{code}/jobs.md for each supported country
    for code in SUPPORTED_COUNTRIES:
        country_dir = os.path.join(REGIONS_DIR, code)
        os.makedirs(country_dir, exist_ok=True)
        jobs_content = _render_country_jobs_md(code, jobs_list, updated_iso, cutoff)
        target_path = os.path.join(country_dir, "jobs.md")
        tmp_path = target_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(jobs_content)
            os.replace(tmp_path, target_path)
        except Exception as exc:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            raise IOError(f"Failed to atomically render {target_path}: {exc}") from exc

    # 2. Render root README.md
    readme_content = _render_global_readme(state, cutoff)
    tmp_readme = README_PATH + ".tmp"
    try:
        with open(tmp_readme, "w", encoding="utf-8") as f:
            f.write(readme_content)
        os.replace(tmp_readme, README_PATH)
    except Exception as exc:
        if os.path.exists(tmp_readme):
            try:
                os.remove(tmp_readme)
            except OSError:
                pass
        raise IOError(f"Failed to atomically render {README_PATH}: {exc}") from exc
