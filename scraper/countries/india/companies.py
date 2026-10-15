"""India-specific company registry (unicorns, domestic product leaders, GCCs)."""
from ...adapters import greenhouse, lever, smartrecruiters, workday, serp_jobs

INDIA_COMPANIES = [
    {"name": "PhonePe", "fetch": smartrecruiters.fetch, "company": "PHONEPELIMITED", "scope": ["in"]},
    {"name": "Razorpay", "fetch": greenhouse.fetch, "token": "razorpaysoftwareprivatelimited", "scope": ["in"]},
    {"name": "Freshworks", "fetch": smartrecruiters.fetch, "company": "freshworks", "scope": ["in"]},
    {"name": "Swiggy", "fetch": smartrecruiters.fetch, "company": "swiggy", "scope": ["in"]},
    {"name": "Meesho", "fetch": lever.fetch, "site": "meesho", "scope": ["in"]},
    {"name": "CRED", "fetch": lever.fetch, "site": "cred", "scope": ["in"]},
    {"name": "Groww", "fetch": greenhouse.fetch, "token": "groww", "scope": ["in"]},
    {"name": "Zeta", "fetch": lever.fetch, "site": "zeta", "scope": ["in"]},
    {"name": "InMobi", "fetch": greenhouse.fetch, "token": "inmobi", "scope": ["in"]},
    {"name": "Zomato", "fetch": smartrecruiters.fetch, "company": "Zomato1", "scope": ["in"]},
    {"name": "Target", "fetch": workday.fetch,
     "host": "target.wd5.myworkdayjobs.com", "site": "targetcareers",
     "search_text": "",
     "applied_facets": {"Location_Country": ["c4f78be1a8f14da0ab49ce1162348a5e"]},
     "scope": ["in"]},
]

INDIA_FALLBACK = [
    {"name": "Flipkart", "fetch": serp_jobs.fetch, "query": "Flipkart software engineer intern India", "scope": ["in"]},
]
