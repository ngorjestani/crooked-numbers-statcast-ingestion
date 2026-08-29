"""Application settings for Statcast ingestion."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ALLOWED_STORAGE_MODES = {"local", "azurite", "azure"}


@dataclass(slots=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    storage_mode: str = "local"
    local_data_root: Path = Path("./data")
    statcast_container: str = "baseball-data"
    blob_account_url: str | None = None
    azurite_connection_string: str = "UseDevelopmentStorage=true"
    statcast_lookback_days: int = 3
    ingestion_mode: str = "local"
    azure_client_id: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        storage_mode = os.getenv("STORAGE_MODE", "local").strip().lower() or "local"
        _validate_storage_mode(storage_mode)

        local_data_root = Path(os.getenv("LOCAL_DATA_ROOT", "./data"))
        statcast_container = os.getenv("STATCAST_CONTAINER", "baseball-data").strip() or "baseball-data"
        blob_account_url = os.getenv("BLOB_ACCOUNT_URL")
        azurite_connection_string = (
            os.getenv("AZURITE_CONNECTION_STRING", "UseDevelopmentStorage=true").strip()
            or "UseDevelopmentStorage=true"
        )
        statcast_lookback_days = _get_int_env("STATCAST_LOOKBACK_DAYS", default=3)
        ingestion_mode = os.getenv("INGESTION_MODE", "local")
        azure_client_id = os.getenv("AZURE_CLIENT_ID") or None

        if storage_mode == "azure":
            blob_account_url = _get_required_env("BLOB_ACCOUNT_URL")
        elif blob_account_url is not None:
            blob_account_url = blob_account_url.strip() or None

        return cls(
            storage_mode=storage_mode,
            local_data_root=local_data_root,
            statcast_container=statcast_container,
            blob_account_url=blob_account_url,
            azurite_connection_string=azurite_connection_string,
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


def _validate_storage_mode(storage_mode: str) -> None:
    if storage_mode not in ALLOWED_STORAGE_MODES:
        allowed_modes = ", ".join(sorted(ALLOWED_STORAGE_MODES))
        msg = f"STORAGE_MODE must be one of: {allowed_modes}"
        raise ValueError(msg)


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
