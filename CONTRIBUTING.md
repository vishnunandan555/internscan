# 🤝 Contributing to InternScan

Thank you for your interest in contributing to **InternScan**! Our mission is to provide students and engineers worldwide with a 100% verified, automated, and fluff-free directory of technical internships sourced directly from official careers portals.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone. Please be respectful, constructive, and collaborative in all issues, pull requests, and discussions.

---

## How You Can Contribute

1. **Add a Company:** Add a top tech employer or startup whose internships are not yet tracked.
2. **Fix or Enhance an Adapter:** Fix a broken scraper or enhance extraction (e.g. posting dates, multi-location hubs).
3. **Frontend & UX:** Improve search speed, accessibility, theme parity, or mobile responsiveness in `docs/`.
4. **Documentation:** Refine setup guides, API examples, or regional coverage notes.
5. **Report Bugs:** Open an issue with reproduction details if a scraper fails or returns ghost roles.

---

## Development Setup

InternScan is built entirely in **Python 3.10+** (standard library preferred) and **Vanilla HTML/CSS/JS** for ultra-lightweight performance.

### 1. Clone the Repository
```bash
git clone https://github.com/vishnunandan555/internscan.git
cd internscan
```

### 2. Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Test Suite
Always verify that unit tests pass before making any changes:
```bash
python3 -m unittest discover -s tests
```

### 4. Local Web Server
Preview the static web application locally:
```bash
python3 -m http.server 8080 --directory docs
```
Navigate to `http://localhost:8080` in your browser.

---

## Adding a New Company

### Step 1: Identify the ATS Platform
Determine the applicant tracking system used by the employer:
- **Workday:** Host pattern `*.myworkdayjobs.com` (e.g. NVIDIA, Walmart, HPE)
- **Greenhouse:** Board token (e.g. Stripe, Figma, Databricks)
- **Lever:** Site name (e.g. Netflix, Spotify)
- **SmartRecruiters:** Company identifier (e.g. Cisco, Snowflake)
- **Custom / Direct API:** Meta GraphQL, Google Careers API, Amazon Jobs API, Apple Careers, etc.

### Step 2: Register the Company
Open the relevant country registry under `scraper/countries/` (e.g. `india/companies.py` or `usa/companies.py`):
```python
{
    "name": "Acme Corp",
    "slug": "acme-corp",
    "fetch": greenhouse.fetch,
    "board": "acmecorp",
    "query": "intern",
}
```

### Step 3: Test with Dry-Run
Run a dry run to verify extraction without altering production databases:
```bash
python3 -m scraper.main -c acme-corp --dry-run
```
Inspect the output to confirm:
- Requisition IDs are stable.
- Roles match engineering categories (`Software`, `AI/ML`, `Data`, etc.).
- Regional locations are correctly parsed.

---

## Core Invariants to Respect

When submitting a pull request, ensure you follow these repository rules:
1. **Never delete jobs:** The synchronization engine marks unlisted postings as `active: false` with a `closed` timestamp. Records are never deleted to preserve `first_seen` history.
2. **Atomic Writes:** All database and markdown persistence must write to `.tmp` first and commit atomically via `os.replace`.
3. **Strict Memory Budget (< 35 MB RAM):** Avoid heavy dependencies (like `pandas`, `selenium`, `playwright`). Rely on standard library HTTP or lightweight minimal dependencies.
4. **Stable UIDs:** Unique identifiers must follow `{company_slug}:{external_id}`.

---

## Pull Request Guidelines

1. **Branch Naming:** Use clear branch names (e.g., `feat/add-uber-scraper`, `fix/meta-posted-date`).
2. **Commit Messages:** Follow conventional commits:
   - `feat: add Snowflake Canada scraper`
   - `fix: resolve Workday 30+ day timestamp parsing`
   - `docs: update API documentation`
3. **Tests Required:** Add or update tests in `tests/` for any new logic.
4. **Check Quality:** Run `python3 -m unittest discover -s tests` prior to opening your PR.

Thank you for helping empower students and engineers everywhere!
