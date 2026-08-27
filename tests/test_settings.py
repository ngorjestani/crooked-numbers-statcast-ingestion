from __future__ import annotations

import pytest

from crooked_numbers_ingest.settings import Settings


def test_settings_from_env_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLOB_ACCOUNT_URL", "https://crookednumbers.blob.core.windows.net")
    monkeypatch.setenv("STATCAST_CONTAINER", "baseball-data")
    monkeypatch.delenv("STATCAST_LOOKBACK_DAYS", raising=False)
    monkeypatch.delenv("INGESTION_MODE", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)

    settings = Settings.from_env()

    assert settings.blob_account_url == "https://crookednumbers.blob.core.windows.net"
    assert settings.statcast_container == "baseball-data"
    assert settings.statcast_lookback_days == 3
    assert settings.ingestion_mode == "local"
    assert settings.azure_client_id is None


def test_settings_from_env_reads_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLOB_ACCOUNT_URL", "https://example.blob.core.windows.net")
    monkeypatch.setenv("STATCAST_CONTAINER", "statcast")
    monkeypatch.setenv("STATCAST_LOOKBACK_DAYS", "5")
    monkeypatch.setenv("INGESTION_MODE", "container-apps-job")
    monkeypatch.setenv("AZURE_CLIENT_ID", "client-id")

    settings = Settings.from_env()

    assert settings.blob_account_url == "https://example.blob.core.windows.net"
    assert settings.statcast_container == "statcast"
    assert settings.statcast_lookback_days == 5
    assert settings.ingestion_mode == "container-apps-job"
    assert settings.azure_client_id == "client-id"


def test_settings_from_env_requires_blob_account_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("BLOB_ACCOUNT_URL", raising=False)
    monkeypatch.setenv("STATCAST_CONTAINER", "baseball-data")

    with pytest.raises(ValueError, match="BLOB_ACCOUNT_URL"):
        Settings.from_env()


def test_settings_from_env_requires_container(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLOB_ACCOUNT_URL", "https://example.blob.core.windows.net")
    monkeypatch.delenv("STATCAST_CONTAINER", raising=False)

    with pytest.raises(ValueError, match="STATCAST_CONTAINER"):
        Settings.from_env()


def test_settings_from_env_rejects_invalid_lookback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BLOB_ACCOUNT_URL", "https://example.blob.core.windows.net")
    monkeypatch.setenv("STATCAST_CONTAINER", "baseball-data")
    monkeypatch.setenv("STATCAST_LOOKBACK_DAYS", "zero")

    with pytest.raises(ValueError, match="STATCAST_LOOKBACK_DAYS"):
        Settings.from_env()
