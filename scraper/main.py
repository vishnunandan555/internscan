"""InternScan India — High-speed concurrent orchestrator for verified tech internships.

Usage:
    python -m scraper.main                     # Scrape all companies concurrently (8 threads)
    python -m scraper.main -c qualcomm         # Scrape a single company
    python -m scraper.main -c "amd,phonepe"    # Scrape specific companies
    python -m scraper.main --dry-run           # Preview listings without writing to disk
    python -m scraper.main -k "hardware"       # Filter for hardware/specific roles
    python -m scraper.main --version           # Show current version
    python -m scraper.main --list              # List all configured & unsupported companies
"""
import argparse
import concurrent.futures
from datetime import datetime, timezone
import gzip
import json
import os
import re
import shutil
import sys
import time

from . import __version__, api, ci, display, store, telegram
from .categories import categorize
from .companies import (
    COMPANIES,
    FALLBACK_COMPANIES,
    UNSUPPORTED,
    get_all_known_companies,
    get_companies,
    has_fallback_keys,
)
from .countries import SUPPORTED_COUNTRIES
from .http import close_thread_session, get_session, set_thread_timeout
from .logger import ScrapeLogger
from .regions import classify_location, get_city_tag, is_india_job
from .render_list import render_list
from .render_readme import render

HEALTH_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "health.json")
DOCS_JOBS_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "jobs.json")
DOCS_SITEMAP_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "sitemap.xml")





def _scrape_single_company(cfg, keyword=None, country=None):
    """Worker function executed inside ThreadPoolExecutor for a single company."""
    name = cfg["name"]
    start_t = time.perf_counter()
    try:
        cfg["session"] = get_session()
        set_thread_timeout(cfg.get("timeout"))
        fetched = cfg["fetch"](cfg)
        interns = [j for j in fetched if j.looks_like_internship() and j.url]

        # Optional keyword filter (e.g. "hardware", "machine learning", "frontend")
        if keyword:
            kw = keyword.lower()
            interns = [j for j in interns if kw in j.title.lower()]

        # Fused single-pass filter for categorization, region verification, and city hub tagging
        matched = []
        for j in interns:
            cat = categorize(j.title)
            if not cat:
                continue
            c_code, region, hub = classify_location(j.locations)
            # If target country is specified, filter by it
            if country and c_code != country:
                continue
            # Keep roles in supported countries or global remote
            if c_code in SUPPORTED_COUNTRIES or c_code == "remote":
                j.category = cat
                j.country = c_code
                j.region = region
                j.city_tag = hub
                matched.append(j)

        duration = time.perf_counter() - start_t
        return (name, matched, len(fetched), len(interns), duration, None)
    except Exception as err:
        duration = time.perf_counter() - start_t
        return (name, [], 0, 0, duration, err)
    finally:
        close_thread_session()


