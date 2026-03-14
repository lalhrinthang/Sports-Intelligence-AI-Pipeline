from modules.gemini_collector import collect_match_insights
# This is a simple test script to verify that the Gemini Collector can successfully process a match and return insights.
sample_match = {
    "id": "07e3e6c1966c98bce260a6608d692f73",
    "sport_key": "soccer_epl",
    "home_team": "Burnley",
    "away_team": "Bournemouth",
    "commence_time": "2026-03-14T15:00:00Z"
}

print("Sending match to Gemini Pro for research...")
print("(This may take 10-20 seconds while Gemini searches the web)\n")

result = collect_match_insights(sample_match)

if result:
    print("SUCCESS! Gemini returned:\n")
    for key, value in result.items():
        print(f"  {key}:")
        print(f"    {value[:100]}...")  # Show first 100 chars
        print()
else:
    print("FAILED — check logfile.txt for details")