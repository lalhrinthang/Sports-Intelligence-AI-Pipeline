import os
import asyncio
from dotenv import load_dotenv # Load environment variables from .env file
from telegram import Bot, Update # Telegram Bot API classes
from logger import log_step # Import the logging function from logger.py

load_dotenv() # Load environment variables from .env file

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') # Get the Telegram bot token from environment variables
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') # Get the Telegram chat ID from environment variables

async def _send_message(text):
    """Internal async function to send a Telegram message."""
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML") # Send a message to the specified chat ID and parse it as HTML

def send_alert(message):
    try:
        asyncio.run(_send_message(message)) # Run the async function to send the message
        log_step("Telegram", "SUCCESS", f"Message sent: {message[:50]}") # Log the successful sending of the message, including a preview of the message content
    except Exception as error:
        log_step("Telegram", "FAILED", f"Cound not send message: {str(error)}") # Log any errors that occur while trying to send the message

def send_intelligence_report(verdict, reason, confidence, match_id, home_team="", away_team=""):
    """Send a clean, formatted V3 Intelligence Report."""
    # ── Match name line ───────────────────────────────────
    if home_team and away_team:
        match_line = f"⚽ {home_team} vs {away_team}"
    else:
        match_line = f"🆔 <code>{match_id[:16]}...</code>"

    # Then in the report string replace the ID section:
    f"⚽ <b>MATCH</b>\n"
    f"┗ {match_line}\n"
    # ── Confidence badge ──────────────────────────────────
    if confidence >= 80:
        confidence_badge = "🔥 HIGH"
    elif confidence >= 65:
        confidence_badge = "✅ MEDIUM"
    else:
        confidence_badge = "⚠️ LOW"

    # ── Verdict emoji ─────────────────────────────────────
    verdict_upper = verdict.upper()
    if "BACK" in verdict_upper or "WIN" in verdict_upper:
        verdict_emoji = "🟢"
    elif "NO VALUE" in verdict_upper or "SKIP" in verdict_upper:
        verdict_emoji = "🔴"
    else:
        verdict_emoji = "🟡"

    # ── Split reason into pillars ─────────────────────────
    # Claude writes "PILLAR 1 (...): ... PILLAR 2 (...): ..."
    # We split on PILLAR to make each one its own section
    pillar_lines = ""
    if "PILLAR" in reason:
        import re
        parts = re.split(r'(PILLAR \d)', reason)
        # parts = ['', 'PILLAR 1', ' text...', 'PILLAR 2', ' text...']
        i = 1
        while i < len(parts) - 1:
            pillar_name = parts[i].strip()
            pillar_text = parts[i + 1].strip()

            # Clean up the pillar header
            # e.g. "PILLAR 1 (TEAM STRENGTH): Liverpool..."
            # becomes "1️⃣ TEAM STRENGTH"
            header_match = re.match(
                r'PILLAR (\d)[\s\S]*?\(([^)]+)\)', 
                pillar_name + pillar_text
            )

            number_emojis = {
                "1": "1️⃣", "2": "2️⃣",
                "3": "3️⃣", "4": "4️⃣"
            }

            # Extract pillar number
            num = re.search(r'\d', pillar_name)
            num = num.group() if num else "•"
            emoji = number_emojis.get(num, "•")

            # Extract pillar title from text
            # Format: "(TEAM STRENGTH): actual text..."
            title_match = re.match(
                r'\s*\(([^)]+)\):\s*([\s\S]+)', pillar_text
            )
            if title_match:
                title = title_match.group(1)
                content = title_match.group(2).strip()

                # Trim content to 2 sentences max
                sentences = content.split(". ")
                short = ". ".join(sentences[:2])
                if len(sentences) > 2:
                    short += "."

                pillar_lines += (
                    f"\n{emoji} <b>{title}</b>\n"
                    f"┗ {short}\n"
                )
            i += 2
    else:
        # No pillar format — just trim the reason
        sentences = reason.split(". ")
        pillar_lines = ". ".join(sentences[:3]) + "."

    # ── Extract alignment line ────────────────────────────
    alignment = ""
    if "ALIGNMENT:" in reason:
        alignment_part = reason.split("ALIGNMENT:")[-1].strip()
        # Take first sentence only
        alignment = alignment_part.split(".")[0].strip() + "."

    # ── Build the message ─────────────────────────────────
    report = (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧠 <b>V3 INTELLIGENCE REPORT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"\n"
        f"⚽ <b>MATCH</b>\n"
        f"┗ {match_line}\n"
        f"\n"
        f"{verdict_emoji} <b>VERDICT</b>\n"
        f"┗ <b>{verdict}</b>\n"
        f"\n"
        f"📊 <b>CONFIDENCE</b>\n"
        f"┗ {confidence_badge} — {confidence}%\n"
        f"\n"
        f"📋 <b>PILLAR ANALYSIS</b>"
        f"{pillar_lines}"
    )

    # Add alignment summary if found
    if alignment:
        report += (
            f"\n🎯 <b>ALIGNMENT</b>\n"
            f"┗ {alignment}\n"
        )

    report += f"\n━━━━━━━━━━━━━━━━━━━━━━"

    send_alert(report)
    
def send_pipeline_failure(step, error_message):
    """Send an alert when something goes wrong."""
    alert = f"""
⚠️ <b>PIPELINE FAILURE</b>

🔴 <b>Step:</b> {step}
❌ <b>Error:</b> {error_message}

Manual intervention required.
    """
    send_alert(alert)