"""Storage abstractions for raw Statcast uploads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ParquetUploader(Protocol):
    """Interface for writing parquet bytes to object storage."""

    def upload_parquet(self, blob_path: str, payload: bytes) -> None:
        """Upload parquet content to the target blob path."""


@dataclass(slots=True)
class StubParquetUploader:
    """Placeholder uploader until Azure Blob support is implemented."""

    def upload_parquet(self, blob_path: str, payload: bytes) -> None:
        msg = (
            "Azure Blob upload is not implemented yet. "
            f"Attempted upload to {blob_path} with {len(payload)} bytes."
        )
        raise NotImplementedError(msg)
