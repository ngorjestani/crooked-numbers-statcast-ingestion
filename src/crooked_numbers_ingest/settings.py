"""Application settings for Statcast ingestion."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    blob_account_url: str
    statcast_container: str
    statcast_lookback_days: int = 3
    ingestion_mode: str = "local"
    azure_client_id: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        blob_account_url = _get_required_env("BLOB_ACCOUNT_URL")
        statcast_container = _get_required_env("STATCAST_CONTAINER")
        statcast_lookback_days = _get_int_env("STATCAST_LOOKBACK_DAYS", default=3)
        ingestion_mode = os.getenv("INGESTION_MODE", "local")
        azure_client_id = os.getenv("AZURE_CLIENT_ID") or None

        return cls(
            blob_account_url=blob_account_url,
            statcast_container=statcast_container,
            statcast_lookback_days=statcast_lookback_days,
            ingestion_mode=ingestion_mode,
            azure_client_id=azure_client_id,
        )


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        msg = f"Missing required environment variable: {name}"
        raise ValueError(msg)
    return value.strip()


def _get_int_env(name: str, *, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default

    try:
        parsed = int(value)
    except ValueError as exc:
        msg = f"Environment variable {name} must be an integer"
        raise ValueError(msg) from exc

    if parsed < 1:
        msg = f"Environment variable {name} must be greater than 0"
        raise ValueError(msg)

    return parsed
