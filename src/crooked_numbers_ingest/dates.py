"""Date helpers for Statcast ingestion windows."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta


def utc_today() -> date:
    """Return today's date in UTC."""

    return datetime.now(UTC).date()


def target_dates(lookback_days: int, *, today: date | None = None) -> list[date]:
    """Return dates from yesterday back to the lookback boundary in UTC."""

    if lookback_days < 1:
        msg = "lookback_days must be greater than 0"
        raise ValueError(msg)

    anchor_date = today or utc_today()
    return [anchor_date - timedelta(days=offset) for offset in range(1, lookback_days + 1)]
