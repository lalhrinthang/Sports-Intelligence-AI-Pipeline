import os
import sys
import anthropic
from dotenv import load_dotenv
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import log_step
from validator import MatchData
import json

load_dotenv()

# Debug: check if key is loading
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    log_step("Claude Strategist", "FAILED", "API key not found! Check your .env file.")
else:
    log_step("Claude Strategist", "SUCCESS", "API key loaded successfully.")
    
# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=api_key)

def load_prompt(validated_data: MatchData):
    """
    Load Claude's prompt from opus_strategist.txt
    and inject the validated intelligence data.
    """
    try:
        with open("prompts/opus_strategist.txt", "r") as file:
            prompt_template = file.read()
        
        data_dict = validated_data.model_dump()  # Convert MatchData to a dictionary
        data = json.dumps(data_dict, indent=2)  # Convert dictionary to a pretty-printed JSON string
        prompt = prompt_template.replace("{intelligence_data}", data) # Inject the JSON string into the prompt template

        return prompt
    except FileNotFoundError:
        log_step("Claude", "FAILURE", "Prompt file not found: prompts/opus_strategist.txt")
        return None
    except Exception as e:
        log_step("Claude", "FAILURE", f"Error loading prompt: {str(e)}")
        return None
    
    # Main Function to get Claude's verdict
def run_v3_audit(validated_data: MatchData):
    
    """
    Send validated intelligence to Claude for the V3 Audit.

    IMPORTANT: Claude has NO tool access here.
    It only sees the data we inject into the prompt.

    Returns: dict with verdict, reason, confidence — or None on failure
    """
    
    match_id = validated_data.match_id
    log_step("CLAUDE", "STARTING",
             f"Running V3 Audit for match: {match_id}")
    
    #Load and prepare the prompt
    prompt = load_prompt(validated_data)
    if not prompt:
        log_step("CLAUDE", "FAILED", "Could not load prompt. Aborting audit.")
        return None
    try:
        # Call the Anthropic API with the prepared prompt
        log_step("CLAUDE", "RUNNING", "Sending request to Anthropic API...")
        
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                 }
            ]
        )
        # Extract and return the relevant information from Claude's response
        raw_text = response.content[0].text.strip()
        
        log_step("CLAUDE", "RESPONSE_RECEIVED", f"Got {len(raw_text)} characters")
        
        # clean and parse the response
        cleaned_text = clean_json_response(raw_text)
        verdict_data = json.loads(cleaned_text)
        
        # make sure we have all the expected fields
        required_fields = ["match_id","verdict","reason","confidence"]
        
        for field in required_fields:
            if field not in verdict_data:
                log_step("CLAUDE", "FAILED", f"Missing field in response: {field}")
                
                raise ValueError(f"Missing field in response: {field}")
        log_step("CLAUDE", "SUCCESS",
                 f"Verdict: {verdict_data['verdict']} | "
                 f"Confidence: {verdict_data['confidence']}%")
        
        return verdict_data
    
    except json.JSONDecodeError as e:
        log_step("CLAUDE", "FAILURE",
                 f"Claude returned invalid JSON: {e}")
        return run_v3_audit_sonnet_fallback(validated_data)  # Try the fallback if JSON parsing fails 
    
        # Fallback can use sonnet or opus model, this is optional to change
    except Exception as e:
        log_step("CLAUDE", "FAILURE", f"Claude API error: {e}")
        return None
    
def run_v3_audit_sonnet_fallback(
        validated_data: MatchData) -> dict | None:
    """
    Fallback to Claude Sonnet if Haiku fails.
    More affordable but less reliable.
    """

    log_step("CLAUDE", "FALLBACK",
             "Haiku failed — trying Claude Sonnet...")

    prompt = load_prompt(validated_data)
    if not prompt:
        return None

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_text = response.content[0].text.strip()
        cleaned = clean_json_response(raw_text)
        verdict_data = json.loads(cleaned)

        log_step("CLAUDE", "SONNET_SUCCESS",
                 f"Sonnet verdict: {verdict_data.get('verdict')}")

        return verdict_data

    except Exception as e:
        log_step("CLAUDE", "TOTAL_FAILURE",
                 f"Both Sonnet and Haiku failed: {e}")
        return None      
        
def clean_json_response(text: str) -> str:
    """Strip markdown code fences if present."""
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()