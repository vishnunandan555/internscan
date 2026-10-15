#!/usr/bin/env python3
"""InternScan India — Telegram Bot
Lightweight, resilient Telegram Bot engineered for ultra-low memory nodes (< 35 MB RAM).

Modes of Operation:
1. Auto-Broadcaster: Polls InternScan India's public API and alerts your Telegram
   channel or group the moment a new verified internship appears.
2. Interactive Commands:
   - /start, /help : Bot intro & command guide
   - /latest       : View newly discovered internships
   - /active       : Active openings summary & top categories
   - /status       : Health check, bot uptime & node memory usage
"""
import html
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# Optional: Load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_VERSION = "2.0.0"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
API_LATEST_URL = (
    os.environ.get("INTERNSCAN_API_URL")
    or "https://vishnunandan555.github.io/internscan/api/latest.json"
).strip()
API_ACTIVE_URL = (
    os.environ.get("INTERNSCAN_ACTIVE_URL")
    or "https://vishnunandan555.github.io/internscan/api/active.json"
).strip()

POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL_SECONDS", "1800"))  # Default 30 mins
STATE_FILE = os.path.join(os.path.dirname(__file__), "seen_jobs.json")
TELEGRAM_API = "https://api.telegram.org/bot"

START_TIME = time.time()


def http_get(url: str, timeout: int = 15) -> Optional[dict]:
    """Fetch JSON from a remote URL using standard urllib (zero dependencies)."""
    headers = {"User-Agent": f"InternScan-Bot/{BOT_VERSION}"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] HTTP GET error for {url}: {exc}", file=sys.stderr)
    return None


def telegram_api(method: str, payload: dict) -> Optional[dict]:
    """Invoke Telegram Bot API method via JSON POST."""
    if not BOT_TOKEN:
        return None
    url = f"{TELEGRAM_API}{BOT_TOKEN}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Telegram API error ({method}): {exc}", file=sys.stderr)
        return None


def send_message(chat_id: str, text: str, reply_to: Optional[int] = None) -> bool:
    """Send HTML message to a chat or channel."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    res = telegram_api("sendMessage", payload)
    return bool(res and res.get("ok"))


def format_job_card(job: dict, is_reopened: bool = False) -> str:
    """Format single internship into a modern HTML Telegram card."""
    badge = "🔄 <b>INTERNSHIP REOPENED</b>" if is_reopened else "🚀 <b>NEW INTERNSHIP OPENING</b>"
    company = html.escape(str(job.get("company", "Company")))
    title = html.escape(str(job.get("title", "Internship Role")))
    category = html.escape(str(job.get("category") or "Software"))
    loc = html.escape(str(job.get("city_tag") or ", ".join(job.get("locations", [])) or "India"))
    url = job.get("url", "").strip()

    lines = [
        badge,
        "",
        f"🏢 <b>Company:</b> {company}",
        f"💼 <b>Role:</b> {title}",
        f"📍 <b>Location:</b> {loc}",
        f"🏷️ <b>Category:</b> <code>{category}</code>",
    ]

    if job.get("posted"):
        lines.append(f"📅 <b>Posted:</b> {html.escape(str(job['posted']))}")

    if url:
        lines.append("")
        lines.append(f"👉 <a href=\"{html.escape(url)}\"><b>Apply on Official Portal &rarr;</b></a>")

    lines.append("")
    lines.append("<i>Verified by InternScan India · Official ATS Sync</i>")
    return "\n".join(lines)


# State Persistence for Zero-Duplicate Broadcasting
def load_seen_state() -> dict:
    """Load seen jobs and last sync timestamp from local disk."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return {"last_updated": None, "seen_uids": []}


def save_seen_state(state: dict) -> None:
    """Save seen state atomically."""
    tmp = STATE_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2)
        os.replace(tmp, STATE_FILE)
    except Exception as exc:
        print(f"Failed to save state: {exc}", file=sys.stderr)


