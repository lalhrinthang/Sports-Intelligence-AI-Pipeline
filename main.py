import time
import schedule
from datetime import datetime, timedelta

from logger import log_step
from scheduler import get_matches_starting_soon
from pipeline import process_match
from modules.database import init_db
from modules.telegram_bot import send_alert

#need schedule to run a function every X minutes that checks for matches starting in the next 15 minutes, then calls process_match for each one

def run__schedule_check():
    """
    Called every 60 seconds by the scheduler loop.
    Checks for upcoming matches and triggers the pipeline.
    """
    log_step("MAIN","HEARTBEAT",f"Checking schedule at " f"{datetime.now().strftime('%H:%M:%S')}")
    
    upcoming = get_matches_starting_soon(window_minutes=15)
    
    if not upcoming:
        log_step("MAIN","IDLE",f"No matches starting in the next 15 minutes.")
        return
    
    log_step("MAIN", "MATCHES_FOUND",
             f"{len(upcoming)} match(es) to process")
    
    for match in upcoming:
        try:
            process_match(match)
        except Exception as e:
            # if one match fails, we log it but continue with the others
            # this prevents one bad match from breaking the whole pipeline
            
            log_step("MAIN", "MATCH_ERROR",
                     f"Unhandled error for match "
                     f"{match.get('id')}: {e}")
            
            send_alert(
                f"⚠️ <b>Unhandled Error</b>\n"
                f"Match: {match.get('home_team')} vs "
                f"{match.get('away_team')}\n"
                f"Error: {str(e)[:200]}"
            )


def main():
    """
    Entry point. Starts the pipeline and keeps it running forever.
    """

    print("=" * 55)
    print("   V3 SYNDICATE AUTOMATION PIPELINE")
    print("=" * 55)
    