# 🌍 Regional Directories (`regions/`)

The `regions/` directory contains localized Markdown trackers and employer coverage registries partitioned across our **5 supported regions**.

---

## Directory & File Map

Each regional directory contains two auto-generated, synchronized Markdown files:

| Region | Folder | `jobs.md` (Live Openings) | `companies.md` (Coverage & Health) |
| :--- | :--- | :--- | :--- |
| **India** | [`in/`](in/) | [🇮🇳 India Openings](in/jobs.md) | [Tracked Employers](in/companies.md) |
| **United States** | [`us/`](us/) | [🇺🇸 USA Openings](us/jobs.md) | [Tracked Employers](us/companies.md) |
| **Canada** | [`ca/`](ca/) | [🇨🇦 Canada Openings](ca/jobs.md) | [Tracked Employers](ca/companies.md) |
| **United Kingdom** | [`uk/`](uk/) | [🇬🇧 UK Openings](uk/jobs.md) | [Tracked Employers](uk/companies.md) |
| **Europe** | [`eu/`](eu/) | [🇪🇺 Europe Openings](eu/jobs.md) | [Tracked Employers](eu/companies.md) |

---

## Architecture & Generation Lifecycle

- **`jobs.md`** files are generated automatically by [`scraper/render_readme.py`](../scraper/render_readme.py). They contain verified active engineering internship postings grouped by employer with direct application links, tech hubs, category buckets, and `✨` newly added indicators.
- **`companies.md`** files are generated automatically by [`scraper/render_list.py`](../scraper/render_list.py). They document directly scraped ATS employers, bot-protected fallback adapters (Google Jobs / JSearch), and unsupported campus-only hiring policies with verified rationale.

> [!NOTE]
> All files in `regions/` are auto-generated on every 24-hour scrape cycle by GitHub Actions. Never hand-edit these files directly, as manual edits will be overwritten during the next synchronization run.
