"""Keka Hire job boards: https://{subdomain}.keka.com/careers/api/jobs/default/active"""
from typing import Any, Dict, List

from ..http import request_json
from ..models import Job, as_date

API = "https://{subdomain}.keka.com/careers/api/jobs/{portal}/active"


def fetch(cfg: Dict[str, Any]) -> List[Job]:
    subdomain = cfg["subdomain"]
    portal = cfg.get("portal", "default")
    url = API.format(subdomain=subdomain, portal=portal)
    data = request_json("GET", url)
    jobs: List[Job] = []
    for j in data or []:
        locations: List[str] = []
        for loc in j.get("jobLocations") or []:
            city = loc.get("city") or loc.get("name") or ""
            country = loc.get("countryName") or loc.get("countryCode") or ""
            if city and country and city.lower() != country.lower():
                locations.append(f"{city}, {country}")
            elif city or country:
                locations.append(city or country)
        job_id = str(j.get("id") or j.get("jobNumber") or "")
        if not job_id:
            continue
        job_url = f"https://{subdomain}.keka.com/careers/jobdetails/{job_id}"
        jobs.append(Job(
            company=cfg["name"],
            external_id=job_id,
            title=j.get("title", ""),
            url=job_url,
            locations=locations,
            posted=as_date(j.get("publishedOn")),
        ))
    return jobs
