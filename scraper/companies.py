"""Company registry for India Tech Internships Tracker.

Every entry: display name + adapter fetch function + adapter config.
Focuses on FAANG, top global MNC tech centers in India, and top Indian product startups/unicorns.
"""
from typing import Any, Callable, List, Optional, TypedDict

from .adapters import (
    amazon,
    amd,
    apple,
    bloomberg,
    eightfold,
    github_careers,
    google,
    greenhouse,
    janestreet,
    lever,
    meta,
    microsoft,
    oracle_hcm,
    phenom,
    qualcomm,
    smartrecruiters,
    workday,
)

# Companies we can't scrape via public JSON APIs, and why.
UNSUPPORTED = {
    # Tier A
    "Atlassian": "careers site uses iCIMS iframe portal without public search API; student hiring routed via campus and early-career portal",
    # Tier B
    "BrowserStack": "uses closed ATS without public search API; routes student hiring via campus & aggregators",
    "Chargebee": "uses closed ATS without public search API; routes student hiring via campus & aggregators",
    "Dream11": "uses Dream Sports proprietary careers portal without public search API",
    "Flipkart": "careers site sits behind enterprise bot defense and routes student hiring via campus visits & Flipkart GRiD",
    "Juspay": "no external ATS; hires student interns exclusively via campus challenges (Unstop/HackerEarth) and direct email",
    "Myntra": "careers portal (jobs.myntra.com) is a compiled Flutter web application without public search API; hires via campus & HackerRamp",
    "Nykaa": "careers portal sits behind bot protection returning 403; internal Darwinbox portal lacks public candidate search REST API",
    "Postman": "retired public Greenhouse board; careers site runs custom Next.js frontend without public search API",
    "Zepto": "uses TalentRecruit proprietary portal without public search API; hires via campus & portal forms",
    "Zerodha": "no external ATS; engineering openings posted ad-hoc via static page (zerodha.com/careers) and email",
    "Zoho": "uses Zoho Recruit proprietary portal without public job search API",
    # Tier C
    "Arm": "early careers portal (earlycareers-arm.icims.com) requires authenticated candidate login",
    "ASML": "has no software engineering/R&D center in India (field service only in Gujarat); portal is custom Next.js without public CXS API",
    "HashiCorp": "acquired by IBM; public Greenhouse board retired, jobs folded into IBM internal recruitment portal",
    "HP": "careers portal sits behind Cloudflare bot protection returning 403 to non-browser clients",
    "Intuit": "careers portal sits behind Radancy search without open public REST API",
    "SAP": "SuccessFactors career site requires authenticated recruiter operators; no public search API",
    "Siemens": "careers site runs on Avature global portal without public JSON search API; requires interactive session",
    "Faveo": "careers site runs on Zoho Recruit India portal without open unauthenticated REST API",
    "Uber": "careers search API sits behind Cloudflare bot protection returning 403 to non-browser clients; needs headless browser",
    # Tier D
    "American Express": "careers site sits behind Akamai bot defense returning 403 to automated clients",
    "D. E. Shaw": "campus-only hiring program for Indian engineering colleges (IIT/BITS/NIT)",
    "Deloitte": "South Asia career portal runs on closed SAP SuccessFactors infrastructure; routes graduate hiring via campus",
    "Goldman Sachs": "campus & internship portal (tal.net) requires interactive SSO / browser session",
    "HSBC": "careers site (mycareer.hsbc.com) runs on Avature CRM without open unauthenticated REST search API",
    "Infosys": "student tech hiring conducted exclusively through InfyTQ / Springboard campus portal",
    "Tata Consultancy Services": "student tech hiring conducted exclusively through TCS NextStep / National Qualifier Test (NQT) campus portal",
    # Other Notable
    "ByteDance": "job-search API rejects requests without browser client signature; needs headless browser",
    "LinkedIn": "careers site only links to linkedin.com/jobs, which is authwalled and prohibits automated scraping",
    "Target": "careers site uses Radancy custom portal; student tech hiring for Target India (Manyata Tech Park, Bengaluru) is routed via campus drives & target.com/careers/students",
    "Tesla": "careers site sits behind Akamai bot protection returning 403 to non-browser clients",
    "Spotify": "limited tech/engineering presence in India; student hiring primarily US/EU/UK",
}

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


