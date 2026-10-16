# 💬 InternScan — Discussion Topics & Feature Roadmap

> **Repository:** [`vishnunandan555/internscan`](https://github.com/vishnunandan555/internscan)  
> **Status:** Release v2.0.0 Production Ready  
> **Last Updated:** October 2026  

This document outlines key technical discussion points, proposed enhancements, architectural decisions, and operational details for the InternScan ecosystem.

---

## 📌 Table of Contents
1. [Current Milestone Status](#1-current-milestone-status)
2. [Active Discussion Topics](#2-active-discussion-topics)
   - [A. Telegram Broadcast Automation](#a-telegram-broadcast-automation)
   - [B. Unsupported ATS Onboarding](#b-unsupported-ats-onboarding)
   - [C. PWA (Progressive Web App) Support](#c-pwa-progressive-web-app-support)
   - [D. Batch Graduation Year Filtering](#d-batch-graduation-year-filtering)
   - [E. Discord / Slack Webhook Integration](#e-discord--slack-webhook-integration)
3. [CI/CD & Automated Pipeline Guarantees](#3-cicd--automated-pipeline-guarantees)
4. [Contribution & Next Steps](#4-contribution--next-steps)

---

## 1. Current Milestone Status

- [x] **Full-Stack Scraper Core:** 18 custom ATS engines supporting 60+ employers with threadpool concurrency.
- [x] **Inviolable Data Invariants:** Atomic commits (`os.replace`), zero record deletions, and stable UIDs (`company_slug:external_id`).
- [x] **Multi-Region Support:** Dedicated localized hubs for India (`/in`), United States (`/us`), Canada (`/ca`), United Kingdom (`/uk`), and Europe (`/eu`).
- [x] **Developer Platform:** Free, CORS-enabled REST APIs (`/api/latest.json`, `/api/active.json`) and RSS 2.0 feeds (`feed.xml`).
- [x] **Mobile UI Overhaul:**
  - Zero horizontal overflow on viewports from 320px to 430px+.
  - Clean `36×36px` square icon buttons in navbar with no label clipping.
  - Symmetrical `2×2` metrics grid with uniform minimum heights.
  - Native iOS & Android touch feedback (`transform: scale(0.96)`).
  - iOS auto-zoom prevention via `16px` input sizing and `viewport-fit=cover`.
- [x] **CI/CD Reliability:** Dedicated CI test suite (`.github/workflows/ci.yml`) and daily scraper pipeline (`.github/workflows/update.yml`).

---

## 2. Active Discussion Topics

### A. Telegram Broadcast Automation
- **Context:** The scraper includes built-in Telegram HTML notification dispatching ([scraper/telegram.py](file:///home/vishnunandan555/Projects/interntrack-india/scraper/telegram.py)) and a dedicated background bot daemon ([bot/main.py](file:///home/vishnunandan555/Projects/interntrack-india/bot/main.py)).
- **Points to Discuss:**
  1. Do we want to create an official public broadcast channel (e.g., `@internscan_alerts`)?
  2. If so, configure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as GitHub Repository Secrets under **Settings → Secrets and variables → Actions**.
  3. Frequency: Should the bot alert immediately after every daily scrape (03:00 AM IST), or bundle multiple postings into a single digest?

### B. Unsupported ATS Onboarding
- **Context:** Certain high-profile companies (e.g., Zerodha, CRED, Dream11, Juspay, Postman) currently use custom JS-heavy career pages or third-party forms (Google Forms, Lever without open public APIs) and are categorized under `UNSUPPORTED` in [scraper/countries/india/unsupported.py](file:///home/vishnunandan555/Projects/interntrack-india/scraper/countries/india/unsupported.py).
- **Points to Discuss:**
  1. Evaluate lightweight headless API reverse-engineering for companies that expose internal REST or GraphQL endpoints (e.g., Greenhouse/Workable hidden APIs).
  2. Maintain strict adherence to the **< 35 MB RAM memory budget** rule (no heavy browser automation like Selenium/Playwright in production scrapers).
  3. Add community-submitted direct application URLs for recurring seasonal internship programs.

### C. PWA (Progressive Web App) Support
- **Context:** With the mobile UI optimization completed, users frequently access InternScan from mobile browsers.
- **Points to Discuss:**
  1. Add a `manifest.json` with icons (`icon.png`, `apple-touch-icon.png`) for "Add to Home Screen" support on iOS & Android.
  2. Implement a minimal, zero-dependency Service Worker for offline caching of previously fetched `jobs.json`.

### D. Batch Graduation Year Filtering
- **Context:** Internships frequently target specific graduating cohorts (e.g. `2026 Batch`, `2027 Batch`, `Pre-final Year`).
- **Points to Discuss:**
  1. Introduce an automated batch year extractor in [scraper/categories.py](file:///home/vishnunandan555/Projects/interntrack-india/scraper/categories.py) using regex matching on job titles (e.g. `\b202[6-8]\b`).
  2. Add quick filter pills on the web UI: `🎓 2026 Grad`, `🎓 2027 Grad`, `🎓 2028 Grad`.

### E. Discord / Slack Webhook Integration
- **Context:** Student developer communities, university clubs, and open-source groups often request automatic Discord/Slack notifications.
- **Points to Discuss:**
  1. Add optional `DISCORD_WEBHOOK_URL` and `SLACK_WEBHOOK_URL` support in [scraper/main.py](file:///home/vishnunandan555/Projects/interntrack-india/scraper/main.py) to post clean embedded cards.
  2. Document webhook setup instructions in [docs/docs/index.html](file:///home/vishnunandan555/Projects/interntrack-india/docs/docs/index.html).

---

## 3. CI/CD & Automated Pipeline Guarantees

The repository is guarded by 3 automated GitHub workflows:

| Workflow | Trigger | Primary Function |
| :--- | :--- | :--- |
| **`CI & Test Suite`** (`ci.yml`) | Every `push` & `pull_request` to `main` | Runs 30+ unit tests, validates store partitioning, models, typing annotations, API generation, and README generation. |
| **`Scrape & Update`** (`update.yml`) | Daily at `21:30 UTC` (`03:00 AM IST`) + manual dispatch | Concurrent multi-country crawler, updates database, regenerates markdown tables and REST APIs, commits with `[skip ci]`. |
| **`Scraper Doctor`** (`scraper-doctor.yml`) | Issue labeled `scraper-health` | AI self-healing diagnostic workflow for broken career endpoints. |

---

## 4. Contribution & Next Steps

If you have feedback, ideas, or wish to prioritize any of the above topics:
- Open a GitHub Issue with the `enhancement` or `discussion` label.
- Submit PRs following the guidelines in [CONTRIBUTING.md](file:///home/vishnunandan555/Projects/interntrack-india/CONTRIBUTING.md) and [AGENTS.md](file:///home/vishnunandan555/Projects/interntrack-india/AGENTS.md).
