from modules.odds_collector import get_upcoming_matches

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
    print(f"  Starts: {first.get('commence_time')}")