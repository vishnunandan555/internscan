# 🇺🇸 United States Regional Scraper Module (`scraper/countries/usa/`)

This directory houses company configurations and metadata specific to engineering internship tracking in the **United States**.

---

## 1. Directory Structure

```
scraper/countries/usa/
├── __init__.py         # Package initialization
├── companies.py        # USA-specific company configurations and overrides
├── unsupported.py      # Registry of US companies with un-scrapable portals & reasons
└── README_usa.md       # Documentation for the USA regional scraper
```

---

## 2. Responsibilities

- **Company Definitions (`companies.py`):**
  Defines US-specific company records, targeting software engineering, data science, and hardware internship roles across major US tech hubs (Silicon Valley, Seattle, New York, Austin, Boston, etc.).
- **Unsupported Companies (`unsupported.py`):**
  Documents US employers whose early-career portals use anti-bot defenses, non-public career backends, or invitation-only hiring pipelines.

---

## 3. Adding a US Company

To add a new company operating in the United States:
1. Edit `scraper/countries/usa/companies.py` with the appropriate ATS adapter and parameters.
2. Verify that `country="us"` is designated in the configuration.
3. Test using CLI dry-run:
   ```bash
   python3 -m scraper.main -c <company_slug> --dry-run
   ```
