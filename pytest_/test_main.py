import pytest
import sys
import os
from pipeline import process_match
# Make sure Python can find our modules
# sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch, MagicMock
from pipeline import process_match
from main import run_schedule_check


# ── Shared test data ─────────────────────────────────────────────────

SAMPLE_MATCH = {
    "id": "test_001",
    "sport_key": "soccer_epl",
    "home_team": "Arsenal",
    "away_team": "Man City",
    "commence_time": "2026-03-14T15:00:00Z"
}

GOOD_INTELLIGENCE = {
    "match_id": "test_001",
    "lineups_injuries": (
        "Arsenal: Raya; White, Saliba, Gabriel, Zinchenko; "
        "Rice, Odegaard; Saka, Havertz, Trossard; Martinelli. "
        "Partey OUT. Man City: Ederson; Walker, Dias, Gvardiol; "
        "De Bruyne, Bernardo; Doku, Foden, Haaland. Rodri OUT."
    ),
    "odds_movement": (
        "Arsenal opened 2.40 now 2.10. Steam move detected. "
        "Man City drifted 3.10 to 3.50."
    ),
    "weather": "London 11C light rain wind 18kmh southwest.",
    "public_sentiment": (
        "78 percent backing Arsenal. Sharps and public aligned."
    )
}

GOOD_VERDICT = {
    "match_id": "test_001",
    "verdict": "Back Arsenal — Strong Value",
    "reason": (
        "Three of four pillars align for Arsenal. "
        "Steam move, key injury to Rodri, and public sentiment "
        "all point Arsenal."
    ),
    "confidence": 82
}

# ════════════════════════════════════════════════════════════════
# SCENARIO 1 — Happy Path (Everything works perfectly)
# ════════════════════════════════════════════════════════════════

class TestScenario1_HappyPath:
    """
    The ideal scenario. Every step succeeds.
    Expected: Telegram gets the V3 Intelligence Report.
    """

    @patch("pipeline.is_match_processed", return_value=False)
    @patch("pipeline.collect_match_insights",
           return_value=GOOD_INTELLIGENCE)
    @patch("pipeline.validate_match_data",
           return_value=(MagicMock(
               match_id="test_001",
               model_dump=lambda: GOOD_INTELLIGENCE
           ), None))
    @patch("pipeline.run_v3_audit", return_value=GOOD_VERDICT)
    @patch("pipeline.send_intelligence_report")
    @patch("pipeline.save_verdict")
    def test_full_pipeline_succeeds(
        self,
        mock_save,
        mock_telegram,
        mock_claude,
        mock_validate,
        mock_gemini,
        mock_db
    ):
        process_match(SAMPLE_MATCH)

        # Gemini was called once with our match
        mock_gemini.assert_called_once_with(SAMPLE_MATCH)

        # Claude was called once
        mock_claude.assert_called_once()

        # Telegram received the report
        mock_telegram.assert_called_once()
        call_args = mock_telegram.call_args[1]
        assert call_args["verdict"] == "Back Arsenal — Strong Value"
        assert call_args["confidence"] == 82

        # Verdict was saved to database
        mock_save.assert_called_once()

        print("✅ Scenario 1 passed: Full pipeline ran successfully")

# ════════════════════════════════════════════════════════════════
# SCENARIO 2 — Match Already Processed (Duplicate Prevention)
# ════════════════════════════════════════════════════════════════

class TestScenario2_AlreadyProcessed:
    """
    Match was already processed in a previous cycle.
    Expected: Pipeline exits early. Gemini never called.
    """

    @patch("pipeline.is_match_processed", return_value=True)
    @patch("pipeline.collect_match_insights")
    @patch("pipeline.send_intelligence_report")
    def test_skips_already_processed_match(
        self,
        mock_telegram,
        mock_gemini,
        mock_db
    ):
        process_match(SAMPLE_MATCH)

        # Gemini must NOT be called
        mock_gemini.assert_not_called()

        # Telegram must NOT receive a report
        mock_telegram.assert_not_called()

        print("✅ Scenario 2 passed: Duplicate match correctly skipped")

# ════════════════════════════════════════════════════════════════
# SCENARIO 3 — Gemini Fails (Returns None)
# ════════════════════════════════════════════════════════════════

