# 🤖 InternTrack India — Telegram Bot & Hosting Guide

A resilient, ultra-lightweight Telegram Bot engineered to run 24/7 on minimal cloud nodes (**< 35 MB RAM**, requiring less than 15% of a 256 MB ₹10/month server).

---

## Features

- 📢 **Auto-Broadcaster:** Automatically checks the [InternTrack India Public API](https://vishnunandan555.github.io/interntrack-india/api/latest.json) and posts clean, formatted cards into your Telegram Channel or Group the moment a new internship drops.
- 💬 **Interactive Commands:**
  - `/latest` — Immediate real-time list of newly verified internships.
  - `/active` — Overview of currently active openings and top domain categories.
  - `/status` — Live health check, uptime, and memory footprint.
  - `/help`   — Command directory and tracker links.
- 🛡️ **Zero-Spam Deduplication:** Tracks seen job UIDs in a local `seen_jobs.json` file (~5 KB) so it never repeats notifications across server reboots.
- 🪶 **Zero Heavy Dependencies:** Written in standard Python 3.

---

## 3-Minute Quick Setup

### Step 1: Create Your Bot on Telegram (30 seconds)

1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)**.
2. Send `/newbot`.
3. Choose a name (e.g. `My Campus Intern Tracker`) and a username ending in `bot` (e.g. `campus_intern_bot`).
4. Copy your **HTTP API Token** (e.g. `7123456789:AAHfkj83...`).

### Step 2: Get your Channel or Group ID

* **To post in a Telegram Channel:**
  1. Create a Telegram Channel.
  2. Go to **Channel Settings → Administrators → Add Administrator** and select your bot. Give it permission to **Post Messages**.
  3. Your `TELEGRAM_CHAT_ID` is your public channel username (e.g. `@my_internships_hub`).
* **To post in a Private Group / Personal Chat:**
  1. Add your bot to the group.
  2. Send any message in the group.
  3. Forward a message to **[@userinfobot](https://t.me/userinfobot)** or check `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` to get the numeric ID (e.g. `-1001234567890`).

---

## Deploying on a ₹10/month Nano Server (Linux / VPS)

### 1. Clone & Configure

SSH into your server and run:

```bash
git clone https://github.com/vishnunandan555/interntrack-india.git
cd interntrack-india/bot

# Install the single tiny helper (python-dotenv)
pip install -r requirements.txt

# Create your configuration
cp .env.example .env
nano .env
```

Paste your bot token and channel ID:
```env
TELEGRAM_BOT_TOKEN=7123456789:AAHfkj...
TELEGRAM_CHAT_ID=@my_internships_hub
POLL_INTERVAL_SECONDS=1800
```
*(Press `Ctrl + O` then `Enter` to save, and `Ctrl + X` to exit nano)*.

### 2. Test Run

```bash
python3 main.py
```
You should see:
```text
============================================================
🤖 InternTrack India Telegram Bot Starting...
📡 API Endpoint : https://vishnunandan555.github.io/interntrack-india/api/latest.json
📢 Broadcast To : @my_internships_hub
⏱️ Poll Cadence : Every 1800s
============================================================
```

### 3. Keep Running 24/7 with systemd (Auto-Restart on Reboot)

To ensure the bot never stops running, even if the node reboots:

```bash
# 1. Copy the systemd unit file
sudo cp interntrack-bot.service /etc/systemd/system/

# (Optional: adjust paths in the service file if your user is not root)
# sudo nano /etc/systemd/system/interntrack-bot.service

# 2. Reload systemd and enable auto-start on boot
sudo systemctl daemon-reload
sudo systemctl enable interntrack-bot

# 3. Start the bot
sudo systemctl start interntrack-bot

# 4. Check live status and logs
sudo systemctl status interntrack-bot
```

To watch live logs in real-time:
```bash
journalctl -u interntrack-bot -f
```

---

## Alternative: Run via PM2 / Tmux

If your node has Node.js installed, you can also use `pm2`:
```bash
npm install -g pm2
pm2 start main.py --name "intern-bot" --interpreter python3
pm2 save
pm2 startup
```

Or simply run inside `tmux` / `screen`:
```bash
tmux new -s bot
python3 main.py
# Press Ctrl+B, then D to detach and let it run in the background
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | **Yes** | — | Bot token provided by `@BotFather`. |
| `TELEGRAM_CHAT_ID` | Optional | — | Channel `@username` or group/chat ID for auto-broadcasts. If omitted, only interactive commands (`/latest`) will respond. |
| `POLL_INTERVAL_SECONDS` | No | `1800` | How often to poll the public API (in seconds). Default: 30 minutes. |
| `INTERNTRACK_API_URL` | No | Official API | Remote URL for `api/latest.json`. |
| `INTERNTRACK_ACTIVE_URL` | No | Official API | Remote URL for `api/active.json`. |

---

## License

MIT © [Vishnu Nandan](https://github.com/vishnunandan555) · Part of the [InternTrack India](https://github.com/vishnunandan555/interntrack-india) project.
