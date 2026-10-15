# 🧪 Unit Test Suite (`tests/`)

The `tests/` directory contains unit tests verifying core invariants, data models, classifiers, and atomic database persistence.

---

## Test Directory

| File | Target Component | What It Tests |
| :--- | :--- | :--- |
| [`test_models.py`](test_models.py) | `scraper/models.py` | UID generation `{slug}:{external_id}`, location normalization, date parsing |
| [`test_categories.py`](test_categories.py) | `scraper/categories.py` | Domain classification (`Software`, `AI/ML`, `Hardware/Silicon`, `Data`...) |
| [`test_regions.py`](test_regions.py) | `scraper/regions.py` | Tech hub matching across India, US, Canada, UK, and Europe |
| [`test_companies.py`](test_companies.py) | `scraper/companies.py` | Company lookup, slug uniqueness, and adapter mappings |
| [`test_country_modules.py`](test_country_modules.py) | `scraper/countries/` | Multi-country registry integrity and shared company inheritance |
| [`test_store.py`](test_store.py) | `scraper/store.py` | Atomic commits, non-destructive diff engine, and closed job retention |
| [`test_api.py`](test_api.py) | `scraper/api.py` | Public REST API generation (`active.json`, `latest.json`) and RSS feed validation |
| [`test_telegram.py`](test_telegram.py) | `scraper/telegram.py` | HTML message formatting and escaping |

---

## Running the Tests

Execute the full suite using Python's standard `unittest` runner:

```bash
python3 -m unittest discover -s tests
```

To run an individual test module:

```bash
python3 -m unittest tests/test_models.py
```
