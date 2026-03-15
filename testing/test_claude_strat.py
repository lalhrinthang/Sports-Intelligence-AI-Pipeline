import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validator import validate_match_data
from modules.claude_strategist import run_v3_audit
from modules.telegram_bot import send_pipeline_failure, send_intelligence_report
from modules.gemini_collector import collect_match_insights

print("=" * 50)
print("TEST 1: Valid data — should PASS validator")
print("=" * 50)

good_data = {
    "match_id": "EPL_001",
    "lineups_injuries": (
        "Arsenal: Raya; White, Saliba, Gabriel, Zinchenko; "
        "Rice, Odegaard, Havertz; Saka, Trossard, Martinelli. "
        "Partey OUT (hamstring). "
        "Man City: Ederson; Walker, Dias, Gvardiol, Akanji; "
        "De Bruyne, Bernardo, Kovacic; Doku, Haaland, Foden. "
        "Rodri OUT (ACL)."
    ),
    "odds_movements": (
        "Arsenal opened 2.40, now 2.10 — steam move detected. "
        "Man City drifted from 3.10 to 3.50. "
        "Draw stable at 3.30. Sharp money on Arsenal."
    ),
    "recent_form": (
        "Arsenal: 3W-1D (12pts). Man City: 2W-1D-1L (7pts). "
        "Arsenal in strong form, City inconsistent."
    ),
    "weather": (
        "London, Emirates Stadium. 11 degrees Celsius. "
        "Light rain, overcast. Wind 18 km/h southwest. "
        "Humidity 82 percent."
    ),
    "public_sentiment": (
        "78 percent of Twitter/X backing Arsenal. "
        "Reddit r/soccer consensus: Arsenal to win. "
        "Top influencer BettingExpert tipped Arsenal -0.5 AH. "
        "Public and sharps aligned."
    )
}

# Step 1: Get Gemini output
intelligence = collect_match_insights(good_data)

# DEBUG — print EXACTLY what Gemini returned
print("\n===== RAW GEMINI OUTPUT =====")
print(intelligence)
print("\n===== FIELD NAMES ONLY =====")
if isinstance(intelligence, dict):
    for key in intelligence.keys():
        print(f"  '{key}'")
else:
    print(f"Not a dict! Got: {type(intelligence)}")
validated, error = validate_match_data(good_data)

if validated:
    print("✅ Validator PASSED\n")
    print("Sending to Claude for V3 Audit...")
    print("(This may take 10-15 seconds)\n")

    verdict = run_v3_audit(validated)

    if verdict:
        print("✅ Claude V3 Audit complete!\n")
        print(f"  Match ID:   {verdict['match_id']}")
        print(f"  Verdict:    {verdict['verdict']}")
        print(f"  Confidence: {verdict['confidence']}%")
        print(f"  Reason:     {verdict['reason'][:120]}...")

        # Send to Telegram
        send_intelligence_report(
            verdict=verdict["verdict"],
            reason=verdict["reason"],
            confidence=verdict["confidence"],
            match_id=verdict["match_id"]
        )
        print("\n✅ Report sent to Telegram!")
    else:
        print("❌ Claude audit failed — check logfile.txt")

else:
    print(f"❌ Validator FAILED: {error}")
    send_pipeline_failure("VALIDATOR", error)


print("\n" + "=" * 50)
print("TEST 2: Bad data — should FAIL validator")
print("=" * 50)

bad_data = {
    "match_id": "EPL_002",
    "lineups_injuries": "Arsenal vs Chelsea",
    # Missing: odds_movement, weather, public_sentiment
}

validated2, error2 = validate_match_data(bad_data)

if validated2:
    print("❌ Should have failed but passed — something is wrong!")
else:
    print(f"✅ Correctly REJECTED bad data")
    print(f"   Error: {error2}")
    print("   Telegram alert would be sent now")
    send_pipeline_failure("VALIDATOR", error)