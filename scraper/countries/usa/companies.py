"""United States specific company registry."""
from ...adapters import greenhouse, lever, workday

US_COMPANIES = [
    {"name": "Roblox", "fetch": greenhouse.fetch, "token": "roblox", "scope": ["us"]},
    {"name": "DoorDash", "fetch": greenhouse.fetch, "token": "doordash", "scope": ["us"]},
    {"name": "Duolingo", "fetch": greenhouse.fetch, "token": "duolingo", "scope": ["us"]},
    {"name": "Samsara", "fetch": greenhouse.fetch, "token": "samsara", "scope": ["us"]},
    {"name": "Palantir", "fetch": lever.fetch, "site": "palantir", "scope": ["us"]},
]

US_FALLBACK = []
