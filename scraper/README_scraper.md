# ⚙️ Scraper Engine (`scraper/`)

The `scraper/` directory houses the core synchronization pipeline, company registries, classification engines, and output generators that power InternScan.

---

## Architecture & Module Map

```text
scraper/
├── main.py            # CLI entrypoint & concurrent ThreadPool orchestrator
├── store.py           # Atomic JSON persistence & three-way diff engine (added, closed, reopened)
├── models.py          # Job dataclass with stable UID generation ({slug}:{external_id})
├── categories.py      # Engineering domain classifier (Software, AI/ML, Data, Silicon...)
├── regions.py         # Multi-country geolocation classifier & tech hub tagger
├── companies.py       # Master registry and lookup across all supported employers
├── http.py            # Resilient HTTP client with retry logic, backoff, and standard User-Agent
├── logger.py          # Structured logging facility (writes to logs/ history & summaries)
├── display.py         # ANSI terminal formatting, color helpers, and progress spinners
├── detector.py        # Automatic ATS detector for new or unmapped company careers portals
├── api.py             # Public REST developer endpoints & RSS 2.0 feed generator
├── telegram.py        # Telegram push notification dispatcher (HTML formatted cards)
├── render_readme.py   # Atomic root README.md & regional jobs.md generator
├── render_list.py     # Atomic regional companies.md tracking status generator
├── adapters/          # Modular ATS fetchers (Workday, Greenhouse, Lever, Meta, Apple...)
└── countries/         # Regional company registries (India, USA, Canada, UK, Europe)
```

---

## Key Workflows

### 1. Concurrent Execution (`main.py`)

Runs multiple scraper threads in parallel (`ThreadPoolExecutor`) to fetch listings across 60+ employers in under 25 seconds:

```bash
# Run all scrapers across all regions
python3 -m scraper.main

# Scrape specific companies
python3 -m scraper.main -c "google,nvidia,meta"

# Test extraction without modifying databases (Dry Run)
python3 -m scraper.main -c meta --dry-run
```

### 2. Atomic Diff Merge (`store.py`)

Computes diffs between incoming scrape data and `data/jobs.json`:

- **New roles:** Assigned `first_seen = today`, `active = True`.
- **Closed roles:** Kept in database, marked `active = False`, `closed = today`.
- **Reopened roles:** Marked `active = True`, `reopened = today`, preserving historical `first_seen`.

### 3. Public API & Feed Generation (`api.py`)

After each sync, automatically produces:

- `docs/api/active.json` & `docs/<country>/api/active.json`
- `docs/api/latest.json` & `docs/<country>/api/latest.json`
- `docs/feed.xml` & `docs/<country>/feed.xml` (RSS 2.0)
- `docs/<country>/jobs.json` (Direct high-speed replica for client-side loading)
