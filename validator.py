from pydantic import BaseModel, ValidationError, field_validator
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import log_step

class MatchData(BaseModel):
    match_id: str
    lineups_injuries: str
    odds_movements: str
    weather: str
    public_sentiment: str
    
    @field_validator('*', mode='before')
    @classmethod
    def field_must_not_be_empty(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Field must be a non-empty string")
        return value
    
    @field_validator('*', mode='after')
    @classmethod
    def warn_if_unavailable(cls, value):
        if value == "Data Unavailable":
            log_step("VALIDATION", "WARNING", "Field is marked as 'Data Unavailable'. This may impact the quality of insights.")
        return value

def validate_match_data(raw_data: dict):
    """
    Validate Gemini's JSON against our schema.

    Returns:
        (validated_object, None)    → if PASS
        (None, error_string)        → if FAIL
        
    """
    log_step("VALIDATION","RUNNING", f"Checking {len(raw_data)} fields for match data validity")
    # Guard: make sure input is actually a dict
    if not isinstance(raw_data, dict):
        error = f"Expected dict, got {type(raw_data).__name__}"
        log_step("VALIDATOR", "FAILURE", error)
        return None, error
    try:
        validated = MatchData(**raw_data)
        
        log_step("VALIDATION", "SUCCESS", f"All fields valid for match: {validated.match_id}")
        
        return validated , None
    
    except ValidationError as e:
        error_messages = []
        
        for error in e.errors():
            field = error.get('loc',["unknown"])[0]
            message = error.get('msg', 'Unknown error')
            error_messages.append(f"{field}: {message}")
            
        formatted_errors = " | ".join(error_messages)
        
        log_step("VALIDATION", "FAILURE", f"Validation failed - {formatted_errors}")
        
        return None, formatted_errors
    
    except Exception as e:
        log_step("VALIDATION", "FAILURE", f"Unexpected: {e}")
        return None, str(e)