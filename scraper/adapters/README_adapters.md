# 🔌 ATS Adapters (`scraper/adapters/`)

The `scraper/adapters/` directory contains modular fetchers tailored to specific Applicant Tracking Systems (ATS) and custom enterprise career APIs.

---

## Adapter Directory

| Adapter | Target ATS / Company | Typical Configuration Parameters |
| :--- | :--- | :--- |
| [`workday.py`](workday.py) | **Workday CXS API** (NVIDIA, Walmart, HPE, Autodesk, AMD...) | `host`, `site`, `tenant`, `search_text` |
| [`greenhouse.py`](greenhouse.py) | **Greenhouse Job Boards** (Stripe, Figma, Databricks, Rubrik...) | `board` token, `query` |
| [`lever.py`](lever.py) | **Lever API** (Netflix, Spotify, Palantir...) | `site`, `query` |
| [`smartrecruiters.py`](smartrecruiters.py) | **SmartRecruiters** (Cisco, Snowflake, Visa...) | `company`, `query` |
| [`meta.py`](meta.py) | **Meta Careers GraphQL** | Unauthenticated Relay persisted query + LSD session + concurrent detail enrichment |
| [`google.py`](google.py) | **Google Careers API** | Direct internal JSON endpoint |
| [`amazon.py`](amazon.py) | **Amazon.jobs API** | Amazon public job search API |
| [`apple.py`](apple.py) | **Apple Careers API** | Apple post-search JSON endpoint |
| [`microsoft.py`](microsoft.py) | **Microsoft Careers API** | Microsoft internal query endpoint |
| [`eightfold.py`](eightfold.py) | **Eightfold AI** (Micron, PayPal...) | Domain endpoints with facet filtering |
| [`oracle_hcm.py`](oracle_hcm.py) | **Oracle Cloud HCM** | Enterprise REST recruitment services |
| [`phenom.py`](phenom.py) | **Phenom People** (Mastercard, Thermo Fisher...) | JSON feed endpoints |
| [`janestreet.py`](janestreet.py) | **Jane Street** | Public careers listing JSON |
| [`ashby.py`](ashby.py) | **Ashby HQ** | High-growth startup ATS API |
| [`github_careers.py`](github_careers.py) | **GitHub Careers** | GitHub jobs portal |
| [`bloomberg.py`](bloomberg.py) | **Bloomberg Careers** | Bloomberg careers query endpoint |
| [`qualcomm.py`](qualcomm.py) | **Qualcomm Workday Adapter** | Tailored Workday facet scraper |
| [`serp_jobs.py`](serp_jobs.py) | **Google Jobs Fallback** | Fallback indexer for bot-protected portals |

---

## How to Implement a New Adapter

All adapters must follow a consistent function signature:

```python
from ..models import Job

def fetch(cfg: dict) -> list[Job]:
    """Fetch active jobs from the target careers portal.
    
    Args:
        cfg: Dictionary containing company config (name, slug, host, board, etc.)
        
    Returns:
        List of un-filtered Job instances.
    """
    ...
```

### Guidelines for Adapter Authors:
1. **Produce Stable UIDs:** Use the ATS requisition number or external ID. Never generate random UUIDs.
2. **Extract Real Dates:** When available in the ATS payload, parse the employer's official `datePosted` or relative timestamp into `YYYY-MM-DD` format.
3. **Respect Rate Limits:** Always use `request_json` or include backoff jitter to prevent IP blocks.
