from datetime import datetime, timezone, timedelta
from modules.odds_collector import get_upcoming_matches

now_utc = datetime.now(timezone.utc)
now_myt = datetime.now()

print(f"\n===== TIME CHECK =====")
print(f"Your machine time (local): {now_myt.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"UTC time right now:        {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Difference (should be +8 for Malaysia): "
      f"{int((now_myt - now_utc.replace(tzinfo=None)).total_seconds()/3600)}h")

print(f"\n===== UPCOMING MATCHES =====")
matches = get_upcoming_matches()

print(f"Total matches found: {len(matches)}\n")

for match in matches:
    raw_time = match.get("commence_time", "")
    start_utc = datetime.fromisoformat(
        raw_time.replace("Z", "+00:00")
    )
    start_myt = start_utc + timedelta(hours=8)
    diff_minutes = (start_utc - now_utc).total_seconds() / 60

    print(f"Match:     {match.get('home_team')} vs {match.get('away_team')}")
    print(f"Sport:     {match.get('sport_key')}")
    print(f"UTC time:  {start_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"MYT time:  {start_myt.strftime('%Y-%m-%d %H:%M:%S')} MYT")
    print(f"Starts in: {diff_minutes:.0f} minutes from now")
    print(f"In window: {'✅ YES' if 0 <= diff_minutes <= 120 else '❌ NO'}")
    print("-" * 45)