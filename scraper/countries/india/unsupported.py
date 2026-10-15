"""Documented unsupported companies or campus-only hiring programs in India."""

INDIA_UNSUPPORTED = {
    # Tier A
    "Atlassian": "careers site uses iCIMS iframe portal; indexed via Google Jobs fallback when SERP_API_KEY or RAPIDAPI_KEY is configured",
    # Tier B
    "BrowserStack": "uses closed ATS without public search API; routes student hiring via campus & aggregators",
    "Chargebee": "uses closed ATS without public search API; routes student hiring via campus & aggregators",
    "Dream11": "uses Dream Sports proprietary careers portal without public search API",
    "Flipkart": "careers site sits behind enterprise bot defense; indexed via Google Jobs fallback when SERP_API_KEY or RAPIDAPI_KEY is configured",
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
    "HP": "careers portal sits behind Cloudflare bot protection; indexed via Google Jobs fallback when SERP_API_KEY or RAPIDAPI_KEY is configured",
    "Intuit": "careers portal sits behind Radancy search without open public REST API",
    "SAP": "SuccessFactors career site requires authenticated recruiter operators; indexed via Google Jobs fallback when SERP_API_KEY or RAPIDAPI_KEY is configured",
    "Siemens": "careers site runs on Avature global portal without public JSON search API; requires interactive session",
    "Faveo": "careers site runs on Zoho Recruit India portal without open unauthenticated REST API",
    "Uber": "careers search API sits behind Cloudflare bot defense; indexed via Google Jobs fallback when SERP_API_KEY or RAPIDAPI_KEY is configured",
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
    "Tesla": "careers site sits behind Akamai bot protection returning 403 to non-browser clients",
    "Spotify": "limited tech/engineering presence in India; student hiring primarily US/EU/UK",
}
