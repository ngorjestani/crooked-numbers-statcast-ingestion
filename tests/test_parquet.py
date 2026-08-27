from __future__ import annotations

from io import BytesIO
from datetime import UTC, date, datetime

import pandas as pd
import pyarrow.parquet as pq

from crooked_numbers_ingest.parquet import statcast_dataframe_to_parquet_bytes


def test_statcast_dataframe_to_parquet_bytes_adds_metadata_and_pitch_uid() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "game_pk": 123,
                "at_bat_number": 4,
                "pitch_number": 2,
                "events": "single",
            }
        ]
    )

    payload = statcast_dataframe_to_parquet_bytes(
        dataframe,
        date(2026, 8, 26),
        ingestion_mode="local",
        fetched_at_utc=datetime(2026, 8, 27, 12, 30, tzinfo=UTC),
    )

    result = pq.read_table(BytesIO(payload)).to_pandas()

    assert result.loc[0, "game_pk"] == 123
    assert result.loc[0, "events"] == "single"
    assert result.loc[0, "source_name"] == "statcast"
    assert result.loc[0, "source_query_start_date"] == "2026-08-26"
    assert result.loc[0, "source_query_end_date"] == "2026-08-26"
    assert result.loc[0, "fetched_at_utc"] == "2026-08-27T12:30:00+00:00"
    assert result.loc[0, "ingestion_mode"] == "local"
    assert result.loc[0, "pitch_uid"] == "123_4_2"


def test_statcast_dataframe_to_parquet_bytes_preserves_raw_columns_without_pitch_uid() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "game_date": "2026-08-26",
                "events": "walk",
                "description": "ball",
            }
        ]
    )

    payload = statcast_dataframe_to_parquet_bytes(
        dataframe,
        date(2026, 8, 26),
        ingestion_mode="container-apps-job",
        source_name="statcast",
        fetched_at_utc=datetime(2026, 8, 27, 0, 0, tzinfo=UTC),
    )

    result = pq.read_table(BytesIO(payload)).to_pandas()

    assert result.loc[0, "game_date"] == "2026-08-26"
    assert result.loc[0, "events"] == "walk"
    assert result.loc[0, "description"] == "ball"
    assert result.loc[0, "ingestion_mode"] == "container-apps-job"
    assert "pitch_uid" not in result.columns
