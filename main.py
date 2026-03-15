import time
import schedule
from datetime import datetime, timedelta

from logger import log_step
from scheduler import get_matches_starting_soon
from pipeline import process_match
from modules.database import init_db
from modules.telegram_bot import send_alert

#need schedule to run a function every X minutes that checks for matches starting in the next 15 minutes, then calls process_match for each one

def run_schedule_check():
    """
    Called every 60 seconds by the scheduler loop.
    Checks for upcoming matches and triggers the pipeline.
    """
    log_step("MAIN","HEARTBEAT",f"Checking schedule at " f"{datetime.now().strftime('%H:%M:%S')}")
    # Change  ==> 15 min
    upcoming = get_matches_starting_soon(window_minutes=120) # Check for matches starting in the next 30 minutes
    
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
    
    #initialize the database (creates tables if they don't exist)
    init_db()
    
    # alert that the pipeline has started successfully
    send_alert(
        "🟢 <b>V3 Syndicate Pipeline Started</b>\n"
        "Monitoring match schedule every 60 seconds.\n"
        f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    log_step("MAIN", "STARTED", "Pipeline started successfully. Entering main loop.")
    
    #repeat every 60 seconds
    schedule.every(60).seconds.do(run_schedule_check)
    
    log_step("MAIN", "SCHEDULER", "Entering main loop")
    
    while True:
        try:
            schedule.run_pending() # Run any scheduled tasks that are due
            time.sleep(1) # Sleep briefly to avoid busy-waiting
        except KeyboardInterrupt:
            log_step("MAIN", "STOPPED", "Stopped by user (Ctrl+C)")
            send_alert("🔴 <b>Pipeline stopped</b> — manual shutdown.")
            break
        except Exception as e:
            # Unexpected crash — log, alert, and keep going
            log_step("MAIN", "CRASH",
                     f"Main loop error: {e}")
            send_alert(
                f"🔴 <b>Pipeline crash</b>\n"
                f"Error: {str(e)[:300]}\n"
                f"Restarting loop in 30 seconds..."
            )
            time.sleep(30)   # Wait before retrying


if __name__ == "__main__":
    main()