# 🌍 Country Registries (`scraper/countries/`)

The `scraper/countries/` package manages regional company configurations, target locations, and localized adapter settings.

---

## Structure

```
scraper/countries/
├── __init__.py        # Multi-country registry loader & registry aggregation
├── shared.py          # Shared multi-national tech employers (Amazon, Google, Meta, Apple...)
├── india/             # India-specific companies and GCCs
│   ├── __init__.py
│   └── companies.py   # Master registry of 60+ Indian tech employers
└── usa/               # US-specific company definitions & Silicon Valley tech firms
    ├── __init__.py
    └── companies.py   # Registry of US engineering employers
```

---

## Adding a New Country Registry

To add support for a new country:
1. Define the ISO country code in `scraper/regions.py` under `SUPPORTED_COUNTRIES`.
2. Add tech hub keyword patterns to `HUB_PATTERNS` in `scraper/regions.py`.
3. Create a new folder under `scraper/countries/<country_code>/` with a `companies.py` registry.
4. Export the company dictionary in `scraper/countries/__init__.py`.
