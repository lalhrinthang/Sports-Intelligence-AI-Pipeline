import os
import asyncio
from dotenv import load_dotenv # Load environment variables from .env file
from telegram import Bot, Update # Telegram Bot API classes
from logger import log_step # Import the logging function from logger.py