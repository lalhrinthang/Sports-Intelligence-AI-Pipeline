from logger import log_step
from modules.gemini_collector import collect_match_insights
from modules.gemini_collector import collect_match_insights
from validator import validate_match_data
from modules.database import is_match_processed, save_verdict
from modules.claude_strategist import run_v3_audit
from modules.telegram_bot import (send_intelligence_report,send_pipeline_failure)

def process_match(match: dict):
    """
    Full pipeline for one match.
    Runs Gemini → Validator → Claude → Telegram → Database.

    This function is called by main.py for each match
    that the scheduler finds in the 15-minute window.
    """

    # Extract basic info
    match_id   = match.get("id", "unknown")
    sport_key  = match.get("sport_key", "unknown") # we can use this to filter for soccer matches only if needed
    home_team  = match.get("home_team", "Unknown")
    away_team  = match.get("away_team", "Unknown")
    start_time = match.get("commence_time", "Unknown")
    
    log_step("PIPELINE","STARTING",f"Processing match: => {home_team} vs {away_team} at {start_time}")
    
    # Check if match has already been processed
    if is_match_processed(match_id):
        log_step("PIPELINE","SKIPPED",f"Match {home_team} vs {away_team} already processed. Skipping.")
        return #skip to next match in scheduler loop
    
    log_step("PIPELINE","STEP-1",f"Running Gemini audit for ....")
    
    intelligence = collect_match_insights(match)
    
    if not intelligence:
        error_msg = f"Gemini failed for {home_team} vs {away_team}"
        log_step("PIPELINE", "FAILURE", error_msg)
        send_pipeline_failure("GEMINI_COLLECTOR", error_msg)
        return   # Stop here — do not call Claude
    
    # Step - 2 : Pydantic validation of Gemini's insights
    log_step("PIPELINE","STEP-2",f"Validating Gemini insights for {home_team} vs {away_team}")
    
    result = validate_match_data(intelligence)
    # Safely unpack — validate_intelligence always returns tuple
    if not isinstance(result, tuple) or len(result) != 2:
        error_msg = "Validator returned unexpected format"
        log_step("PIPELINE", "FAILURE", error_msg)
        send_pipeline_failure("PYDANTIC_VALIDATOR", error_msg)
        return

    validated, error = result
    if validated is None:
        # Validation failed — alert and stop
        log_step("PIPELINE", "FAILURE", f"Validation failed: {error}")
        send_pipeline_failure("PYDANTIC_VALIDATOR", str(error))
        return
    
    # Extra safety check — confirm it's actually a Pydantic object
    if isinstance(validated, dict):
        error_msg = (
            "Validator returned a dict instead of "
            "Pydantic object — check validate_intelligence()"
        )
        log_step("PIPELINE", "FAILURE", error_msg)
        send_pipeline_failure("PYDANTIC_VALIDATOR", error_msg)
        return

    log_step("PIPELINE", "VALIDATED",
             f"Data clean for: {validated.match_id}")
    
    # Step 3: Run Claude audit to get verdict, confidence, and reason
    log_step("PIPELINE","STEP-3",
             f"Running Claude audit for "
             f"{home_team} vs {away_team}")
    # Log the type before sending — confirms it's Pydantic
    log_step("PIPELINE", "DEBUG",
             f"Type going into Claude: {type(validated).__name__}")
    verdict_data = run_v3_audit(intelligence)
    
    if not verdict_data:
        error_msg = f"Claude audit failed for match {match_id}"
        log_step("PIPELINE", "FAILURE", error_msg)
        send_pipeline_failure("CLAUDE_STRATEGIST", error_msg)
        return   # Stop here — do not save to database
    # Step 4: Save verdict to database and send Telegram report
    log_step("PIPELINE","STEP-4",f"Sending intelligence report to Telegram for match {match_id}")
    
    send_intelligence_report(
        verdict=verdict_data["verdict"],
        reason=verdict_data["reason"],
        confidence=verdict_data["confidence"],
        match_id=match_id,
        home_team=home_team,
        away_team=away_team
    )
    
    log_step("PIPELINE", "COMPLETE",
             f"Done: {home_team} vs {away_team} | "
             f"Verdict: {verdict_data['verdict']} | "
             f"Confidence: {verdict_data['confidence']}%")
    # ── Step 5: Save to database ─────────────────────────
    log_step("PIPELINE", "STEP_5", "Saving to database...")

    save_verdict(
        match_id=match_id,
        home=home_team,
        away=away_team,
        verdict=verdict_data.get("verdict", "Unknown"),
        confidence=verdict_data.get("confidence", 0),
        reason=verdict_data.get("reason", "")
    )

    log_step("PIPELINE", "COMPLETE",
             f"Done: {home_team} vs {away_team} | "
             f"Verdict: {verdict_data.get('verdict')} | "
             f"Confidence: {verdict_data.get('confidence')}%")