def check_and_broadcast() -> int:
    """Fetch api/latest.json and broadcast any new postings to the channel."""
    if not CHANNEL_ID:
        return 0

    data = http_get(API_LATEST_URL)
    if not data:
        return 0

    updated_at = data.get("updated_at")
    new_jobs = data.get("new_jobs", [])
    reopened_jobs = data.get("reopened_jobs", [])

    state = load_seen_state()
    seen_set = set(state.get("seen_uids", []))

    broadcast_count = 0

    # Filter out anything already broadcasted
    jobs_to_send = []
    for j in new_jobs:
        job_key = f"{j.get('company')}:{j.get('title')}:{j.get('url')}"
        if job_key not in seen_set:
            jobs_to_send.append((j, False, job_key))

    for j in reopened_jobs:
        job_key = f"reopened:{j.get('company')}:{j.get('title')}:{j.get('url')}"
        if job_key not in seen_set:
            jobs_to_send.append((j, True, job_key))

    for job, is_reopened, job_key in jobs_to_send:
        card = format_job_card(job, is_reopened=is_reopened)
        if send_message(CHANNEL_ID, card):
            seen_set.add(job_key)
            broadcast_count += 1
            time.sleep(0.5)  # Telegram rate limit compliance

    state["last_updated"] = updated_at
    # Keep last 500 keys to keep disk memory < 15KB
    state["seen_uids"] = list(seen_set)[-500:]
    save_seen_state(state)

    if broadcast_count > 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Broadcasted {broadcast_count} new alerts to {CHANNEL_ID}.")

    return broadcast_count


