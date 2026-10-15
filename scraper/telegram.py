"""Telegram notification dispatcher for InternScan India.

Sends structured notification cards to a Telegram Channel, Group, or personal chat
when new or reopened internships are detected during scraping.
Requires:
    TELEGRAM_BOT_TOKEN : Bot API Token from @BotFather
    TELEGRAM_CHAT_ID   : Target Channel (@channel_username) or Chat/Group numeric ID
"""
import html
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from typing import List, Optional

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


def format_job_message(job: dict, is_reopened: bool = False) -> str:
    """Format single job posting into clean, readable HTML for Telegram."""
    badge = "🔄 <b>INTERNSHIP REOPENED</b>" if is_reopened else "🚀 <b>NEW INTERNSHIP OPENING</b>"
    company = html.escape(str(job.get("company", "Company")))
    title = html.escape(str(job.get("title", "Internship Role")))
    category = html.escape(str(job.get("category") or "Software"))
    city_tag = html.escape(str(job.get("city_tag") or "India"))
    url = job.get("url", "").strip()

    locations = job.get("locations", [])
    loc_display = html.escape(", ".join(locations[:3])) if locations else city_tag

    lines = [
        badge,
        "",
        f"🏢 <b>Company:</b> {company}",
        f"💼 <b>Role:</b> {title}",
        f"📍 <b>Location:</b> {loc_display}",
        f"🏷️ <b>Domain:</b> <code>{category}</code>",
    ]

    if job.get("posted"):
        lines.append(f"📅 <b>Posted:</b> {html.escape(str(job['posted']))}")

    if url:
        lines.append("")
        lines.append(f"👉 <a href=\"{html.escape(url)}\"><b>Apply directly on Career Portal &rarr;</b></a>")

    lines.append("")
    lines.append("<i>Verified by InternScan India · Official ATS Sync</i>")
    return "\n".join(lines)


def send_message(token: str, chat_id: str, text: str) -> bool:
    """Send single HTML message via Telegram Bot API using standard library."""
    url = f"{TELEGRAM_API_BASE}{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.status == 200
    except Exception as exc:
        print(f"[WARN] Failed to send Telegram notification to {chat_id}: {exc}", file=sys.stderr)
        return False


def notify_updates(
    added: Optional[List[dict]] = None,
    reopened: Optional[List[dict]] = None,
    token: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> int:
    """Send notifications for all added and reopened internships.

    Returns the count of successfully delivered messages.
    """
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return 0

    added = added or []
    reopened = reopened or []
    total_to_send = len(added) + len(reopened)

    if total_to_send == 0:
        return 0

    print(f"\n📢 Dispatching {total_to_send} Telegram alert(s) to chat {chat_id}...")
    sent_count = 0

    # Send newly added jobs
    for job in added:
        msg = format_job_message(job, is_reopened=False)
        if send_message(token, chat_id, msg):
            sent_count += 1
        time.sleep(0.35)  # Respect Telegram rate limit (~30 msgs/sec max)

    # Send reopened jobs
    for job in reopened:
        msg = format_job_message(job, is_reopened=True)
        if send_message(token, chat_id, msg):
            sent_count += 1
        time.sleep(0.35)

    print(f"✅ Successfully delivered {sent_count}/{total_to_send} Telegram alert(s).")
    return sent_count
