import decimal
import os
import requests
from dotenv import load_dotenv
from logger import log_step

load_dotenv() # Load environment variables from .env file

API_KEY = os.getenv('ODDS_API_KEY') # Get the Odds API key from environment variables
BASE_URL = "https://api.the-odds-api.com/v4/" # Base URL for the Odds API

# Which sports to collect odds for? Use the API endpoint to get the list of supported sports and their keys.

SPORTS_TO_WATCH = ["soccer_epl", "soccer_uefa_champs_league","soccer_spain_la_liga","soccer_germany_bundesliga","soccer_italy_serie_a","soccer_france_ligue_one"] # List of sport keys to watch (e.g., soccer_epl for English Premier League)

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
            
        except requests.exceptions.HTTPError as http_err:
            log_step("ODDS_API", "FAILURE", f"HTTP error occurred for {sport_key}: {http_err}") # Log HTTP errors
            
        except requests.exceptions.RequestException as req_err:
            log_step("ODDS_API", "FAILURE", f"Request error occurred for {sport_key}: {req_err}") # Log request errors (e.g., connection issues, timeouts)
        
        except requests.exceptions.ConnectionError:
            log_step("ODDS_API","FAILURE", "No Internet Connection")
            
        except Exception as e:
            log_step("ODDS_API", "FAILURE", f"Unexpected Error: {sport_key}: {e}") # Log any errors that occur while fetching matches
            
    return all_matches # Return the list of all upcoming matches across the specified sports    

def get_match_odds(sport_key, match_id):
    """Fetch odds for a specific match."""
    try:
        url = f"{BASE_URL}/sports/{sport_key}/odds"
        
        params = {
            "apiKey": API_KEY,
            "regions": "eu", # Specify regions if needed 
            "markets": "h2h", # Specify markets if needed
            "oddsFormat": "decimal" # Specify odds format if needed
        }
        response = requests.get(url, params=params,timeout=10) #add timeout to prevent hanging
        response.raise_for_status() # Raise an exception for HTTP errors
        all_odds = response.json() # Parse the JSON response
    
    except requests.exceptions.HTTPError as http_err:
        log_step("ODDS_API", "FAILURE", f"HTTP error occurred for {sport_key} - {match_id}: {http_err}") # Log HTTP errors
        return None # Return None if there was an error fetching odds for the match
    except requests.exceptions.RequestException as req_err:
        log_step("ODDS_API", "FAILURE", f"Request error occurred for {sport_key} - {match_id}: {req_err}") # Log request errors
        return None # Return None if there was an error fetching odds for the match
    except Exception as e:
        log_step("ODDS_API", "FAILURE", f"Unexpected Error: {sport_key} - {match_id}: {e}") # Log any errors that occur while fetching odds
        return None # Return None if there was an error fetching odds for the match 
    