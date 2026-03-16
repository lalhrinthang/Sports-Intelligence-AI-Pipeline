# 🛠️ Setup Guide — V3 Syndicate Pipeline

A step-by-step walkthrough for getting the pipeline running from zero.

---

## Step 1 — Get Your API Keys

You need four API keys before running anything.

### The Odds API
1. Go to https://the-odds-api.com
2. Click **Get API Key** — free plan gives 500 requests/month
3. Copy the key

### Google Gemini
1. Go to https://aistudio.google.com
2. Click **Get API Key** → **Create API Key**
3. Copy the key

### Anthropic Claude
1. Go to https://console.anthropic.com
2. Click **API Keys** → **Create Key**
3. Copy the key (starts with `sk-ant-`)

### Telegram Bot
1. Open Telegram and search **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the bot token BotFather gives you
4. Send any message to your new bot
5. Visit `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
6. Find `"chat":{"id":` — that number is your Chat ID

---

## Step 2 — Fill Your .env File

```env
ODDS_API_KEY=paste_here
GEMINI_API_KEY=paste_here
CLAUDE_API_KEY=paste_here
TELEGRAM_BOT_TOKEN=paste_here
TELEGRAM_CHAT_ID=paste_here
```

---

## Step 3 — Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 4 — Test Each Component

Run these in order. Fix any errors before moving to the next.

```bash
# 1. Test Telegram
python test_telegram.py

# 2. Test Odds API + Scheduler
python debug_all_matches.py

# 3. Test Gemini
python test_gemini.py

# 4. Test Validator + Claude
python test_claude_strat.py

# 5. Run all scenario tests
pytest pytest_\test_main.py -v -s

# 6. Run the full pipeline
python main.py
```

---

## Step 5 — Customise Your Sports

Open `modules/odds_collector.py`:

```python
SPORTS_TO_WATCH = [
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_uefa_champs_league",
    "soccer_malaysia_super_league",
]
```

Full list of available sport keys:
https://the-odds-api.com/sports-odds-data/sports-apis.html

---

## Step 6 — Adjust the Match Window

Open `main.py` and change:

```python
MATCH_WINDOW_MINUTES = 120   # How many minutes before kickoff to trigger
```

Recommended settings:

| Use Case | Window |
|----------|--------|
| Early research | 120 min |
| Pre-match | 30 min |
| Last minute | 15 min |

---

## Common Setup Errors

### `ModuleNotFoundError`
Virtual environment is not activated.
```bash
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
```

### `401 Unauthorized` from any API
Wrong API key in `.env`. Double-check for spaces or missing characters.

### `422` from Odds API
Invalid sport key. Check spelling — a common mistake is `scoccer` instead of `soccer`.

### Telegram not receiving messages
1. Make sure you sent at least one message to your bot first
2. Confirm `TELEGRAM_CHAT_ID` is a number, not a username