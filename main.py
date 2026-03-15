import time
import schedule
from datetime import datetime, timedelta

from logger import log_step
from scheduler import get_matches_starting_soon
from pipeline import process_match
from modules.database import init_db
from modules.telegram_bot import send_alert

def main():
    """
    Entry point. Starts the pipeline and keeps it running forever.
    """

    print("=" * 55)
    print("   V3 SYNDICATE AUTOMATION PIPELINE")
    print("=" * 55)