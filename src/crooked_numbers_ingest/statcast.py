"""Statcast data acquisition."""

from __future__ import annotations

from datetime import date

from pybaseball import statcast


def fetch_statcast_for_date(game_date: date):
    """Fetch Statcast data for a single game date."""

    date_text = game_date.isoformat()
    return statcast(start_dt=date_text, end_dt=date_text)
