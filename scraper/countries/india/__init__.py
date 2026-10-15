"""India country configuration module."""
from .companies import INDIA_COMPANIES, INDIA_FALLBACK
from .unsupported import INDIA_UNSUPPORTED

METADATA = {
    "code": "in",
    "name": "India",
    "flag": "🇮🇳",
    "currency": "INR",
    "timezone": "Asia/Kolkata",
    "hubs": [
        "Bengaluru",
        "Hyderabad",
        "Pune",
        "Delhi-NCR",
        "Chennai",
        "Mumbai",
        "Remote (India)",
    ],
}
