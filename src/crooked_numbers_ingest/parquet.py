"""Parquet serialization for raw Statcast ingestion."""

from __future__ import annotations

from datetime import UTC, date, datetime
from io import BytesIO

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def statcast_dataframe_to_parquet_bytes(
    dataframe: pd.DataFrame,
    target_date: date,
    *,
    ingestion_mode: str,
    source_name: str = "statcast",
    fetched_at_utc: datetime | None = None,
) -> bytes:
    """Enrich a Statcast dataframe and serialize it to parquet bytes."""

    enriched = dataframe.copy()
    fetched_at = _normalize_fetched_at(fetched_at_utc)

    enriched["source_name"] = source_name
    enriched["source_query_start_date"] = target_date.isoformat()
    enriched["source_query_end_date"] = target_date.isoformat()
    enriched["fetched_at_utc"] = fetched_at.isoformat()
    enriched["ingestion_mode"] = ingestion_mode

    if {"game_pk", "at_bat_number", "pitch_number"}.issubset(enriched.columns):
        enriched["pitch_uid"] = (
            enriched[["game_pk", "at_bat_number", "pitch_number"]]
            .astype("string")
            .agg("_".join, axis=1)
        )

    buffer = BytesIO()
    table = pa.Table.from_pandas(enriched, preserve_index=False)
    pq.write_table(table, buffer, compression="snappy")
    return buffer.getvalue()


def _normalize_fetched_at(fetched_at_utc: datetime | None) -> datetime:
    if fetched_at_utc is None:
        return datetime.now(UTC)
    if fetched_at_utc.tzinfo is None:
        return fetched_at_utc.replace(tzinfo=UTC)
    return fetched_at_utc.astimezone(UTC)
