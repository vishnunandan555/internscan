"""United States country configuration module."""
from .companies import US_COMPANIES, US_FALLBACK
from .unsupported import US_UNSUPPORTED

METADATA = {
    "code": "us",
    "name": "United States",
    "flag": "🇺🇸",
    "currency": "USD",
    "timezone": "America/New_York",
    "hubs": [
        "SF Bay Area",
        "Seattle",
        "New York",
        "Austin",
        "Boston",
        "Remote (US)",
    ],
}
