from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)


def utc_now_iso():
    """ISO-8601 UTC timestamp with a trailing 'Z' (e.g. 2026-01-01T12:00:00.000000Z)."""
    return utc_now().replace(tzinfo=None).isoformat() + 'Z'