COMPANIES: List[CompanyConfig] = [
    # --- Tier A: Major Product / Big Tech ------------------------------------
    {"name": "Google", "fetch": google.fetch},
    {"name": "Microsoft", "fetch": microsoft.fetch},
    {"name": "Amazon", "fetch": amazon.fetch},
    {"name": "Apple", "fetch": apple.fetch},
    {"name": "Adobe", "fetch": workday.fetch,
     "host": "adobe.wd5.myworkdayjobs.com", "site": "external_experienced"},
    {"name": "Salesforce", "fetch": workday.fetch,
     "host": "salesforce.wd12.myworkdayjobs.com", "site": "External_Career_Site",
     "search_text": "internship"},
    {"name": "Oracle", "fetch": oracle_hcm.fetch},
    {"name": "NVIDIA", "fetch": workday.fetch,
     "host": "nvidia.wd5.myworkdayjobs.com", "site": "NVIDIAExternalCareerSite"},
    {"name": "Qualcomm", "fetch": qualcomm.fetch},
    {"name": "Meta", "fetch": meta.fetch},
    {"name": "Netflix", "fetch": eightfold.fetch,
     "host": "explore.jobs.netflix.net", "domain": "netflix.com"},

    # --- Tier B: Strong Product / Indian Tech Unicorns -----------------------
    {"name": "PhonePe", "fetch": smartrecruiters.fetch, "company": "PHONEPELIMITED"},
    {"name": "Razorpay", "fetch": greenhouse.fetch, "token": "razorpaysoftwareprivatelimited"},
    {"name": "Freshworks", "fetch": smartrecruiters.fetch, "company": "freshworks"},
    {"name": "Swiggy", "fetch": smartrecruiters.fetch, "company": "swiggy"},
    {"name": "Meesho", "fetch": lever.fetch, "site": "meesho"},
    {"name": "CRED", "fetch": lever.fetch, "site": "cred"},
    {"name": "Groww", "fetch": greenhouse.fetch, "token": "groww"},
    {"name": "Zeta", "fetch": lever.fetch, "site": "zeta"},
    {"name": "InMobi", "fetch": greenhouse.fetch, "token": "inmobi"},
    {"name": "Zomato", "fetch": smartrecruiters.fetch, "company": "Zomato1"},

    # --- Tier C: Global Tech MNCs & India Engineering Centers / GCCs --------
    {"name": "Walmart Global Tech", "fetch": workday.fetch,
     "host": "walmart.wd504.myworkdayjobs.com", "site": "WalmartExternal"},
    {"name": "Dell Technologies", "fetch": oracle_hcm.fetch,
     "host": "enterpriseplatform.dell.com", "site_number": "CX_1",
     "job_url": "https://enterpriseplatform.dell.com/hcmUI/CandidateExperience/en/sites/CX_1/job/{id}"},
    {"name": "Cisco", "fetch": phenom.fetch, "host": "careers.cisco.com",
     "job_url": "https://careers.cisco.com/global/en/job/{id}"},
    {"name": "Intel", "fetch": workday.fetch,
     "host": "intel.wd1.myworkdayjobs.com", "site": "External"},
    {"name": "AMD", "fetch": amd.fetch},
    {"name": "Red Hat", "fetch": workday.fetch,
     "host": "redhat.wd5.myworkdayjobs.com", "site": "Jobs"},
    {"name": "HPE", "fetch": phenom.fetch, "host": "careers.hpe.com",
     "job_url": "https://careers.hpe.com/us/en/job/{id}"},
    {"name": "Broadcom (VMware)", "fetch": workday.fetch,
     "host": "broadcom.wd1.myworkdayjobs.com", "site": "External_Career"},
    {"name": "PayPal", "fetch": workday.fetch,
     "host": "paypal.wd1.myworkdayjobs.com", "site": "jobs"},
    {"name": "ServiceNow", "fetch": smartrecruiters.fetch, "company": "servicenow"},
    {"name": "CrowdStrike", "fetch": workday.fetch,
     "host": "crowdstrike.wd5.myworkdayjobs.com", "site": "crowdstrikecareers"},
    {"name": "Palo Alto Networks", "fetch": workday.fetch,
     "host": "paloaltonetworks.wd5.myworkdayjobs.com", "site": "panwexternalcareers"},
    {"name": "Workday", "fetch": workday.fetch,
     "host": "workday.wd5.myworkdayjobs.com", "site": "Workday"},
    {"name": "Micron", "fetch": workday.fetch,
     "host": "micron.wd1.myworkdayjobs.com", "site": "External"},
    {"name": "Nokia", "fetch": oracle_hcm.fetch,
     "host": "fa-evmr-saasfaprod1.fa.ocs.oraclecloud.com", "site_number": "CX_1",
     "job_url": "https://fa-evmr-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/{id}"},
    {"name": "Snowflake", "fetch": phenom.fetch, "host": "careers.snowflake.com",
     "job_url": "https://careers.snowflake.com/us/en/job/{id}"},
    {"name": "GitHub", "fetch": github_careers.fetch},

    # --- Tier D: Finance / Enterprise Engineering Centers --------------------
    {"name": "JPMorgan Chase", "fetch": oracle_hcm.fetch,
     "host": "jpmc.fa.oraclecloud.com", "site_number": "CX_1001",
     "job_url": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/{id}"},
    {"name": "Accenture", "fetch": workday.fetch,
     "host": "accenture.wd103.myworkdayjobs.com", "site": "AccentureCareers"},
    {"name": "Wells Fargo", "fetch": workday.fetch,
     "host": "wf.wd1.myworkdayjobs.com", "tenant": "wf", "site": "WellsFargoJobs"},
    {"name": "Morgan Stanley", "fetch": workday.fetch,
     "host": "ms.wd5.myworkdayjobs.com", "tenant": "ms", "site": "External"},
    {"name": "Barclays", "fetch": workday.fetch,
     "host": "barclays.wd3.myworkdayjobs.com", "site": "External_Career_Site_Barclays"},
    {"name": "Visa", "fetch": workday.fetch,
     "host": "visa.wd5.myworkdayjobs.com", "site": "Visa"},
    {"name": "Mastercard", "fetch": workday.fetch,
     "host": "mastercard.wd1.myworkdayjobs.com", "site": "CorporateCareers"},
    {"name": "Bloomberg", "fetch": bloomberg.fetch},
    {"name": "Jane Street", "fetch": janestreet.fetch},

    # --- Developer & High-Growth Platforms in India --------------------------
    {"name": "Stripe", "fetch": greenhouse.fetch, "token": "stripe"},
    {"name": "MongoDB", "fetch": greenhouse.fetch, "token": "mongodb"},
    {"name": "Rubrik", "fetch": greenhouse.fetch, "token": "rubrik"},
    {"name": "Cloudflare", "fetch": greenhouse.fetch, "token": "cloudflare"},
    {"name": "Datadog", "fetch": greenhouse.fetch, "token": "datadog"},
    {"name": "Databricks", "fetch": greenhouse.fetch, "token": "databricks"},
    {"name": "Elastic", "fetch": greenhouse.fetch, "token": "elastic"},
    {"name": "GitLab", "fetch": greenhouse.fetch, "token": "gitlab"},
    {"name": "Twilio", "fetch": greenhouse.fetch, "token": "twilio"},
    {"name": "Okta", "fetch": greenhouse.fetch, "token": "okta"},
    {"name": "Pure Storage", "fetch": greenhouse.fetch, "token": "purestorage"},
    {"name": "Autodesk", "fetch": workday.fetch,
     "host": "autodesk.wd1.myworkdayjobs.com", "site": "Ext",
     "search_text": "intern"},
]

# Validation: ensure every registry entry has the minimum required keys
_REQUIRED_KEYS = {"name", "fetch"}
for _entry in COMPANIES:
    _missing = _REQUIRED_KEYS - set(_entry.keys())
    if _missing:
        raise ValueError(
            f"Invalid company config for '{_entry.get('name', 'UNKNOWN')}': missing required keys {_missing}"
        )

