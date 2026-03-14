import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from logger import log_step

load_dotenv()

# Configure Gemini with our API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def load_prompt(match_data: dict) -> str:
    """ Read the prompt from gemini_hunter.txt and inject the match data into it. """
    try:
        with open("prompts/gemini_hunter.txt", "r") as f:
            prompt_template = f.read()
            
        # Convert the match data to a pretty-printed JSON string for better readability in the prompt
        match_data_str = json.dumps(match_data, indent=2) # Convert match data to a pretty-printed JSON string
        # Inject the match data into the prompt template
        prompt = prompt_template.replace("{match_data}", match_data_str) # Inject the match data into the prompt template
        return prompt
    
    except FileNotFoundError:
        log_step("GEMINI_COLLECTOR", "FAILURE", "Prompt file not found: prompts/gemini_hunter.txt") # Log if the prompt file is not found
        return None
    
    except Exception as e:
        log_step("GEMINI_COLLECTOR", "FAILURE", f"Error loading prompt: {e}") # Log any other errors that occur while loading the prompt
        return None
    
    # Main function to collect insights for a match
    def collect_match_insights(match_data:dict) -> dict | None: 
        """
        Send match data to Gemini Pro.
        Gemini searches the web and returns a rich JSON.

        Returns: dict if successful, None if anything fails.
        """
        match_id = match_data.get("id", "unknown")
        home_team = match_data.get("home_team", "?")
        away_team = match_data.get("away_team", "?")
        
        log_step("GEMINI_COLLECTOR", "STARTING", f"Collecting insights for match (ID: {match_id}) ({home_team} vs {away_team})") # Log the start of the insight collection process   
        
        prompt = load_prompt(match_data)
        
        if not prompt:
            log_step("GEMINI_COLLECTOR", "FAILED", f"Failed to load prompt for match (ID: {match_id})") # Log if the prompt could not be loaded
            return None
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                tools="google_search_retrival"
            )
            log_step("GEMINI", "CALLING API", "Sending prompt to Gemini Pro API")
            response = model.generate_content(prompt)
            log_step("GEMINI", "API RESPONSE RECEIVED", "Received response from Gemini Pro API")
            
        except Exception as e:
            log_step("GEMINI", "FAILURE", f"Gemini API Error: {e}")
            return None