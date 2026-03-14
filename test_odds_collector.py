from modules.odds_collector import get_upcoming_matches, get_match_odds
from scheduler import get_matches_starting_soon

print("\n--- TEST 1: Get all upcoming matches ---")
matches = get_upcoming_matches()
print(f"Total matches found: {len(matches)}")

if matches:
    # Print the first match as a sample
    first = matches[0]
    print(f"\nSample match:")
    print(f"  ID: {first.get('id')}")
    print(f"  Sport: {first.get('sport_key')}")
    print(f"  Home: {first.get('home_team')}")
    print(f"  Away: {first.get('away_team')}")
    print(f"  Starts: {first.get('commence_time').replace('T', ' Time --> ').replace('Z', ' UTC')}")

# print("\n--- TEST 2: Check 15-minute window ---")
# soon = get_matches_starting_soon(window_minutes=15)
# print(f"Matches starting in 15 min: {len(soon)}")

# # Widen window to test the function works
# print("\n--- TEST 3: Widen window to 72 hours ---")
# soon_wide = get_matches_starting_soon(window_minutes=72*60)
# print(f"Matches in next 72 hours: {len(soon_wide)}")