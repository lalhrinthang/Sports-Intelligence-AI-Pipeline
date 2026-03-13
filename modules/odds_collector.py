import os
import requests
from dotenv import load_dotenv
from logger import log_step

load_dotenv() # Load environment variables from .env file

API_KEY = os.getenv('ODDS_API_KEY') # Get the Odds API key from environment variables
BASE_URL = "https://api.the-odds-api.com/v4/" # Base URL for the Odds API

# Which sports to collect odds for? Use the API endpoint to get the list of supported sports and their keys.

SPORTS_TO_WATCH = ["soccer_epl", "scoccer_uefa_champs_league"]

def get_upcoming_matches():
    """Fetch upcoming matches for the specified sports."""
    all_matches = []
    
    for sport_key in SPORTS_TO_WATCH:
        try:
            url = f"{BASE_URL}/sports/{sport_key}/events"
            
            params = {
                "apiKey": API_KEY,
                #@ Todo: Add more parameters as needed (e.g., regions, markets, oddsFormat)
            }
            response = requests.get(url, params=params,timeout=10) #add timeout to prevent hanging
            
            response.raise_for_status() # Raise an exception for HTTP errors
            matches = response.json() # Parse the JSON response
            
            log_step("ODDS_API", "SUCCESS", f"Got {len(matches)} matches for {sport_key}") # Log the successful fetching of matches
            all_matches.extend(matches) # Add the matches to the overall list
        except Exception as e:
            log_step("ODDS_API", "ERROR", f"Unexpected Error: {sport_key}: {e}") # Log any errors that occur while fetching matches
            
    return all_matches # Return the list of all upcoming matches across the specified sports    