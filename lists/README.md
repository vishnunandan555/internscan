# 📋 Regional Company Lists (`lists/`)

The `lists/` directory contains auto-generated Markdown health reports documenting company tracking statuses for each region.

---

## File Map

| File | Region | Description |
| :--- | :--- | :--- |
| [`in.md`](in.md) | **India (65 companies)** | Active, fallback, and campus-only tracking statuses for India |
| [`us.md`](us.md) | **United States (54 companies)** | Silicon Valley and US nationwide employer statuses |
| [`ca.md`](ca.md) | **Canada (38 companies)** | Canadian tech employer tracking statuses |
| [`uk.md`](uk.md) | **United Kingdom (35 companies)** | London, Cambridge, Oxford, and UK employer statuses |
| [`eu.md`](eu.md) | **Europe (36 companies)** | European tech hub employer statuses |

---

## Automation Rule

These Markdown files are **auto-generated** by [`scraper/render_list.py`](../scraper/render_list.py) during the daily scrape pipeline.  
Do not hand-edit these files directly, as manual changes will be overwritten by the next automated run.
