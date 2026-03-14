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
    
    for match in all_matches:
        try:
            # API returns time in --> "2026-03-14T15:00:00Z" format, parse it to a datetime object
            start_time_str = match.get('commence_time','') # Get the commence_time from the match data
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00')) # Convert the time string to a datetime object (handle 'Z' for UTC)
            
            # check --> within the time window
            if now <=start_time <= window_end:
                home = match.get('home_team','Unknown') # Get the home team name, default to 'Unknown' if not available
                away = match.get('away_team','Unknown') # Get the away team name, default to 'Unknown' if not available
                
                log_step("SCHEDULER", "MATCH_FOUND", f"{home} vs {away} starts at {start_time.strftime('%H:%M')} UTC") # Log the match that is starting soon
                matches_starting_soon.append(match) # Add the match to the list of matches starting soon
        except Exception as e:
            log_step("SCHEDULER", "ERROR", f"Error processing match data: {e}") # Log any errors that occur while processing match data
            
            continue # Skip to the next match if there was an error processing the current match
        
        if not matches_starting_soon:
            log_step("SCHEDULER", "IDLE", f"No matches starting within the next {window_minutes} minutes") # Log if no matches are starting soon'
        
        return matches_starting_soon # Return the list of matches starting within the time window