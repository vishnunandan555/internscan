# 🇮🇳 India Regional Scraper Module (`scraper/countries/india/`)

This directory houses company configurations and metadata specific to engineering internship tracking in **India**.

---

## 1. Directory Structure

```
scraper/countries/india/
├── __init__.py         # Package initialization
├── companies.py        # India-specific company configurations and overrides
├── unsupported.py      # Registry of India companies with un-scrapable portals & reasons
└── README.md           # Documentation for the India regional scraper
```

---

## 2. Responsibilities

- **Company Definitions (`companies.py`):**
  Defines company records targeting India, specifying ATS adapter configurations, tech hub locations (Bengaluru, Hyderabad, Pune, Delhi NCR, Mumbai, etc.), and custom career endpoints.
- **Unsupported Companies (`unsupported.py`):**
  Catalogs companies with Indian operations that cannot currently be scraped automatically (e.g. campus-only hiring, heavy CAPTCHA, or authenticated portals like iCIMS/Workday login walls), along with architectural justifications.

---

## 3. Adding an Indian Company

To add a new company operating in India:
1. Ensure the company has verified tech/software internships in India.
2. Edit `scraper/countries/india/companies.py` to register the adapter configuration.
3. Test using CLI dry-run:
   ```bash
   python3 -m scraper.main -c <company_slug> --dry-run
   ```
