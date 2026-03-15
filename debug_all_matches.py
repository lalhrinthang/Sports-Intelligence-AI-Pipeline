# save as debug_all_matches.py
from datetime import datetime, timezone, timedelta
from modules.odds_collector import get_upcoming_matches

now_utc = datetime.now(timezone.utc)

print(f"Current UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}\n")
print(f"{'Match':<40} {'UTC Time':<22} {'Mins Away':>10} {'Status'}")
print("-" * 90)

matches = get_upcoming_matches()

for m in sorted(matches,
                key=lambda x: x.get("commence_time", "")):
    raw = m.get("commence_time", "")
    start = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    diff  = (start - now_utc).total_seconds() / 60
    name  = f"{m.get('home_team')} vs {m.get('away_team')}"

    if diff < -90:
        status = "🔴 Finished/Late"
    elif diff < 0:
        status = "🟡 In progress"
    elif diff <= 120:
        status = "🟢 IN WINDOW"
    else:
        status = "⏳ Too early"

    print(f"{name:<40} {start.strftime('%Y-%m-%d %H:%M'):<22}"
          f"{diff:>10.0f}    {status}")