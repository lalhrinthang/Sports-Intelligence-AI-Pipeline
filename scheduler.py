from datetime import datetime, timezone, timedelta
from modules.odds_collector import get_upcoming_matches
from logger import log_step

def get_matches_starting_soon(window_minutes=120):
    """
    Get matches that are starting within the next 'window_minutes' minutes.
    Uses UTC time for all comparisons to avoid timezone issues.
    """
    
    #Get the current time in UTC
    now_utc = datetime.now(timezone.utc)
    
    #window end time is current time + window_minutes
    window_end = now_utc + timedelta(minutes=window_minutes)
    
    log_step("SCHEDULER", "RUNNING",
             f"Now (UTC): {now_utc.strftime('%Y-%m-%d %H:%M:%S')} | "
             f"Window end: {window_end.strftime('%H:%M:%S')} UTC")
    
    #Fetch all upcoming matches
    all_matches = get_upcoming_matches()
    
    if not all_matches:
        log_step("SCHEDULER", "IDLE", "No matches returned from API")
        return []
    
    matches_starting_soon = [] 
    
    for match in all_matches:
        try:
            # API returns time in --> "2026-03-14T15:00:00Z" format, 
            # parse it to a datetime object
            
            raw_time  = match.get('commence_time','')
            if not raw_time:
                continue # Skip if no commence_time is provided
            
            start_utc  = datetime.fromisoformat(raw_time.replace('Z', '+00:00')) 
            # Convert the time string to a datetime object (handle 'Z' for UTC)
            diff_seconds = (start_utc - now_utc).total_seconds()
            diff_minutes = diff_seconds / 60
        
            home = match.get('home_team','Unknown') 
            away = match.get('away_team','Unknown') 
            sport = match.get('sport_key','Unknown')
            
            # Categorize the match for clear logging
            if diff_minutes < 0:
                status = f"PAST ({abs(diff_minutes):.0f} min ago)"
            elif diff_minutes <= window_minutes:
                status = f"IN WINDOW ({diff_minutes:.0f} min away)"
            else:
                status = f"TOO EARLY ({diff_minutes:.0f} min away)"

            log_step("SCHEDULER", "CHECKING",
                     f"{home} vs {away} | {status}")
            # Is it within our window?
            # diff_minutes >= -5 allows matches that just started
            # (small buffer for late pipeline triggers)
            if 0 <= diff_minutes <= window_minutes:
                log_step("SCHEDULER", "MATCH_FOUND",
                         f"✅ {home} vs {away} | "
                         f"Sport: {sport} | "
                         f"Starts in {diff_minutes:.0f} min")
                matches_starting_soon.append(match)
                
        except Exception as e:
            log_step("SCHEDULER", "PARSE_ERROR", f"Could not parse time for match {home} vs {away}: {e}") 
            
            continue # Skip to the next match
        
    # Summary log
    if matches_starting_soon:
        log_step("SCHEDULER", "SUMMARY",
                 f"Found {len(matches_starting_soon)} match(es) "
                 f"in next {window_minutes} min")
    else:
        log_step("SCHEDULER", "IDLE",
                 f"No matches starting within "
                 f"the next {window_minutes} minutes")

    return matches_starting_soon