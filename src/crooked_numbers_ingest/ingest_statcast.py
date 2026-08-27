"""Statcast ingestion entry point."""

from __future__ import annotations

import logging
from datetime import date

from crooked_numbers_ingest.dates import target_dates
from crooked_numbers_ingest.settings import Settings
from crooked_numbers_ingest.statcast import fetch_statcast_for_date

LOGGER = logging.getLogger(__name__)


def blob_path_for_date(game_date: date) -> str:
    """Build the raw Statcast blob path for a game date."""

    return (
        f"raw/statcast/season={game_date.year}/"
        f"game_date={game_date.isoformat()}/statcast.parquet"
    )


def run() -> None:
    """Run the Statcast ingestion workflow."""

    settings = Settings.from_env()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    LOGGER.info(
        "Starting Statcast ingestion in %s mode for container %s",
        settings.ingestion_mode,
        settings.statcast_container,
    )

    for game_date in target_dates(settings.statcast_lookback_days):
        blob_path = blob_path_for_date(game_date)
        LOGGER.info("Fetching Statcast data for %s", game_date.isoformat())

        statcast_frame = fetch_statcast_for_date(game_date)
        row_count = len(statcast_frame.index)

        LOGGER.info(
            "Fetched %s rows for %s; target blob path is %s",
            row_count,
            game_date.isoformat(),
            blob_path,
        )
        LOGGER.info("TODO: serialize dataframe to parquet and upload bytes to storage")


if __name__ == "__main__":
    run()
