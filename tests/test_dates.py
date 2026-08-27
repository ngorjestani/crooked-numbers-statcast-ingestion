from __future__ import annotations

from datetime import date

import pytest

from crooked_numbers_ingest.dates import target_dates


def test_target_dates_returns_yesterday_through_lookback_boundary() -> None:
    result = target_dates(3, today=date(2026, 8, 27))

    assert result == [
        date(2026, 8, 26),
        date(2026, 8, 25),
        date(2026, 8, 24),
    ]


def test_target_dates_rejects_non_positive_lookback() -> None:
    with pytest.raises(ValueError, match="lookback_days"):
        target_dates(0, today=date(2026, 8, 27))
