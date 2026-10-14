"""GitHub Actions CI and deployment reporting utilities."""
from datetime import datetime, timezone
import os
import re

from . import display


def update_sitemap(sitemap_path: str) -> None:
    """Keep sitemap.xml <lastmod> timestamps synced for SEO search engine crawlers."""
    if not os.path.exists(sitemap_path):
        return
    try:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with open(sitemap_path, "r", encoding="utf-8") as f:
            content = f.read()
        updated = re.sub(r"<lastmod>[^<]+</lastmod>", f"<lastmod>{today_str}</lastmod>", content)
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(updated)
    except Exception as err:
        print(display.yellow(f"warning: could not update sitemap.xml: {err}"))


def write_github_dryrun_outputs(
    total_duration: float,
    succeeded: set,
    failed: dict,
    all_jobs: list,
) -> None:
    """Surface dry-run stats to GitHub Actions outputs and step summary."""
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        try:
            with open(gh_output, "a", encoding="utf-8") as fh:
                fh.write(f"added=0\nclosed=0\nfailed={len(failed)}\n")
        except OSError as exc:
            print(display.yellow(f"warning: failed writing GITHUB_OUTPUT: {exc}"))

    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary:
        try:
            with open(gh_summary, "a", encoding="utf-8") as fh:
                fh.write("### ⚠️ Dry Run Completed (No Database Changes)\n\n")
                fh.write(f"- **Total Time:** `{total_duration:.1f}s`\n")
                fh.write(f"- **Companies Succeeded:** `{len(succeeded)}`\n")
                fh.write(f"- **Active India Postings Found:** `{len(all_jobs)}`\n\n")
        except OSError as exc:
            print(display.yellow(f"warning: failed writing GITHUB_STEP_SUMMARY: {exc}"))


def write_github_outputs(added: list, closed: list, failed: dict) -> None:
    """Surface added/closed/failed counts to GitHub Actions outputs."""
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        try:
            with open(gh_output, "a", encoding="utf-8") as fh:
                fh.write(f"added={len(added)}\nclosed={len(closed)}\nfailed={len(failed)}\n")
        except OSError as exc:
            print(display.yellow(f"warning: failed writing GITHUB_OUTPUT: {exc}"))


def write_github_summary(
    total_duration: float,
    succeeded: set,
    failed: dict,
    all_jobs: list,
    added: list,
    closed: list,
) -> None:
    """Render a rich dashboard inside GitHub Actions Job Summary."""
    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not gh_summary:
        return
    try:
        with open(gh_summary, "a", encoding="utf-8") as fh:
            fh.write("### 🚀 India Tech Internships Scrape Summary\n\n")
            fh.write(f"- **Runtime:** `{total_duration:.1f}s` (parallel execution)\n")
            fh.write(f"- **Companies Succeeded:** `{len(succeeded)}` | **Failed:** `{len(failed)}`\n")
            fh.write(f"- **Active India Internships:** `{len(all_jobs)}`\n")
            fh.write(f"- **New Postings Added:** `{len(added)}` | **Closed:** `{len(closed)}`\n\n")

            if added:
                fh.write("#### 🆕 New Internships Discovered\n\n")
                fh.write("| Company | Role | Hub | Category |\n|---|---|---|---|\n")
                for j in added:
                    loc = j.get("city_tag") or "India"
                    fh.write(f"| **{j['company']}** | [{j['title']}]({j['url']}) | {loc} | `{j.get('category', 'Tech')}` |\n")
                fh.write("\n")

            if failed:
                fh.write("#### ⚠️ Scraper Diagnostics\n\n")
                fh.write("| Company | Error Message |\n|---|---|\n")
                for c, err in sorted(failed.items()):
                    short_err = str(err).split("\n")[0][:80]
                    fh.write(f"| **{c}** | `{short_err}` |\n")
                fh.write("\n")
    except OSError as exc:
        print(display.yellow(f"warning: failed writing GITHUB_STEP_SUMMARY: {exc}"))