class TestScenario3_GeminiFails:
    """
    Gemini Pro cannot fetch data (API down, quota exceeded etc).
    Expected: Telegram gets failure alert. Claude never called.
    """

    @patch("pipeline.is_match_processed", return_value=False)
    @patch("pipeline.collect_match_insights", return_value=None)
    @patch("pipeline.validate_match_data")
    @patch("pipeline.send_pipeline_failure")
    @patch("pipeline.run_v3_audit")
    def test_gemini_failure_stops_pipeline(
        self,
        mock_claude,
        mock_failure_alert,
        mock_validate,
        mock_gemini,
        mock_db
    ):
        process_match(SAMPLE_MATCH)

        # Pydantic must NOT run
        mock_validate.assert_not_called()

        # Claude must NOT run
        mock_claude.assert_not_called()

        # Failure alert must be sent to Telegram
        mock_failure_alert.assert_called_once()
        call_args = mock_failure_alert.call_args[0]
        assert "GEMINI" in call_args[0]

        print("✅ Scenario 3 passed: Gemini failure handled correctly")
        
        
# ════════════════════════════════════════════════════════════════
# SCENARIO 4 — Pydantic Validation Fails (Missing Fields)
# ════════════════════════════════════════════════════════════════

class TestScenario4_ValidationFails:
    """
    Gemini returns JSON but fields are missing or wrong.
    Expected: Telegram gets validation failure alert. Claude never called.
    """

    BAD_INTELLIGENCE = {
        "match_id": "test_001",
        "lineups_injuries": "Arsenal vs Man City",
        # Missing: odds_movement, weather, public_sentiment
    }

    @patch("pipeline.is_match_processed", return_value=False)
    @patch("pipeline.collect_match_insights",
           return_value=BAD_INTELLIGENCE)
    @patch("pipeline.run_v3_audit")
    @patch("pipeline.send_pipeline_failure")
    def test_validation_failure_stops_pipeline(
        self,
        mock_failure_alert,
        mock_claude,
        mock_gemini,
        mock_db
    ):
        process_match(SAMPLE_MATCH)

        # Claude must NOT run
        mock_claude.assert_not_called()

        # Failure alert must be sent
        mock_failure_alert.assert_called_once()
        call_args = mock_failure_alert.call_args[0]
        assert "VALIDATOR" in call_args[0]

        print("✅ Scenario 4 passed: Validation failure handled correctly")
        
# ════════════════════════════════════════════════════════════════
# SCENARIO 5 — Claude Sonnet Fails, Opus Succeeds (Fallback)
# ════════════════════════════════════════════════════════════════

class TestScenario5_ClaudeFallback:
    """
    Claude Haiku fails but Sonnet succeeds as fallback.
    Expected: Telegram gets report from Sonnet. Pipeline completes.
    """

    SONNET_VERDICT = {
        "match_id": "test_001",
        "verdict": "Back Arsenal — Sonnet Confirmed",
        "reason": "Sonnet fallback analysis confirms value on Arsenal.",
        "confidence": 78
    }

    @patch("pipeline.is_match_processed", return_value=False)
    @patch("pipeline.collect_match_insights",
           return_value=GOOD_INTELLIGENCE)
    @patch("pipeline.validate_match_data",
           return_value=(MagicMock(
               match_id="test_001",
               model_dump=lambda: GOOD_INTELLIGENCE
           ), None))
    @patch("pipeline.run_v3_audit", return_value=SONNET_VERDICT)
    @patch("pipeline.send_intelligence_report")
    @patch("pipeline.save_verdict")
    def test_sonnet_fallback_succeeds(
        self,
        mock_save,
        mock_telegram,
        mock_claude,
        mock_validate,
        mock_gemini,
        mock_db
    ):
        process_match(SAMPLE_MATCH)

        # Report was still sent
        mock_telegram.assert_called_once()
        call_args = mock_telegram.call_args[1]
        assert "Sonnet" in call_args["verdict"]
        assert call_args["confidence"] == 78

        print("✅ Scenario 5 passed: Sonnet fallback worked correctly")
# ════════════════════════════════════════════════════════════════
# SCENARIO 6 — Both Claude Sonnet and Haiku Fail
# ════════════════════════════════════════════════════════════════

class TestScenario6_ClaudeTotalFailure:
    """
    Both Sonnet and Haiku fail completely.
    Expected: Failure alert sent. Database not updated.
    """

    @patch("pipeline.is_match_processed", return_value=False)
    @patch("pipeline.collect_match_insights",
           return_value=GOOD_INTELLIGENCE)
    @patch("pipeline.validate_match_data",
           return_value=(MagicMock(
               match_id="test_001",
               model_dump=lambda: GOOD_INTELLIGENCE
           ), None))
    @patch("pipeline.run_v3_audit", return_value=None)
    @patch("pipeline.send_pipeline_failure")
    @patch("pipeline.save_verdict")
    def test_claude_total_failure_handled(
        self,
        mock_save,
        mock_failure_alert,
        mock_claude,
        mock_validate,
        mock_gemini,
        mock_db
    ):
        process_match(SAMPLE_MATCH)

        # Failure alert must be sent
        mock_failure_alert.assert_called_once()
        call_args = mock_failure_alert.call_args[0]
        assert "CLAUDE" in call_args[0]

        # Database must NOT be updated
        mock_save.assert_not_called()

        print("✅ Scenario 6 passed: Claude total failure handled correctly")

