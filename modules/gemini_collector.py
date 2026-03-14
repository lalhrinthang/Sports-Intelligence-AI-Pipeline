import os
import json
# import google.generativeai as genai
from google import genai
from google.genai import types
from dotenv import load_dotenv
from logger import log_step
# Free tier has limits. Fix: Add a delay between calls
import time
time.sleep(2)  # Wait 2 seconds before calling Gemini

load_dotenv()

# Configure Gemini with our API key
client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

def load_prompt(match_data: dict) -> str:
    """ Read the prompt from gemini_hunter.txt and inject the match data into it. """
    try:
        with open("prompts/gemini_hunter.txt", "r") as f:
            prompt_template = f.read()
        match_data_str = json.dumps(match_data, indent=2) 
        prompt = prompt_template.replace("{match_data}", match_data_str) 
        return prompt
    
    except FileNotFoundError:
        log_step("GEMINI_COLLECTOR", "FAILURE", "Prompt file not found: prompts/gemini_hunter.txt") 
        return None
    
    except Exception as e:
        log_step("GEMINI_COLLECTOR", "FAILURE", f"Error loading prompt: {e}") 
        return None
    
# Main function to collect insights for a match
def collect_match_insights(match_data:dict) -> dict | None: 
        """
        Send match data to Gemini.
        Gemini searches the web and returns a rich JSON.

        Returns: dict if successful, None if anything fails.
        """
        match_id = match_data.get("id", "unknown")
        home_team = match_data.get("home_team", "?")
        away_team = match_data.get("away_team", "?")
        
        log_step("GEMINI_COLLECTOR", "STARTING", f"Collecting insights for match (ID: {match_id}) ({home_team} vs {away_team})") # Log the start of the insight collection process   
        
        prompt = load_prompt(match_data)
        
        if not prompt:
            log_step("GEMINI", "FAILED", f"Failed to load prompt for match (ID: {match_id})") # Log if the prompt could not be loaded
            return None
        try:
            google_search_tool = types.Tool(
                google_search = types.GoogleSearch()
            )
            log_step("GEMINI", "CALLING API", "Sending prompt to gemini 2.5 flash API with Google Search tool enabled")
            
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[google_search_tool],  
                    thinking_config=types.ThinkingConfig(thinking_budget=1024)
                )
            )
            # response = model.generate_content(prompt)
            
            log_step("GEMINI", "API RESPONSE RECEIVED", "Received response from Gemini API")
            
            # Extract the JSON content from the response
            raw_text = response.text.strip()
            log_step("GEMINI", "RESPONSE RECEIVED", f"Got {len(raw_text)} characters back")
            
            clean_text = clean_json_response(raw_text)
            
            insights = json.loads(clean_text) 
            
            log_step("GEMINI", "SUCCESS", f"Successfully collected insights for match (ID: {match_id})")
            
            return insights
        except json.JSONDecodeError as json_err:
            log_step("GEMINI", "FAILURE", f"JSON decoding error for match (ID: {match_id}): {json_err}")
            
            log_step("GEMINI", "RAW RESPONSE", f"Raw response was: {raw_text[:300]}")
            
            return None
        except Exception as e:
            log_step("GEMINI", "FAILURE", f"Gemini API Error: {e}")
            return None
        
def clean_json_response(text: str) -> str:
    """
        Remove markdown code fences if Gemini included them.

        Example input:  ```json\n{...}\n```
        Example output: {...}
    """ 
    # Remove ```json at the start
    if text.startswith("```json"):
        text = text[7:]

        # Remove ``` at the start (without "json")
    elif text.startswith("```"):
        text = text[3:]

        # Remove ``` at the end
    if text.endswith("```"):
        text = text[:-3]

    return text.strip()