# 🔧 Troubleshooting Guide — V3 Syndicate Pipeline

A reference for every error this pipeline can produce and how to fix it.

---

## How to Read the Logs

Every log line follows this format:

```
2026-03-15 23:42:00 | INFO | [MODULE] | Status: STATUS | Detail message
```

The `[MODULE]` tells you exactly which file the error came from:

| Module | File |
|--------|------|
| `[MAIN]` | main.py |
| `[PIPELINE]` | pipeline.py |
| `[SCHEDULER]` | scheduler.py |
| `[ODDS_API]` | modules/odds_collector.py |
| `[GEMINI]` | modules/gemini_collector.py |
| `[VALIDATOR]` | validator.py |
| `[CLAUDE]` | modules/claude_strategist.py |
| `[TELEGRAM]` | modules/telegram_bot.py |
| `[DATABASE]` | modules/database.py |

---

## Errors by Module

---

### SCHEDULER Errors

#### `IDLE — No matches starting within the next X minutes`

**Possible causes and fixes:**

1. **No matches actually scheduled** — run `debug_all_matches.py` to confirm
2. **Timezone mismatch** — The Odds API returns UTC. Your machine may be comparing local time against UTC.
   ```python
   # Make sure scheduler.py uses this — not datetime.now()
   now_utc = datetime.now(timezone.utc)
   ```
3. **Wrong sport key** — e.g. `scoccer_spain_la_liga` instead of `soccer_spain_la_liga`
   ```bash
   python debug_all_matches.py   # check which sports return matches
   ```
4. **Window too small** — increase `MATCH_WINDOW_MINUTES` in `main.py`

---

#### `CHECKING | Match X | Starts in -91 min`

The match already started. The negative number means it kicked off 91 minutes ago.
The scheduler correctly ignores it. This is expected behaviour, not an error.

---

### ODDS_API Errors

#### `HTTP 422 for soccer_xyz`

Invalid sport key. The key does not exist in The Odds API.

Fix: Check the exact key at https://the-odds-api.com/sports-odds-data/sports-apis.html

#### `HTTP 401`

Wrong API key. Check `ODDS_API_KEY` in your `.env` file.

#### `No internet connection`

Your server has no network access. Check your VPS firewall settings.

---

### GEMINI Errors

#### `Gemini returned invalid JSON`

Gemini ignored the JSON-only instruction and returned plain text.

Fix: Add this line to the top of `prompts/gemini_hunter.txt`:
```
YOUR FIRST CHARACTER MUST BE { AND YOUR LAST CHARACTER MUST BE }
```

#### `gemini_hunter.txt not found`

The prompt file is missing or in the wrong location.

Fix: Confirm the file exists at `prompts/gemini_hunter.txt` relative to where you run `main.py`.

#### Gemini returns `null` or empty fields

The match may have very little public data (e.g. lower league, far future).

The pipeline will fail at validation and alert Telegram. This is correct behaviour.

---

### VALIDATOR Errors

#### `odds_movement: Field required`

The field name in your Pydantic schema does not match what Gemini outputs.

**How to diagnose:**
```python
# Add this temporarily to test_phase7.py
intelligence = collect_match_intelligence(sample_match)
print(intelligence.keys())
# Compare the printed keys against MatchIntelligence fields in validator.py
```

**The three files must use identical field names:**

| File | Must contain |
|------|-------------|
| `prompts/gemini_hunter.txt` | Field in the JSON schema section |
| `validator.py` | Field in `MatchIntelligence` class |
| `prompts/opus_strategist.txt` | Field referenced in audit pillars |

#### `recent_form: Field required`

A field exists in `validator.py` but Gemini was never told to provide it.

Fix — choose one:
- Remove the field from `validator.py`
- Add the field to the JSON schema in `gemini_hunter.txt`

---

### CLAUDE Errors

#### `'dict' object has no attribute 'match_id'`

The validated data is arriving as a plain dict instead of a Pydantic object.

**Root cause** — `validate_intelligence()` is returning `raw_data` instead of `validated`:
```python
# WRONG — in validator.py
return raw_data, None

# CORRECT
return validated, None
```

**Secondary cause** — pipeline.py is not unpacking the tuple correctly:
```python
# WRONG
validated = validate_intelligence(intelligence)

# CORRECT
validated, error = validate_intelligence(intelligence)
```

#### `Claude returned invalid JSON`

Claude ignored the JSON-only output rule.

Fix: Add this to the bottom of `prompts/sonnet_strategist.txt`:
```
REMINDER: Your entire response is a single JSON object.
First character: {   Last character: }   Nothing else.
```

The pipeline will automatically retry with Opus before failing.

#### `Both Sonnet and Haiku failed`

Both models returned invalid responses. Usually caused by a malformed prompt.

Fix: Check that `{intelligence_data}` placeholder exists in `sonnet_strategist.txt` and that `load_prompt()` replaces it correctly.

---

### TELEGRAM Errors

#### Telegram not receiving messages

1. Confirm the bot token is correct in `.env`
2. Confirm you sent at least one message to the bot in Telegram
3. Confirm `TELEGRAM_CHAT_ID` is a number, not a username
4. Test with:
   ```bash
   python test_telegram.py
   ```

#### `Chat not found`

Chat ID is wrong. Re-fetch it:
```
https://api.telegram.org/botYOUR_TOKEN/getUpdates
```
Look for `"chat":{"id":` in the response.

---

### pytest Errors

#### `sys.exit(console_main())`

pytest cannot find your modules.
Method 1 : Disable output capturing (quickest fix)
Run pytest with the -s flag to bypass the capture system entirely:
```bash
pytest -s -v \file_name\
```
Fix — ensure these files exist:

```
syndicate-pipeline/
├── conftest.py       ← must exist, with sys.path.insert
├── pytest.ini        ← must have pythonpath = .
└── tests/
    ├── __init__.py   ← must exist
    └── test_main.py
```

`conftest.py` content:
```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
```

`pytest.ini` content:
```ini
[pytest]
testpaths = tests
pythonpath = .
```

#### `ModuleNotFoundError` during pytest

Virtual environment is not active:
```bash
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
```

---

## Debug Scripts Reference

| Script | What it shows |
|--------|--------------|
| `debug_all_matches.py` | All matches, UTC times, minutes until kickoff, in-window status |
| `debug_scheduler.py` | UTC vs local time comparison, window calculation |
| `test_telegram.py` | Confirms Telegram bot token and Chat ID work |
| `test_gemini.py` | Raw Gemini output — shows exact field names returned |
| `test_claude_strat.py` | Full validator + Claude test with good and bad data |
| `test_claude_model.py` | Confirms Claude API token and specific model work |
| `geminiai_model_test.py` | Confirms Google API token and specific gemini model work |

---

## Still Stuck?

1. Run `python debug_all_matches.py` and paste the output
2. Check `logfile.txt` for the last 20 lines
3. Open an issue on GitHub with both outputs attached