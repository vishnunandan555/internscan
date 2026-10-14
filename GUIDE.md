# 🛠️ System Architecture & Developer Guide

Welcome to the complete technical guide for the **India Tech Internships Tracker**.

This document explains the internal architecture, scraper engine, CLI commands, ATS auto-detection, and how to add new companies or integrate external search APIs.

---

## 📑 Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Data Pipeline Flow](#2-data-pipeline-flow)
3. [CLI Reference & Commands](#3-cli-reference--commands)
4. [Smart ATS Auto-Detector](#4-smart-ats-auto-detector)
5. [How to Add a New Company](#5-how-to-add-a-new-company)
6. [Data Schema & Storage](#6-data-schema--storage)
7. [Categories & Location Filters](#7-categories--location-filters)
8. [Automated CI/CD (GitHub Actions)](#8-automated-cicd-github-actions)
9. [External API Fallback (Google Jobs / SerpApi)](#9-external-api-fallback-google-jobs--serpapi)
10. [Troubleshooting & FAQ](#10-troubleshooting--faq)
11. [Telegram Bot & Public API Integration](#11-telegram-bot--public-api-integration)

---

## 1. Architecture Overview

```
                          ┌────────────────────────┐
                          │   Official Career APIs │
                          │ (Greenhouse, Workday,  │
                          │  Lever, Eightfold...)  │
                          └───────────┬────────────┘
                                      │ (HTTP GET/POST)
                                      ▼
                          ┌────────────────────────┐
                          │  Concurrent Engine     │
                          │ (ThreadPoolExecutor)   │
                          │   scraper/main.py      │
                          └───────────┬────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
    ┌────────────────────┐                        ┌────────────────────┐
    │  Intern Filter     │                        │  Location Filter   │
    │ scraper/models.py  │                        │ scraper/regions.py │
    │ & categories.py    │                        │ (India Tech Hubs)  │
    └──────────┬─────────┘                        └──────────┬─────────┘
               └──────────────────────┬──────────────────────┘
                                      ▼
                          ┌────────────────────────┐
                          │   Diff & Merge Engine  │
                          │    scraper/store.py    │
                          └───────────┬────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│  data/jobs.json  │        │    README.md     │        │ docs/index.html  │
│ (Active Database)│        │ (Markdown Table) │        │ (Live Web UI)    │
└──────────────────┘        └──────────────────┘        └──────────────────┘
```

The system is designed with strict separation of concerns:
- **`scraper/adapters/`**: Lightweight adapters per ATS (Workday, Greenhouse, SmartRecruiters, Lever, Phenom, Oracle HCM, Eightfold, custom REST).
- **`scraper/http.py`**: Centralized HTTP client with browser User-Agents, automatic retries on 429/5xx, and adaptive backoff.
- **`scraper/models.py`**: Unified `Job` dataclass with automatic internship detection and date normalization.
- **`scraper/categories.py`**: Fast regex categorization (Software, AI/ML, Data, Hardware/Silicon, Security, Systems).
- **`scraper/regions.py`**: Strict India location classifier with city tagging (Bengaluru, Hyderabad, Pune, Delhi-NCR, Chennai, Mumbai).
- **`scraper/store.py`**: State management, deduplication, and diff engine (`added`, `closed`, `reopened`).
- **`scraper/display.py`**: ANSI color terminal dashboard with execution timings and diagnostics.
- **`docs/`**: Production web application portal (served via GitHub Pages):
  - **`docs/index.html`**: Clean semantic HTML markup, SEO metadata, controls dock, and accessible layout.
  - **`docs/css/style.css`**: Modern responsive styling, theme variables, glassmorphic UI, and mobile breakpoints.
  - **`docs/js/app.js`**: Frontend client logic: real-time search, multi-filter pipeline, saved jobs, and view mode toggling.
  - **`docs/jobs.json`**: Auto-synced active listings database consumed by the web app.

---

## 2. Data Pipeline Flow

1. **Fetch**: Each adapter queries the target company's public JSON REST endpoint.
2. **Filter Internships**: `looks_like_internship()` verifies role keywords (`intern`, `internship`, `co-op`, `grad intern`).
3. **Categorize**: Regex rules assign a domain category (`Software`, `Hardware/Silicon`, `Data`, etc.). Non-engineering roles (Sales, Marketing, HR) are excluded.
4. **Filter India**: Postings are tested against `is_india_job()`. Only jobs in Indian hubs or remote within India are kept.
5. **Diff & Upsert**:
   - New posting $\rightarrow$ tagged with `first_seen = today`, `active = true`.
   - Existing posting $\rightarrow$ updates `last_seen = today`.
   - Missing posting $\rightarrow$ flagged `active = false`, `closed = today`.
   - If only scraping a subset of companies, **all other companies' active jobs are preserved**.
6. **Publish**: Synchronizes `data/jobs.json`, `docs/jobs.json`, updates `data/health.json`, and renders `README.md`.

---

## 3. CLI Reference & Commands

The main entry point is `scraper.main`. It supports full concurrency, dry runs, and targeted filtering:

```bash
# Show CLI options and flags
python3 -m scraper.main --help
```

### Common Commands

#### 1. Preview listings without saving (Dry Run)
```bash
python3 -m scraper.main -c qualcomm --dry-run
```

#### 2. Scrape a single company
```bash
python3 -m scraper.main -c qualcomm
```

#### 3. Scrape multiple companies concurrently
```bash
python3 -m scraper.main -c "amd,phonepe,razorpay" --dry-run
```

#### 4. Filter by role keyword (e.g., Hardware, AI, 2027)
```bash
python3 -m scraper.main -k "hardware" --dry-run
python3 -m scraper.main -k "2027" --dry-run
```

#### 5. Run all 42 scrapers with custom thread pool
```bash
python3 -m scraper.main --workers 10
```

#### 6. List all configured scrapers & unsupported notes
```bash
python3 -m scraper.main --list
```

---

## 4. Smart ATS Auto-Detector

When researching a new company, you don't need to write custom scraper code if they use a standard ATS. Run the auto-detector:

```bash
python3 -m scraper.detector <careers_url> --scrape
```

### Examples:
```bash
# Inspect a Lever job board:
python3 -m scraper.detector https://jobs.lever.co/meesho --scrape

# Inspect a Greenhouse job board:
python3 -m scraper.detector https://boards.greenhouse.io/groww --scrape
```

The detector inspects HTTP redirects, HTML source, and script bundles to extract the company token and invoke the appropriate adapter immediately.

---

## 5. How to Add a New Company

To add an employer to the automated tracker:

1. **Find their ATS**: Look at their careers URL or inspect network requests via DevTools (`XHR/Fetch`).
2. **Open [`scraper/companies.py`](scraper/companies.py)**:
3. **Add an entry to `COMPANIES`**:

```python
# Example 1: Greenhouse company
{
    "name": "NewCompany",
    "fetch": greenhouse.fetch,
    "token": "newcompany_slug",
},

# Example 2: Lever company
{
    "name": "NewCompany",
    "fetch": lever.fetch,
    "site": "newcompany_slug",
},

# Example 3: SmartRecruiters company
{
    "name": "NewCompany",
    "fetch": smartrecruiters.fetch,
    "company": "COMPANY_SLUG",
},

# Example 4: Workday company
{
    "name": "NewCompany",
    "fetch": workday.fetch,
    "host": "newcompany.wd3.myworkdayjobs.com",
    "site": "NewCompanyCareers",
    "max_pages": 15,
},
```

4. **Verify your scraper**:
```bash
python3 -m scraper.main -c "NewCompany" --dry-run
```

---

## 6. Data Schema & Storage

### `data/jobs.json`
Stores the source-of-truth state for every discovered posting:
```json
{
  "updated_at": "2026-09-17T16:30:00Z",
  "jobs": {
    "qualcomm-446719785836": {
      "company": "Qualcomm",
      "external_id": "446719785836",
      "title": "Interim Engineering Intern_2027_SW",
      "url": "https://careers.qualcomm.com/careers/job/446719785836?domain=qualcomm.com",
      "locations": ["Hyderabad, India"],
      "city_tag": "Hyderabad",
      "category": "Software",
      "posted": "2026-09-15",
      "first_seen": "2026-09-17",
      "last_seen": "2026-09-17",
      "active": true
    }
  }
}
```

### `data/health.json`
Tracks scraper uptime and error diagnostics across runs:
```json
{
  "succeeded": ["AMD", "Google", "Microsoft", "Qualcomm", "..."],
  "failed": {
    "Apple": "HTTP 403 Forbidden"
  }
}
```

### `logs/` Execution Logs
Every scrape run generates logs committed directly into the repository:
- **`logs/scrape_full.log`**: Exhaustive technical log of the latest scrape. Includes exact timestamps, execution times per company, raw postings count, location filtering details, HTTP errors, and full stack traces.
- **`logs/scrape_summary.log`**: Concise, scannable summary of the latest scrape. Shows execution timestamp, overall success/failure count, active India listings, a clean list of newly discovered internships (with URLs and locations), and closed listings.
- **`logs/history.log`**: Append-only audit log tracking daily execution history over time:
  ```text
  [2026-09-17 00:00:00 UTC] OK: 40/42 | Active: 14 | +3 new, -0 closed | Runtime: 17.5s
  ```

---

## 7. Categories & Location Filters

- **Category Rules ([`scraper/categories.py`](scraper/categories.py))**:
  - `Software`: Full-stack, backend, frontend, web, mobile, apps.
  - `AI / ML`: Machine learning, deep learning, NLP, computer vision, data science.
  - `Data / Analytics`: Data engineering, analytics, business intelligence.
  - `Hardware / Silicon`: ASIC, FPGA, RTL, firmware, embedded, SoC, VLSI.
  - `Security`: Cybersecurity, infosec, application security.
  - `Systems / Infrastructure`: Cloud, DevOps, SRE, platform, distributed systems.
  - `QA / SDET`: Quality assurance, test automation, SDET.

- **India Location Rules ([`scraper/regions.py`](scraper/regions.py))**:
  - Hubs recognized: `Bengaluru`, `Hyderabad`, `Pune`, `Delhi-NCR`, `Chennai`, `Mumbai`, `Kolkata`, `Remote India`.
  - Non-India postings (USA, UK, Singapore, Europe) are excluded automatically.

---

## 8. Automated CI/CD (GitHub Actions)

The tracker runs completely autonomously via `.github/workflows/update.yml`:
- **Trigger**: Daily at 00:00 UTC (05:30 AM IST) via GitHub Actions `cron: '0 0 * * *'` + manual `workflow_dispatch` (with options for target company, keyword filter, workers, and dry runs).
- **Concurrency**: Parallel execution in GitHub's Linux runner (pip cached).
- **Auto-Commit**: If new internships are found or closed, the bot commits directly with:
  `Automated scrape: +X added, -Y closed [skip ci]`
- **Pages Sync**: The workflow deploys `docs/index.html` and `docs/jobs.json` directly to GitHub Pages.

---

## 9. External API Fallback (Google Jobs / SerpApi)

Certain employers (Flipkart, Atlassian, Uber, Zepto, Goldman Sachs) block unauthenticated scrapers with Cloudflare, Akamai, or require campus SSO credentials.

To discover jobs for these companies without scraping their bot-protected pages:
1. Export your API key:
   ```bash
   export SERP_API_KEY="your_serpapi_key_here"
   # or
   export RAPIDAPI_KEY="your_rapidapi_key_here"
   ```
2. Query using universal search:
   ```bash
   python3 -m scraper.main --search "Flipkart Software Engineer Intern India"
   ```
This queries Google Jobs via SerpApi, bypassing all CAPTCHAs, bot defenses, and SSO walls.

---

## 10. Troubleshooting & FAQ

### Q: A scraper is taking too long to finish.
**A**: Some enterprise Workday/Oracle instances list over 4,000 global jobs. We parameterized `max_pages` (default 15 for Workday, 10 for Oracle HCM). Ensure your company configuration has `max_pages` set.

### Q: How do I test my changes before making a PR?
**A**:
```bash
# 1. Compile test
python3 -m compileall scraper/

# 2. Dry-run test your target company
python3 -m scraper.main -c <company_name> --dry-run
```

### Q: Does running a single company erase other companies' jobs?
**A**: **No.** `scraper/store.py` only updates the company you ran. All other companies' active jobs remain untouched in `data/jobs.json`.

---

## 11. Telegram Bot & Public API Integration

InternTrack India provides automated notifications and public developer APIs.

- **Telegram Bot (`bot/`):** Lightweight (< 35 MB RAM) self-hostable bot with auto-broadcast and `/latest`, `/active`, `/status` commands. See **[bot/README.md](bot/README.md)**.
- **Developer REST APIs:** `api/latest.json` (daily new jobs) and `api/active.json` (all verified active jobs).
- **RSS 2.0 Feed:** `feed.xml` for zero-code bot integrations.
- **GitHub Actions Auto-Push:** Fork and set `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` secrets to broadcast automatically on each scrape.
