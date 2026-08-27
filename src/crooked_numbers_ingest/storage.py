"""Storage abstractions for raw Statcast uploads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol


class ParquetUploader(Protocol):
    """Interface for writing parquet bytes to object storage."""

    def upload_parquet(self, blob_path: str, payload: bytes, *, metadata: dict[str, str]) -> None:
        """Upload parquet content to the target blob path."""


@dataclass(slots=True)
class AzureBlobParquetUploader:
    """Upload parquet bytes to Azure Blob Storage."""

    blob_account_url: str
    container_name: str
    azure_client_id: str | None = None

    def upload_parquet(self, blob_path: str, payload: bytes, *, metadata: dict[str, str]) -> None:
        blob_client = self._blob_service_client().get_blob_client(
            container=self.container_name,
            blob=blob_path,
        )
        blob_client.upload_blob(
            payload,
            overwrite=True,
            content_settings=self._content_settings(),
            metadata=metadata,
        )

    def _blob_service_client(self):
        from azure.storage.blob import BlobServiceClient

        return BlobServiceClient(account_url=self.blob_account_url, credential=self._credential())

    def _credential(self):
        from azure.identity import DefaultAzureCredential

        return DefaultAzureCredential(managed_identity_client_id=self.azure_client_id)

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
