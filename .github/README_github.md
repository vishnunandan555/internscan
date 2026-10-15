# 🤖 GitHub Workflows & Automation (`.github/`)

The `.github/` directory configures continuous integration, automated daily scraping pipelines, and repository health diagnostics.

---

## Workflow Directory

| Workflow | File | Trigger Schedule | What It Does |
| :--- | :--- | :--- | :--- |
| **Daily Scrape & Auto-Commit** | [`.github/workflows/update.yml`](workflows/update.yml) | Daily at `03:00 AM IST` (`21:30 UTC`) & manual dispatch | Runs the full scraper across all regions, merges diffs, generates APIs, updates `README.md`, and commits changes atomically. |
| **Scraper Doctor** | [`.github/workflows/scraper-doctor.yml`](workflows/scraper-doctor.yml) | Weekly on Sunday & manual dispatch | Runs automated health diagnostics against all company adapters to detect rotated GraphQL IDs or broken career endpoints. |

---

## Secrets & Environment Variables

- `BOT_TOKEN` *(Optional):* Telegram bot token for instant push notifications on newly dropped internships.
- `CHAT_ID` *(Optional):* Target Telegram channel or group ID.
- `SERP_API_KEY` / `RAPIDAPI_KEY` *(Optional):* Used only for Google Jobs fallback adapters when an ATS blocks direct scraping.
