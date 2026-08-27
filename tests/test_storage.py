from __future__ import annotations

from datetime import date

from crooked_numbers_ingest.storage import build_blob_metadata, build_blob_path


def test_build_blob_path_uses_expected_statcast_partition_layout() -> None:
    assert (
        build_blob_path(date(2026, 8, 26))
        == "raw/statcast/season=2026/game_date=2026-08-26/statcast.parquet"
    )


def test_build_blob_metadata_uses_expected_values() -> None:
    metadata = build_blob_metadata(
        game_date=date(2026, 8, 26),
        row_count=321,
        fetched_at_utc="2026-08-27T00:15:00+00:00",
    )

    assert metadata == {
        "source": "baseball_savant_statcast",
        "game_date": "2026-08-26",
        "row_count": "321",
        "fetched_at_utc": "2026-08-27T00:15:00+00:00",
    }
