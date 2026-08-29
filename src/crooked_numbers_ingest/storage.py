"""Storage abstractions for raw Statcast uploads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

from crooked_numbers_ingest.settings import Settings


class ParquetSink(Protocol):
    """Interface for writing parquet bytes to the configured destination."""

    def write_parquet(self, relative_path: str, payload: bytes, *, metadata: dict[str, str]) -> None:
        """Write parquet content to the target relative path."""


@dataclass(slots=True)
class LocalParquetSink:
    """Write parquet bytes to the local filesystem."""

    local_data_root: Path

    def write_parquet(self, relative_path: str, payload: bytes, *, metadata: dict[str, str]) -> None:
        output_path = self.local_data_root / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(payload)


@dataclass(slots=True)
class BlobParquetSink:
    """Upload parquet bytes to a blob service client."""

    container_name: str
    blob_service_client: object

    def write_parquet(self, relative_path: str, payload: bytes, *, metadata: dict[str, str]) -> None:
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=relative_path,
        )
        blob_client.upload_blob(
            payload,
            overwrite=True,
            content_settings=self._content_settings(),
            metadata=metadata,
        )

    @staticmethod
    def _content_settings():
        from azure.storage.blob import ContentSettings

        return ContentSettings(content_type="application/octet-stream")


def build_blob_path(game_date: date) -> str:
    """Build the raw Statcast blob path for a game date."""

    return (
        f"raw/statcast/season={game_date.year}/"
        f"game_date={game_date.isoformat()}/statcast.parquet"
    )


def build_blob_metadata(
    *,
    game_date: date,
    row_count: int,
    fetched_at_utc: str,
) -> dict[str, str]:
    """Build Azure Blob metadata for a Statcast parquet upload."""

    return {
        "source": "baseball_savant_statcast",
        "game_date": game_date.isoformat(),
        "row_count": str(row_count),
        "fetched_at_utc": fetched_at_utc,
    }


def build_local_output_path(local_data_root: Path | str, game_date: date) -> Path:
    """Build the local filesystem output path for a Statcast parquet file."""

    return Path(local_data_root) / build_blob_path(game_date)


def create_parquet_sink(settings: Settings) -> ParquetSink:
    """Create the configured parquet sink for local, azurite, or azure output."""

    if settings.storage_mode == "local":
        return LocalParquetSink(local_data_root=settings.local_data_root)
    return BlobParquetSink(
        container_name=settings.statcast_container,
        blob_service_client=create_blob_service_client(settings),
    )


def create_blob_service_client(settings: Settings):
    """Create a blob service client for Azurite or Azure."""

    from azure.storage.blob import BlobServiceClient

    if settings.storage_mode == "azurite":
        return BlobServiceClient.from_connection_string(settings.azurite_connection_string)

    return BlobServiceClient(
        account_url=settings.blob_account_url or "",
        credential=_default_azure_credential(settings.azure_client_id),
    )


def _default_azure_credential(azure_client_id: str | None):
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential(managed_identity_client_id=azure_client_id)
