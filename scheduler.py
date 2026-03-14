from datetime import datetime, timezone, timedelta
from modules.odds_collector import get_upcoming_matches
from logger import log_step

def get_matches_starting_soon(window_minutes=15):
    """Get matches that are starting within the next 'window_minutes' minutes."""
    
    #Get the current time in UTC
    now = datetime.now(timezone.utc)
    
    #window end time is current time + window_minutes
    window_end = now + timedelta(minutes=window_minutes)
    
    log_step("SCHEDULER", "RUNNING", f"Checking matches between {now.strftime('%H:%M')}" f" and {window_end.strftime('%H:%M')} UTC") # Log the time window being checked for matches
    
    #Fetch all upcoming matches
    all_matches = get_upcoming_matches()
    
    matches_starting_soon = [] # List to hold matches starting within the time window
    
    