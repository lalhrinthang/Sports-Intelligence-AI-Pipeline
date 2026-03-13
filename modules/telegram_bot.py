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

def send_intelligence_report(verdict,reason,confidence,match_id):
    """Send a formatted V3 Intelligence Report."""
    report = f"""
                🧠 <b>V3 INTELLIGENCE REPORT</b>

                📋 <b>Match ID:</b> {match_id}
                ⚖️ <b>Verdict:</b> {verdict}
                📊 <b>Confidence:</b> {confidence}%
                💡 <b>Reason:</b> {reason}
                
                """
    send_alert(report) # Send the formatted intelligence report as an alert
    