def run(only_companies=None, keyword=None, dry_run=False, workers=8, country=None):
    """Run concurrent scraping across target companies."""
    # Filter target companies
    all_known = get_all_known_companies(country=country) if country else get_all_known_companies()
    if only_companies:
        norm_targets = {c.strip().lower() for c in only_companies}
        targets = [c for c in all_known if c["name"].lower() in norm_targets]
        if not targets:
            print(display.red(f"Error: No configured company matched {only_companies}."))
            print(display.dim("Use --list to see all supported company names."))
            return 1
    else:
        targets = get_companies(country=country) if country else get_companies()

    country_label = f" [{country.upper()}]" if country else " [GLOBAL]"
    print(display.bold(f"\n🚀 Launching scraper for {len(targets)} companies{country_label} ({workers} worker threads)..."))
    if dry_run:
        print(display.yellow("⚠️  Running in DRY RUN mode: files will NOT be updated.\n"))
    else:
        print()

    logger = ScrapeLogger()
    logger.log(f"Starting scrape for {len(targets)} companies with {workers} workers (country={country}, dry_run={dry_run}, keyword={keyword})")

    all_jobs, succeeded, failed = [], set(), {}
    total_start_t = time.perf_counter()

    # Execute scrapers concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(workers, len(targets))) as executor:
        futures = {executor.submit(_scrape_single_company, cfg, keyword, country): cfg["name"] for cfg in targets}

        for future in concurrent.futures.as_completed(futures):
            name, matched_jobs, n_fetched, n_interns, duration, err = future.result()
            if err is None:
                succeeded.add(name)
                all_jobs.extend(matched_jobs)
                print(display.status_ok(name, duration, n_fetched, n_interns, len(matched_jobs)))
                logger.log(f"[OK]   {name:<24} ({duration:4.1f}s) -> {n_fetched:>4} postings, {n_interns:>2} interns, {len(matched_jobs)} matched")
            else:
                failed[name] = str(err)
                print(display.status_fail(name, duration, err))
                logger.log(f"[FAIL] {name:<24} ({duration:4.1f}s) -> ERROR: {err}", level="ERROR")

    total_duration = time.perf_counter() - total_start_t

    if not succeeded:
        print(display.red("\nEvery attempted scraper failed — aborting without touching state."))
        if not dry_run:
            logger.save(
                total_duration=total_duration,
                succeeded=succeeded,
                failed=failed,
                added=[],
                closed=[],
                reopened=[],
                all_india_jobs=[],
            )
        return 1

    # In dry-run mode, display stats and exit without modifying database or production logs
    if dry_run:
        display.print_dashboard(
            total_duration=total_duration,
            succeeded=succeeded,
            failed=failed,
            added=[],
            closed=[],
            reopened=[],
            all_india_jobs=all_jobs,
            is_dry_run=True,
        )
        ci.write_github_dryrun_outputs(total_duration, succeeded, failed, all_jobs)
        return 0

    # Merge into database and diff
    state = store.load()
    added, closed, reopened = store.merge(state, all_jobs, succeeded)
    store.save(state)
    render(state)

    # Maintain cumulative health across full and partial runs
    all_configured = {c["name"] for c in targets}
    prev_succeeded = all_configured.copy()
    prev_failed = {}
    if os.path.exists(HEALTH_PATH):
        try:
            with open(HEALTH_PATH, "r", encoding="utf-8") as fh:
                hdata = json.load(fh)
                prev_failed = dict(hdata.get("failed", {}))
                prev_succeeded = (set(hdata.get("succeeded", [])) | all_configured) - set(prev_failed.keys())
        except Exception:
            pass

    if only_companies:
        for c in succeeded:
            prev_succeeded.add(c)
            prev_failed.pop(c, None)
        for c, err in failed.items():
            prev_failed[c] = str(err)
            prev_succeeded.discard(c)
        full_succeeded = prev_succeeded
        full_failed = prev_failed
    else:
        full_succeeded = succeeded
        full_failed = failed

    # Render minimal company list into LIST.md
    render_list(full_succeeded, full_failed, updated_at=state.get("updated_at"))

    # Sync a copy directly into docs/ so GitHub Pages loads without CORS or CDN latency
    try:
        os.makedirs(os.path.dirname(DOCS_JOBS_PATH), exist_ok=True)
        shutil.copyfile(store.DATA_PATH, DOCS_JOBS_PATH)
        # Pre-compress gzip copy for optimized network distribution (Issue 3.3)
        with open(store.DATA_PATH, "rb") as f_in:
            with gzip.open(store.DATA_PATH + ".gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        shutil.copyfile(store.DATA_PATH + ".gz", DOCS_JOBS_PATH + ".gz")
        ci.update_sitemap(DOCS_SITEMAP_PATH)
        api.generate_apis(state, added=added, reopened=reopened)
    except Exception as err:
        print(display.yellow(f"warning: could not sync docs/jobs.json or public APIs: {err}"))

    # Record health
    os.makedirs(os.path.dirname(HEALTH_PATH), exist_ok=True)
    with open(HEALTH_PATH, "w", encoding="utf-8") as fh:
        json.dump({"succeeded": sorted(full_succeeded), "failed": full_failed},
                  fh, indent=2, sort_keys=True)
        fh.write("\n")

    # Save dual-tier logs to logs/ folder
    logger.save(
        total_duration=total_duration,
        succeeded=succeeded,
        failed=failed,
        added=added,
        closed=closed,
        reopened=reopened,
        all_india_jobs=all_jobs,
    )

    # Display full dashboard summary
    display.print_dashboard(
        total_duration=total_duration,
        succeeded=succeeded,
        failed=failed,
        added=added,
        closed=closed,
        reopened=reopened,
        all_india_jobs=all_jobs,
        is_dry_run=False,
    )

    # Surface counts and summary to GitHub CI
    ci.write_github_outputs(added, closed, failed)
    ci.write_github_summary(total_duration, succeeded, failed, all_jobs, added, closed)

    # Dispatch Telegram notifications if configured
    try:
        telegram.notify_updates(added=added, reopened=reopened)
    except Exception as err:
        print(display.yellow(f"warning: could not dispatch Telegram alerts: {err}"))

    return 0




def _args_from_env() -> tuple:
    """Read scraper config from environment variables (set by GitHub Actions or container)."""
    company_env = os.environ.get("SCRAPER_COMPANY", "").strip()
    country_env = os.environ.get("SCRAPER_COUNTRY", "").strip()
    keyword_env = os.environ.get("SCRAPER_KEYWORD", "").strip()
    dry_run_env = os.environ.get("SCRAPER_DRY_RUN", "").strip().lower() in ("true", "1", "yes")
    workers_env_str = os.environ.get("SCRAPER_WORKERS", "").strip()
    workers_env = int(workers_env_str) if workers_env_str.isdigit() else None
    companies = [c.strip() for c in company_env.split(",") if c.strip()] if company_env else None
    return companies, keyword_env or None, dry_run_env, workers_env, country_env or None


def main():
    parser = argparse.ArgumentParser(
        description="High-speed concurrent internship scraper for India engineering roles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("targets", nargs="*", help="Optional company name(s) to scrape (e.g. Google Qualcomm)")
    parser.add_argument("-c", "--company", action="append", help="Company name to scrape (can be repeated or comma-separated)")
    parser.add_argument("-C", "--country", help="Target country code (e.g. 'in', 'us', 'ca', 'uk', 'eu')")
    parser.add_argument("-k", "--keyword", help="Custom keyword to filter internship titles (e.g. 'hardware', '2027')")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Preview scraped listings without modifying data/ or README")
    parser.add_argument("-s", "--search", help="Universal search for any company/keyword using Google Jobs/SERP API")
    parser.add_argument("-w", "--workers", type=int, default=None, help="Number of concurrent worker threads (default: 8)")
    parser.add_argument("-l", "--list", action="store_true", help="List all configured and unsupported companies")
    parser.add_argument("-v", "--version", action="version", version=f"InternScan India v{__version__}")

    args = parser.parse_args()

    if args.search:
        from .adapters import serp_jobs
        print(display.bold(f"\n🔍 Querying Universal Job Search for: '{args.search}'..."))
        try:
            jobs = serp_jobs.fetch({"name": args.search, "query": args.search})
            print(display.green(f"Found {len(jobs)} postings:"))
            for j in jobs:
                loc = ", ".join(j.locations)
                print(f"  • {display.bold(j.company)} — {j.title} {display.cyan(loc)}")
                print(f"    {display.dim(j.url)}")
        except Exception as e:
            print(display.red(f"Error querying search API: {e}"))
            print(display.dim("Note: Requires SERP_API_KEY or RAPIDAPI_KEY set in environment."))
        return 0

    if args.list:
        print(display.bold(f"\n⚡ Direct ATS Scrapers ({len(COMPANIES)} companies):"))
        for c in sorted(COMPANIES, key=lambda x: x["name"]):
            padded = f"{c['name']:<24}"
            print(f"  • {display.bold(padded)} (adapter: {c['fetch'].__module__.split('.')[-1]})")

        fallback_status = "ENABLED (Key Active)" if has_fallback_keys() else "STANDBY (Set SERP_API_KEY/RAPIDAPI_KEY)"
        print(display.bold(f"\n🛡️ Bot-Protected Scrapers ({len(FALLBACK_COMPANIES)} companies — {fallback_status}):"))
        for c in sorted(FALLBACK_COMPANIES, key=lambda x: x["name"]):
            padded = f"{c['name']:<24}"
            print(f"  • {display.bold(padded)} (adapter: Google Jobs fallback)")

        print(display.bold(f"\n📋 Documented Unsupported / Campus-Only ({len(UNSUPPORTED)} companies):"))
        for name, reason in sorted(UNSUPPORTED.items()):
            print(f"  {display.status_skip(name, reason)}")
        print()
        return 0

    env_companies, env_keyword, env_dry_run, env_workers, env_country = _args_from_env()

    # Combine positional args and --company flags
    selected = []
    if args.targets:
        selected.extend(args.targets)
    if args.company:
        for c in args.company:
            selected.extend([part.strip() for part in c.split(",") if part.strip()])
    if not selected and env_companies:
        selected.extend(env_companies)

    keyword = args.keyword or env_keyword
    dry_run = args.dry_run or env_dry_run
    workers = args.workers if args.workers is not None else (env_workers if env_workers is not None else 8)
    country = args.country or env_country

    return run(
        only_companies=set(selected) if selected else None,
        keyword=keyword,
        dry_run=dry_run,
        workers=workers,
        country=country,
    )


if __name__ == "__main__":
    sys.exit(main())
