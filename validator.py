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