# ════════════════════════════════════════════════════════════════
# SCENARIO 7 — No Matches in 15-Minute Window (Idle State)
# ════════════════════════════════════════════════════════════════

class TestScenario7_NoMatchesFound:
    """
    Scheduler finds no matches starting soon.
    Expected: Pipeline stays idle. No API calls made.
    """

    @patch("main.get_matches_starting_soon", return_value=[])
    @patch("main.process_match")
    def test_idle_when_no_matches(
        self,
        mock_process,
        mock_scheduler
    ):
        run_schedule_check()

        # process_match must never be called
        mock_process.assert_not_called()

        print("✅ Scenario 7 passed: Idle state works correctly")


# ════════════════════════════════════════════════════════════════
# SCENARIO 8 — Multiple Matches Found at Once
# ════════════════════════════════════════════════════════════════

class TestScenario8_MultipleMatches:
    """
    Scheduler finds 3 matches starting soon.
    Expected: All 3 are processed independently.
    """

    THREE_MATCHES = [
        {**SAMPLE_MATCH, "id": "m1",
         "home_team": "Arsenal", "away_team": "Man City"},
        {**SAMPLE_MATCH, "id": "m2",
         "home_team": "Liverpool", "away_team": "Chelsea"},
        {**SAMPLE_MATCH, "id": "m3",
         "home_team": "Spurs", "away_team": "Newcastle"},
    ]

    @patch("main.get_matches_starting_soon",
           return_value=THREE_MATCHES)
    @patch("main.process_match")
    def test_all_matches_processed(
        self,
        mock_process,
        mock_scheduler
    ):
        run_schedule_check()

        # process_match called exactly 3 times
        assert mock_process.call_count == 3

        # Each match was passed correctly
        processed_ids = [
            call[0][0]["id"]
            for call in mock_process.call_args_list
        ]
        assert "m1" in processed_ids
        assert "m2" in processed_ids
        assert "m3" in processed_ids

        print("✅ Scenario 8 passed: All 3 matches processed")


# ════════════════════════════════════════════════════════════════
# SCENARIO 9 — One Match Crashes Mid-Pipeline (Resilience)
# ════════════════════════════════════════════════════════════════

class TestScenario9_OneMatchCrashes:
    """
    First match throws an unexpected exception.
    Expected: Second match still processes. Pipeline doesn't die.
    """

    TWO_MATCHES = [
        {**SAMPLE_MATCH, "id": "crash_match",
         "home_team": "Bad Team", "away_team": "Error FC"},
        {**SAMPLE_MATCH, "id": "good_match",
         "home_team": "Arsenal", "away_team": "Chelsea"},
    ]

    def process_side_effect(match):
        if match["id"] == "crash_match":
            raise Exception("Simulated unexpected crash!")

    @patch("main.get_matches_starting_soon",
           return_value=TWO_MATCHES)
    @patch("main.process_match",
           side_effect=process_side_effect)
    @patch("main.send_alert")
    def test_pipeline_survives_one_crash(
        self,
        mock_alert,
        mock_process,
        mock_scheduler
    ):
        # Should NOT raise — crash is caught internally
        run_schedule_check()

        # process_match was attempted for both matches
        assert mock_process.call_count == 2

        # Telegram was alerted about the crash
        mock_alert.assert_called()
        alert_message = mock_alert.call_args[0][0]
        assert "Error" in alert_message

        print("✅ Scenario 9 passed: Pipeline survived one match crash")


# ════════════════════════════════════════════════════════════════
# SCENARIO 10 — Gemini Returns Invalid JSON Type
# ════════════════════════════════════════════════════════════════

class TestScenario10_GeminiReturnsWrongType:
    """
    Gemini returns a string instead of a dict (JSON parse failed).
    Expected: Pipeline catches it before Pydantic even runs.
    """

    @patch("pipeline.is_match_processed", return_value=False)
    @patch("pipeline.collect_match_insights",
           return_value="This is not a dict")  # ← string, not dict
    @patch("pipeline.validate_match_data")
    @patch("pipeline.send_pipeline_failure")
    def test_wrong_type_caught_early(
        self,
        mock_failure_alert,
        mock_validate,
        mock_gemini,
        mock_db
    ):
        process_match(SAMPLE_MATCH)

        # Pydantic must NOT run
        mock_validate.assert_not_called()

        # Alert must be sent
        mock_failure_alert.assert_called_once()

        print("✅ Scenario 10 passed: Wrong type caught before validation")