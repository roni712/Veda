from datetime import datetime, timedelta, timezone

def is_stale(latest_timestamp, threshold_hours=24):
    now = datetime.now(timezone.utc)

    # Safety: if DB ever returns naive (edge case)
    if latest_timestamp.tzinfo is None:
        latest_timestamp = latest_timestamp.replace(tzinfo=timezone.utc)

    return now - latest_timestamp > timedelta(hours=threshold_hours)