# Command Handlers for Interactive Chat
def handle_command(chat_id: str, text: str, msg_id: int) -> None:
    """Process incoming slash commands."""
    cmd = text.split()[0].lower().split("@")[0]

    if cmd in ("/start", "/help"):
        reply = (
            f"👋 <b>Welcome to InternScan India Bot! (v{BOT_VERSION})</b>\n\n"
            "I track 100% verified software engineering, AI/ML, systems, and tech "
            "internships across 59+ tech giants and GCCs in India direct from official career portals.\n\n"
            "<b>Available Commands:</b>\n"
            "• /latest - View the newest internships from today's sync\n"
            "• /active - Overview of currently active openings & categories\n"
            "• /status - Health check & server resource stats\n"
            "• /help   - Display this help message\n\n"
            "🌐 <a href=\"https://vishnunandan555.github.io/internscan/\"><b>Open Web Tracker &rarr;</b></a>"
        )
        send_message(chat_id, reply, reply_to=msg_id)

    elif cmd == "/latest":
        data = http_get(API_LATEST_URL)
        if not data:
            send_message(chat_id, "⚠️ Unable to reach the InternScan API right now. Please try again shortly.", reply_to=msg_id)
            return

        new_jobs = data.get("new_jobs", [])
        if not new_jobs:
            total = data.get("total_active", 0)
            send_message(
                chat_id,
                f"ℹ️ <b>No brand new postings added today.</b>\n\n"
                f"There are currently <b>{total}</b> active verified internships available!\n"
                f"👉 <a href=\"https://vishnunandan555.github.io/internscan/\">Browse all openings here</a>",
                reply_to=msg_id,
            )
            return

        send_message(chat_id, f"🔥 <b>{len(new_jobs)} New Internship(s) Added Today:</b>", reply_to=msg_id)
        for j in new_jobs[:5]:
            send_message(chat_id, format_job_card(j))
            time.sleep(0.3)

    elif cmd == "/active":
        data = http_get(API_ACTIVE_URL)
        if not data:
            send_message(chat_id, "⚠️ Unable to reach the InternScan API right now.", reply_to=msg_id)
            return

        jobs = data.get("jobs", [])
        total = len(jobs)
        # Calculate category distribution
        categories = {}
        for j in jobs:
            c = j.get("category") or "Software"
            categories[c] = categories.get(c, 0) + 1

        cat_lines = "\n".join([f"  • <b>{c}:</b> {n} openings" for c, n in sorted(categories.items(), key=lambda x: -x[1])[:6]])

        reply = (
            f"📊 <b>InternScan India — Active Openings</b>\n\n"
            f"🎯 <b>Total Verified Positions:</b> {total}\n"
            f"🕒 <b>Last Updated:</b> {data.get('updated_at', 'Today')}\n\n"
            f"<b>Top Categories:</b>\n{cat_lines}\n\n"
            f"👉 <a href=\"https://vishnunandan555.github.io/internscan/\"><b>Explore all {total} listings on Web Tracker &rarr;</b></a>"
        )
        send_message(chat_id, reply, reply_to=msg_id)

    elif cmd == "/status":
        uptime_sec = int(time.time() - START_TIME)
        mins, sec = divmod(uptime_sec, 60)
        hrs, mins = divmod(mins, 60)
        uptime_str = f"{hrs}h {mins}m {sec}s"

        # Check memory footprint on Linux
        mem_mb = "N/A"
        try:
            with open("/proc/self/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        mem_mb = f"{int(line.split()[1]) / 1024:.1f} MB"
                        break
        except Exception:
            pass

        reply = (
            f"🟢 <b>InternScan Bot Status: ONLINE (v{BOT_VERSION})</b>\n\n"
            f"⏱️ <b>Bot Uptime:</b> <code>{uptime_str}</code>\n"
            f"🧠 <b>RAM Usage:</b> <code>{mem_mb}</code> (Runs on &lt;35MB nodes!)\n"
            f"📡 <b>Target Channel:</b> <code>{CHANNEL_ID or 'Not Set'}</code>\n"
            f"🔄 <b>Poll Cadence:</b> Every {POLL_INTERVAL_SECONDS // 60} minutes\n"
            f"🚀 <b>Tracking 59+ Tech Employers</b>"
        )
        send_message(chat_id, reply, reply_to=msg_id)


def run_bot():
    """Main event loop combining long-polling for commands and timer for broadcasts."""
    print("=" * 60)
    print(f"🤖 InternScan India Telegram Bot (v{BOT_VERSION}) Starting...")
    print(f"📡 API Endpoint : {API_LATEST_URL}")
    print(f"📢 Broadcast To : {CHANNEL_ID or 'Disabled (Set TELEGRAM_CHAT_ID)'}")
    print(f"⏱️ Poll Cadence : Every {POLL_INTERVAL_SECONDS}s")
    print("=" * 60)

    if not BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN is not set in environment or .env!", file=sys.stderr)
        print("Please check bot/.env.example for instructions.", file=sys.stderr)
        sys.exit(1)

    # Initial check on startup
    try:
        check_and_broadcast()
    except Exception as exc:
        print(f"Startup check failed: {exc}", file=sys.stderr)

    last_check_time = time.time()
    offset = None

    while True:
        # 1. Check if it's time to poll the API for new internships
        if time.time() - last_check_time >= POLL_INTERVAL_SECONDS:
            try:
                check_and_broadcast()
            except Exception as exc:
                print(f"Broadcast check failed: {exc}", file=sys.stderr)
            last_check_time = time.time()

        # 2. Long-poll Telegram getUpdates for interactive user messages
        try:
            params = {"timeout": 15, "limit": 20}
            if offset is not None:
                params["offset"] = offset

            updates = telegram_api("getUpdates", params)
            if updates and updates.get("ok"):
                for item in updates.get("result", []):
                    offset = item["update_id"] + 1
                    msg = item.get("message")
                    if not msg:
                        continue
                    text = msg.get("text", "")
                    sender_id = str(msg.get("chat", {}).get("id", ""))
                    msg_id = msg.get("message_id")

                    if text.startswith("/"):
                        handle_command(sender_id, text, msg_id)
        except Exception as exc:
            print(f"Error handling updates: {exc}", file=sys.stderr)
            time.sleep(2)

        time.sleep(0.5)


if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 InternScan Bot stopped gracefully.")
        sys.exit(0)
