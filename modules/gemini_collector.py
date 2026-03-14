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