# 🤖 AGENTS.md — AI Agent & Developer Guidelines

> **Repository:** InternScan India (`vishnunandan555/internscan`)  
> **Release Version:** `2.0.0`  
> **Purpose:** High-speed automated directory, public REST/RSS APIs, and Telegram alert bot for verified tech & software engineering internships across top tech employers in India.

---

## 1. Project Architecture & File Map

```
internscan/
├── scraper/                   # Python core scraper & synchronization engine
│   ├── main.py                # Concurrent ThreadPool orchestrator (CLI entrypoint)
│   ├── store.py               # Atomic database persistence & diff merge (added, closed, reopened)
│   ├── models.py              # Shared Job dataclass (generates stable UID "{slug}:{external_id}")
│   ├── companies.py           # Master registry of 59+ supported companies & adapters
│   ├── adapters/              # Modular ATS fetchers (18 custom crawler engines)
│   ├── countries/             # Multi-country regional modules (India, USA, etc.)
│   ├── categories.py          # Engineering domain classifier (Software, AI/ML, Data, Silicon...)
│   ├── regions.py             # India location filter & Tech Hub tagger (BLR, HYD, DEL, PUN, BOM...)
│   ├── api.py                 # Public REST API & RSS 2.0 generator (outputs to docs/api/)
│   ├── telegram.py            # Telegram push notification dispatcher (HTML mode)
│   ├── render_readme.py       # Auto-generator for README.md tables
│   └── render_list.py         # Auto-generator for LIST.md company health
├── bot/                       # Dedicated lightweight Telegram Bot (< 35 MB RAM)
│   ├── main.py                # Polling daemon & interactive slash commands (/latest, /status)
│   ├── requirements.txt       # Minimal dependencies (python-dotenv only)
│   ├── .env.example           # Environment template (BOT_TOKEN, CHAT_ID, POLL_INTERVAL)
│   └── internscan-bot.service # Linux systemd unit for 24/7 background operation
├── docs/                      # Production web application (GitHub Pages root)
│   ├── index.html             # High-speed static web app with Integrations & APIs section
│   ├── css/style.css          # Design system, dark/light theme, glassmorphism
│   ├── js/app.js              # Client state, fuzzy search, filters, saved roles
│   ├── api/                   # Public REST developer endpoints
│   ├── in/, us/, ca/, uk/, eu/# Localized country-specific portals
│   ├── feed.xml               # Standard RSS 2.0 feed
│   └── jobs.json              # Direct replica of database for client-side loading
├── data/
│   ├── jobs.json              # Master JSON database of all internships
│   ├── health.json            # Cumulative scraper health status
│   └── in/, us/, ca/, uk/, eu/# Region-partitioned job databases
├── lists/                     # Auto-generated regional company health markdown files
├── scripts/                   # Auxiliary CLI tooling (download_logos.py, generate_og_image.py)
├── logs/                      # Execution trace logs and scrape summaries
├── tests/                     # Unit test suite (unittest)
├── ARCHITECTURE.md            # Comprehensive end-to-end system architecture
├── CONTRIBUTING.md            # Developer contribution guidelines & ATS onboarding
├── SECURITY.md                # Vulnerability disclosure & ethical crawling policy
├── GUIDE.md                   # Complete developer handbook & CLI manual
└── .github/workflows/
    ├── update.yml             # Daily 03:00 AM IST scrape & auto-commit pipeline
    └── scraper-doctor.yml     # Nightly diagnostics runner
```

---

## 2. Inviolable Core Invariants (Do Not Break)

1. **Jobs are NEVER deleted:**
   - When a job posting disappears from a careers portal, it is marked `active: false` and timestamped with `closed = today`.
   - Never remove records from `data/jobs.json`. This guarantees `first_seen` survives posting flapping on and off.
2. **Atomic Writes Only:**
   - Any write to `data/jobs.json`, `README.md`, or `seen_jobs.json` must write to a temporary file (`.tmp`) and use `os.replace` to guarantee POSIX atomic commits without data corruption.
3. **Strict Memory Budget (< 35 MB RAM):**
   - Both `bot/` and `scraper/` run on minimal cloud nodes (e.g. 256 MB RAM VPS).
   - **Never import heavy libraries** such as `pandas`, `selenium`, `playwright`, or heavy web frameworks.
   - Use standard library `urllib` or minimal HTTP libraries.
4. **Stable Unique Identifiers (UIDs):**
   - Every `Job` object must produce a stable `uid = "{company_slug}:{external_id}"`.
   - Never use random hashes or volatile URLs as the primary ID if the ATS provides a requisition/job number.
5. **Verified Region Filtering:**
   - Only engineering jobs located in India or designated Remote (India) must be included.
   - Categorization must match one of the predefined engineering buckets in `scraper/categories.py`.

---

## 3. Standard Commands & Workflows

### Run the Test Suite
Always run the full test suite before committing changes:
```bash
python3 -m unittest discover -s tests
```

### Dry-Run Scrape a Company
Test scrapers without modifying database or production markdown files:
```bash
python3 -m scraper.main -c google --dry-run
python3 -m scraper.main -c "qualcomm,nvidia" --dry-run
```

### Check Version
```bash
python3 -m scraper.main --version
# Outputs: InternScan India v2.0.0
```

### Regenerate Public APIs & RSS
```bash
python3 -c "from scraper import store, api; api.generate_apis(store.load())"
```

### Regenerate README.md
```bash
python3 -c "from scraper import store, render_readme; render_readme.render(store.load())"
```

---

## 4. Coding & Design Standards

- **Python:** Python 3.10+ compatible, type hints on public helpers, clean exception handling.
- **Frontend / CSS:**
  - Pure Vanilla CSS tokens in `docs/css/style.css` (CSS custom properties `--brand`, `--bg`, `--surface`, `--ink`).
  - Do not introduce Tailwind or heavy CSS preprocessors.
  - Maintain dark/light mode parity and mobile responsive viewport standards.
- **Documentation:**
  - Preserve existing comments and docstrings.
  - When modifying APIs or bot commands, keep `README.md`, `GUIDE.md`, and `docs/index.html` in sync.
