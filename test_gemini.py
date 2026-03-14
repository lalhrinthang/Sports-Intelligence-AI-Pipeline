from modules.gemini_collector import collect_match_insights
# This is a simple test script to verify that the Gemini Collector can successfully process a match and return insights.

# We simulate a match object (like what The Odds API gives us)
# In the real pipeline, this comes from Phase 5
sample_match = {
    "id": "test_match_001",
    "sport_key": "soccer_epl",
    "home_team": "Arsenal",
    "away_team": "Manchester City",
    "commence_time": "2026-03-14T15:00:00Z"
}

print("Sending match to Gemini for research...")
print("(This may take 10-20 seconds while Gemini searches the web)\n")

result = collect_match_insights(sample_match)

if result:
    print("SUCCESS! Gemini returned:\n")
    for key, value in result.items():
        print(f"  {key}:")
        print(f"    {value[:200]}...")  # Show first 100 chars
        print()
else:
    print("FAILED — check logfile.txt for details")