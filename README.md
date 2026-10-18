<a id="top"></a>
<p align="center">
  <a href="https://internscan.vercel.app/">
    <img src="docs/icon.png" width="96" height="96" alt="InternScan Logo">
  </a>
</p>
<h1 align="center">InternScan — The Global Directory for Tech Internships</h1>

<p align="center">
  <strong>Automated, open-source directory of verified engineering, AI/ML, and tech internships across top employers worldwide. 100% open source and direct.</strong>
</p>

<p align="center">
  <a href="https://internscan.vercel.app/"><img src="https://img.shields.io/badge/Live_Dashboard-Explore_All_Regions-6366f1?style=for-the-badge&logo=globe&logoColor=white" alt="Live Dashboard"></a>
  <a href="#-regional-internship-trackers"><img src="https://img.shields.io/badge/Verified_Roles-503_Active-10b981?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Active Roles"></a>
  <a href="#-regional-internship-trackers"><img src="https://img.shields.io/badge/Tracked_Employers-65+_Global-2563eb?style=for-the-badge&logo=airplay&logoColor=white" alt="Tracked Employers"></a>
  <a href="#-regional-internship-trackers"><img src="https://img.shields.io/badge/Supported_Regions-5_Countries-f59e0b?style=for-the-badge&logo=target&logoColor=white" alt="Supported Regions"></a>
  <a href="https://github.com/vishnunandan555/internscan/actions/workflows/update.yml"><img src="https://img.shields.io/badge/Sync_Cadence-Daily_03:00_IST-0ea5e9?style=for-the-badge&logo=githubactions&logoColor=white" alt="Sync Cadence"></a>
  <a href="ARCHITECTURE.md"><img src="https://img.shields.io/badge/Architecture-System_Design-8b5cf6?style=for-the-badge&logo=diagram-next&logoColor=white" alt="Architecture"></a>
  <a href="bot/README_bot.md"><img src="https://img.shields.io/badge/Telegram_Bot-Deploy_in_3_mins-0088cc?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Bot"></a>
  <a href="https://internscan.vercel.app/api/active.json"><img src="https://img.shields.io/badge/Public_API-REST_&_RSS-ec4899?style=for-the-badge&logo=fastapi&logoColor=white" alt="Public API"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/Contributing-Join_Us-14b8a6?style=for-the-badge&logo=github&logoColor=white" alt="Contributing"></a>
</p>

> 🕐 Last synchronized: **2026-10-19 04:57:24 IST** · 📌 **503** active verified tech internships worldwide across **5** supported regions.

---

## 🌍 Regional Internship Trackers

InternScan partitions verified listings into dedicated regional portals. Each region features its own Markdown job tracker, company coverage registry, and high-speed web application:

| Region | Flag | Active Roles | Markdown Job Directory | Tracked Employers | Live Web Portal |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **India** | 🇮🇳 | **15** | [🇮🇳 **View India Jobs**](regions/in/jobs.md) | [Tracked Companies](regions/in/companies.md) | [Open India Dashboard](https://internscan.vercel.app/in/) |
| **United States** | 🇺🇸 | **298** | [🇺🇸 **View US Jobs**](regions/us/jobs.md) | [Tracked Companies](regions/us/companies.md) | [Open US Dashboard](https://internscan.vercel.app/us/) |
| **Canada** | 🇨🇦 | **51** | [🇨🇦 **View Canada Jobs**](regions/ca/jobs.md) | [Tracked Companies](regions/ca/companies.md) | [Open Canada Dashboard](https://internscan.vercel.app/ca/) |
| **United Kingdom** | 🇬🇧 | **27** | [🇬🇧 **View UK Jobs**](regions/uk/jobs.md) | [Tracked Companies](regions/uk/companies.md) | [Open UK Dashboard](https://internscan.vercel.app/uk/) |
| **Europe** | 🇪🇺 | **111** | [🇪🇺 **View Europe Jobs**](regions/eu/jobs.md) | [Tracked Companies](regions/eu/companies.md) | [Open Europe Dashboard](https://internscan.vercel.app/eu/) |

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
| `https://internscan.vercel.app/api/active.json` | `GET` | JSON | All currently active verified internships worldwide. |
| `https://internscan.vercel.app/api/latest.json` | `GET` | JSON | New and reopened internships discovered in today's scrape. |
| `https://internscan.vercel.app/feed.xml` | `GET` | RSS 2.0 | Standard RSS feed for Slack, Discord webhooks, or Feed readers. |
| `https://internscan.vercel.app/metrics.json` | `GET` | JSON | Scraper health, platform metrics, and country breakdowns. |
| `https://internscan.vercel.app/{region}/api/active.json` | `GET` | JSON | Regional active postings (`in`, `us`, `ca`, `uk`, `eu`). |

```python
# Quick Python Example
import requests

data = requests.get("https://internscan.vercel.app/api/active.json").json()
print(f"Total active global roles: {data['total_active']}")
for job in data.get("jobs", [])[:5]:
    print(f"• [{job['country'].upper()}] {job['company']}: {job['title']} ({job['city_tag']})")
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
| **[DISCUSSIONS.md](DISCUSSIONS.md)** | Technical roadmap, feature RFCs, and architecture discussions |

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
