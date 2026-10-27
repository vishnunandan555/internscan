"""Company registry for InternScan Tracker.

Modular country architecture:
- Shared Big Tech MNCs: scraper.countries.shared
- Country modules: scraper.countries.<country>
"""
import os
from typing import Any, Callable, List, Optional, TypedDict

from .countries import (
    COUNTRY_METADATA,
    SUPPORTED_COUNTRIES,
    get_companies_for_country,
    get_unsupported_for_country,
    has_fallback_keys,
)


class CompanyConfig(TypedDict, total=False):
    name: str
    fetch: Callable[..., List[Any]]
    host: str
    site: str
    search_text: str
    company: str
    token: str
    site_number: str
    job_url: str
    tenant: str
    org: str
    domain: str
    session: Any
    timeout: int
    scope: Any
    applied_facets: Any
    query: str
    subdomain: str
    portal: str


# Backward-compatible India direct and fallback registries
COMPANIES: List[CompanyConfig] = get_companies_for_country("in", include_fallback=False)  # type: ignore

_COMPANIES_NAMES = {c["name"] for c in COMPANIES}
FALLBACK_COMPANIES: List[CompanyConfig] = [  # type: ignore
    c for c in get_companies_for_country("in", include_fallback=True)
    if c["name"] not in _COMPANIES_NAMES
]

UNSUPPORTED = get_unsupported_for_country("in")


def get_companies(country: str = "in") -> List[CompanyConfig]:
    """Returns the active list of companies to scrape for a country (default: 'in').
    If SERP_API_KEY or RAPIDAPI_KEY is set, includes bot-protected fallbacks."""
    return get_companies_for_country(country)  # type: ignore


def get_all_known_companies(country: str = "in") -> List[CompanyConfig]:
    """Returns all configured companies for a country including direct ATS and bot-protected fallbacks."""
    return get_companies_for_country(country, include_fallback=True)  # type: ignore
