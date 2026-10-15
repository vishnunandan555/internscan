"""Modular country registry and aggregation engine."""
from typing import Dict, List, Optional
import os

from .shared import SHARED_COMPANIES, SHARED_FALLBACK
from .india import METADATA as IN_METADATA, INDIA_COMPANIES, INDIA_FALLBACK, INDIA_UNSUPPORTED
from .usa import METADATA as US_METADATA, US_COMPANIES, US_FALLBACK, US_UNSUPPORTED

SUPPORTED_COUNTRIES = ["in", "us", "ca", "uk", "eu"]

COUNTRY_METADATA: Dict[str, dict] = {
    "in": IN_METADATA,
    "us": US_METADATA,
    "ca": {
        "code": "ca",
        "name": "Canada",
        "flag": "🇨🇦",
        "currency": "CAD",
        "timezone": "America/Toronto",
        "hubs": ["Toronto", "Waterloo", "Vancouver", "Montreal", "Remote (Canada)"],
    },
    "uk": {
        "code": "uk",
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "currency": "GBP",
        "timezone": "Europe/London",
        "hubs": ["London", "Cambridge / Oxford", "Remote (UK)"],
    },
    "eu": {
        "code": "eu",
        "name": "Europe",
        "flag": "🇪🇺",
        "currency": "EUR",
        "timezone": "Europe/Berlin",
        "hubs": ["Berlin", "Munich", "Dublin", "Amsterdam", "Zurich", "Remote (EU)"],
    },
}

LOCAL_COMPANIES: Dict[str, List[dict]] = {
    "in": INDIA_COMPANIES,
    "us": US_COMPANIES,
    "ca": [],
    "uk": [],
    "eu": [],
}

LOCAL_FALLBACK: Dict[str, List[dict]] = {
    "in": INDIA_FALLBACK,
    "us": US_FALLBACK,
    "ca": [],
    "uk": [],
    "eu": [],
}

LOCAL_UNSUPPORTED: Dict[str, Dict[str, str]] = {
    "in": INDIA_UNSUPPORTED,
    "us": US_UNSUPPORTED,
    "ca": {},
    "uk": {},
    "eu": {},
}


def has_fallback_keys() -> bool:
    """Check if Google Jobs / SERP API fallback keys are configured."""
    return bool(os.environ.get("SERP_API_KEY") or os.environ.get("RAPIDAPI_KEY"))


def get_companies_for_country(country_code: str, include_fallback: Optional[bool] = None) -> List[dict]:
    """Return all active scraping target companies for a given country."""
    c_code = country_code.lower()
    if include_fallback is None:
        include_fallback = has_fallback_keys()

    companies = []
    # 1. Add shared global companies (they hire in all supported countries)
    companies.extend(SHARED_COMPANIES)

    # 2. Add local companies for this country
    if c_code in LOCAL_COMPANIES:
        companies.extend(LOCAL_COMPANIES[c_code])

    # 3. Add fallbacks if enabled
    if include_fallback:
        companies.extend(SHARED_FALLBACK)
        if c_code in LOCAL_FALLBACK:
            companies.extend(LOCAL_FALLBACK[c_code])

    # Deduplicate by company name while preserving order
    seen = set()
    deduped = []
    for c in companies:
        if c["name"] not in seen:
            seen.add(c["name"])
            deduped.append(c)

    return deduped


def get_unsupported_for_country(country_code: str) -> Dict[str, str]:
    """Return documented unsupported companies for a given country."""
    return LOCAL_UNSUPPORTED.get(country_code.lower(), {})
