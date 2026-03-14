from pydantic import BaseModel, ValidationError, validator
from logger import log_step

class MatchData(BaseModel):
    match_id: str
    lineups_injuries: str
    odds_movements: str
    recent_form: str
    weather: str
    public_sentiment: str
    
    @validator('*', pre=True) # Validate that all fields are non-empty strings
    def field_must_be_empty(cls,value,field):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field.name} must be a non-empty string")
        return value
    
    @validator('*')
    def warn_if_unavailable(cls, value, field):
        if value == "Data Unavailable":
            log_step("VALIDATION", "WARNING", f"{field.name} is marked as 'Data Unavailable'. This may impact the quality of insights.")
            return value

def validate_match_data(raw_data: dict) -> MatchData | None:
    
    log_step("VALIDATION","RUNNING", f"Checking {len(raw_data)} fieldss for match data validity")
    
    try:
        validated = MatchData(**raw_data)
        
        log_step("VALIDATION", "SUCCESS", f"All fields valid for match: {validated.match_id}")
        
        return validated
    
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