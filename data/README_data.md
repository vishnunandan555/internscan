# 💾 Database Layer (`data/`)

The `data/` directory contains the persistent master databases and regional partitions for all tracked internships.

---

## Directory Layout

```
data/
├── jobs.json          # Master JSON database of all internships across all regions
├── jobs.json.gz       # Gzip-compressed snapshot for archival and fast loading
├── health.json        # Cumulative health status and scraper diagnostics
├── in/jobs.json       # Partitioned active database for India
├── us/jobs.json       # Partitioned active database for the United States
├── ca/jobs.json       # Partitioned active database for Canada
├── uk/jobs.json       # Partitioned active database for the United Kingdom
└── eu/jobs.json       # Partitioned active database for Europe
```

---

## Database Schema (`jobs.json`)

```json
{
  "updated_at": "2026-10-15T05:35:41Z",
  "jobs": {
    "nvidia:JR198231": {
      "uid": "nvidia:JR198231",
      "company": "NVIDIA",
      "external_id": "JR198231",
      "title": "Software Engineering Intern - Deep Learning",
      "url": "https://nvidia.wd5.myworkdayjobs.com/...",
      "locations": ["Bengaluru, India", "Pune, India"],
      "country": "in",
      "region": "APAC",
      "city_tag": "Bengaluru",
      "category": "AI/ML",
      "posted": "2026-10-12",
      "first_seen": "2026-10-12",
      "last_seen": "2026-10-15",
      "active": true
    }
  }
}
```

---

## Atomic Write Invariants

- Direct edits or un-atomic writes to `data/jobs.json` are **strictly forbidden**.
- All writes are managed exclusively by [`scraper/store.py`](../scraper/store.py).
- Writes commit to `.tmp` first, followed by POSIX atomic `os.replace` to eliminate any chance of corrupt records.
- Records are **never deleted**. Closed jobs retain their historical `first_seen` timestamps with `active: false` and a `closed` timestamp.
