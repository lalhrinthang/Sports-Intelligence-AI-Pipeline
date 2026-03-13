import os
import asyncio
from dotenv import load_dotenv # Load environment variables from .env file
from telegram import Bot, Update # Telegram Bot API classes
from logger import log_step # Import the logging function from logger.py

load_dotenv() # Load environment variables from .env file

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') # Get the Telegram bot token from environment variables
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') # Get the Telegram chat ID from environment variables