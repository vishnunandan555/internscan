#!/usr/bin/env python3
"""Synchronize scraper health status with GitHub Issues.

Prevents issue spam and duplicates by maintaining at most ONE open issue
with the label 'scraper-health':
- If failures exist in data/health.json:
    - If an open 'scraper-health' issue exists: updates its title and body with
      the latest failing companies and UTC timestamp.
    - Automatically closes any duplicate/older open 'scraper-health' issues as superseded.
    - If no open issue exists: creates a single issue titled '[Scraper Health] Active Scraper Failures'.
- If no failures exist (0 failing companies):
    - Automatically closes all open 'scraper-health' issues with a resolution comment.
"""

from datetime import datetime, timezone
import json
import os
import subprocess
import sys
import tempfile

LABEL = "scraper-health"
ISSUE_TITLE = "[Scraper Health] Active Scraper Failures"
HEALTH_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "health.json")


def run_gh(*args):
    """Run a gh CLI command and return stdout string, or None on error."""
    try:
        cmd = ["gh"] + list(args)
        res = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return res.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as err:
        print(f"[warning] gh command failed: {err}", file=sys.stderr)
        return None


def get_open_health_issues():
    """Return a list of open issues with label scraper-health: [{'number': N, 'title': '...'}, ...]"""
    out = run_gh("issue", "list", "--state", "open", "--label", LABEL, "--json", "number,title")
    if not out:
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def format_issue_body(failed: dict) -> str:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "### Automated Scraper Health Report",
        f"_Last synced: {now_utc}_",
        "",
        f"**{len(failed)}** career scraper(s) reported errors during the scheduled run:",
        "",
    ]
    for company, err in sorted(failed.items()):
        lines.append(f"- **{company}**: `{err}`")

    lines.extend([
        "",
        "> **Note:** Job listings for temporarily failing companies are preserved in `data/jobs.json`.",
        "> This issue is automatically kept up to date and will close automatically when all scrapers recover.",
    ])
    return "\n".join(lines)


def sync():
    if not os.path.isfile(HEALTH_FILE):
        print(f"[info] No health file found at {HEALTH_FILE}, exiting.")
        return 0

    try:
        with open(HEALTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"[error] Failed reading {HEALTH_FILE}: {exc}", file=sys.stderr)
        return 1

    failed = data.get("failed", {})
    open_issues = get_open_health_issues()
    print(f"[info] Scraper health: {len(failed)} failed. Found {len(open_issues)} open '{LABEL}' issues.")

    if not failed:
        # All scrapers are healthy! Close any open scraper-health issues.
        if open_issues:
            print(f"[info] Scrapers recovered. Closing {len(open_issues)} open health issue(s)...")
            for issue in open_issues:
                num = issue["number"]
                run_gh(
                    "issue",
                    "close",
                    str(num),
                    "--comment",
                    "🎉 All scrapers passed successfully in the latest scrape run. Auto-closing.",
                    "--reason",
                    "completed",
                )
                print(f"[info] Closed #{num}")
        else:
            print("[info] All scrapers healthy, no open issues to close.")
        return 0

    # Failures exist
    body_content = format_issue_body(failed)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
        tf.write(body_content)
        body_file_path = tf.name

    try:
        if open_issues:
            # Sort by issue number descending to pick the most recent (or pick first)
            open_issues_sorted = sorted(open_issues, key=lambda x: x["number"], reverse=True)
            primary_issue = open_issues_sorted[0]
            primary_num = primary_issue["number"]

            print(f"[info] Updating primary issue #{primary_num} with latest failures...")
            run_gh(
                "issue",
                "edit",
                str(primary_num),
                "--title",
                ISSUE_TITLE,
                "--body-file",
                body_file_path,
            )

            # Close all other duplicate issues
            for dup in open_issues_sorted[1:]:
                dup_num = dup["number"]
                print(f"[info] Closing duplicate/superseded issue #{dup_num}...")
                run_gh(
                    "issue",
                    "close",
                    str(dup_num),
                    "--comment",
                    f"Closed as duplicate/superseded in favor of #{primary_num}.",
                    "--reason",
                    "not planned",
                )
        else:
            print("[info] Creating single health issue...")
            # Ensure label exists
            run_gh("label", "create", LABEL, "--color", "D93F0B", "--description", "a careers-API scraper is failing")
            run_gh(
                "issue",
                "create",
                "--title",
                ISSUE_TITLE,
                "--body-file",
                body_file_path,
                "--label",
                LABEL,
            )
    finally:
        if os.path.exists(body_file_path):
            os.remove(body_file_path)

    return 0


if __name__ == "__main__":
    sys.exit(sync())
