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

def load_prompt(validated_data) -> str:
    """
    Load Claude's prompt from opus_strategist.txt
    and inject the validated intelligence data.
    """
    try:
        with open("prompts/opus_strategist.txt", "r") as f:
            template = f.read()

        # ── Convert to dict safely ────────────────────────
        # Handle Pydantic v2
        if hasattr(validated_data, "model_dump"):
            data_dict = validated_data.model_dump()

        # Handle Pydantic v1
        elif hasattr(validated_data, "dict"):
            data_dict = validated_data.dict()

        # Already a dict — use directly
        elif isinstance(validated_data, dict):
            data_dict = validated_data

        # Unknown type — log and fail safely
        else:
            log_step("CLAUDE", "FAILURE",
                     f"Unknown data type: {type(validated_data)}")
            return None

        data_str = json.dumps(data_dict, indent=2)
        prompt   = template.replace("{intelligence_data}", data_str)

        log_step("CLAUDE", "PROMPT_LOADED",
                 f"Prompt ready — {len(prompt)} characters")

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
    
    # ── Safety check on input ─────────────────────────────
    # Get match_id safely regardless of object type
    if hasattr(validated_data, "match_id"):
        match_id = validated_data.match_id        # Pydantic object
    elif isinstance(validated_data, dict):
        match_id = validated_data.get("match_id", "unknown")  # dict
    else:
        log_step("CLAUDE", "FAILURE",
                 f"Invalid input type: {type(validated_data)}")
        return None

    log_step("CLAUDE", "STARTING",
             f"Running V3 Audit for match: {match_id}")
    #Load and prepare the prompt
    prompt = load_prompt(validated_data)
    if not prompt:
        log_step("CLAUDE", "FAILED", "Could not load prompt. Aborting audit.")
        return None
    try:
        # Call the Anthropic API with the prepared prompt
        log_step("CLAUDE", "CALLING_API", "Sending request to Anthropic API...")
        
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
        
        log_step("CLAUDE", "RESPONSE_RECEIVED", 
                 f"Got {len(raw_text)} characters")
        
        # clean and parse the response
        cleaned_text = clean_json_response(raw_text)
        verdict_data = json.loads(cleaned_text)
        
        # make sure we have all the expected fields
        required = ["match_id","verdict","reason","confidence"]
        missing  = [f for f in required if f not in verdict_data]
        
        if missing:
            raise ValueError(
                f"Claude response missing fields: {missing}"
            )

        log_step("CLAUDE", "SUCCESS",
                 f"Verdict: {verdict_data['verdict']} | "
                 f"Confidence: {verdict_data['confidence']}%")

        return verdict_data
    
    except json.JSONDecodeError as e:
        log_step("CLAUDE", "HAIKU_FAILED",
                 f"Claude returned invalid JSON: {e}")
        return run_v3_audit_sonnet_fallback(validated_data)  # Try the fallback if JSON parsing fails 
    except ValueError as e:
        log_step("CLAUDE", "HAIKU_FAILED",
                 f"Missing fields from Haiku: {e}")
        return run_v3_audit_sonnet_fallback(validated_data)

        # Fallback can use sonnet or opus model, this is optional to change
    except Exception as e:
        log_step("CLAUDE", "HAIKU_API_ERROR", f"Claude HAIKU API error: {e}")
        return None
    
def run_v3_audit_sonnet_fallback(validated_data) -> dict | None:
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