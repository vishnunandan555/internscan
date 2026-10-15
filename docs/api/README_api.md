# 🌐 Public REST API Endpoints (`docs/api/`)

This directory contains static, zero-latency REST API endpoints served via GitHub Pages for public integration.

---

## 1. Endpoints

| Endpoint | Format | Description |
|---|---|---|
| `latest.json` | JSON | Contains internships newly discovered or reopened during the most recent automated synchronization run. |
| `active.json` | JSON | Array of all currently verified, active engineering internships. |

---

## 2. API Characteristics

- **Host:** GitHub Pages CDN (`https://vishnunandan555.github.io/internscan/api/`)
- **Authentication:** None required (100% free and open).
- **CORS:** Enabled by default (accessible via browser `fetch` from any origin).
- **Update Frequency:** Re-generated on every scraper run (daily at 03:00 AM IST).
- **Regional Partitions:** Also available per region under `docs/in/api/`, `docs/us/api/`, `docs/uk/api/`, etc.
