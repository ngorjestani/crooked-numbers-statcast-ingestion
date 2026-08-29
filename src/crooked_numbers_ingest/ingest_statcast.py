"""Statcast ingestion entry point."""

from __future__ import annotations

import logging

from crooked_numbers_ingest.dates import target_dates
from crooked_numbers_ingest.parquet import (
    fetched_at_isoformat,
    statcast_dataframe_to_parquet_bytes,
    utc_now,
)
from crooked_numbers_ingest.settings import Settings
from crooked_numbers_ingest.storage import (
    build_blob_metadata,
    build_blob_path,
    create_parquet_sink,
)
from crooked_numbers_ingest.statcast import fetch_statcast_for_date

LOGGER = logging.getLogger(__name__)


def run() -> None:
    """Run the Statcast ingestion workflow."""

    settings = Settings.from_env()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    LOGGER.info(
        "Starting Statcast ingestion in %s mode with %s storage",
        settings.ingestion_mode,
        settings.storage_mode,
    )
    sink = create_parquet_sink(settings)

    for game_date in target_dates(settings.statcast_lookback_days):
        blob_path = build_blob_path(game_date)
        LOGGER.info("Fetching Statcast data for %s", game_date.isoformat())

        statcast_frame = fetch_statcast_for_date(game_date)
        row_count = len(statcast_frame.index)
        fetched_at = utc_now()
        fetched_at_utc = fetched_at_isoformat(fetched_at)

        LOGGER.info(
            "Fetched %s rows for %s; target blob path is %s",
            row_count,
            game_date.isoformat(),
            blob_path,
        )
        parquet_bytes = statcast_dataframe_to_parquet_bytes(
            statcast_frame,
            game_date,
            ingestion_mode=settings.ingestion_mode,
            fetched_at_utc=fetched_at,
        )
        LOGGER.info(
            "Serialized %s rows for %s into %s parquet bytes",
            row_count,
            game_date.isoformat(),
            len(parquet_bytes),
        )
        sink.write_parquet(
            blob_path,
            parquet_bytes,
            metadata=build_blob_metadata(
                game_date=game_date,
                row_count=row_count,
                fetched_at_utc=fetched_at_utc,
            ),
        )
        LOGGER.info("Wrote parquet for %s to %s", game_date.isoformat(), blob_path)


if __name__ == "__main__":
    run()
