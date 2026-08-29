from __future__ import annotations

import pytest

from crooked_numbers_ingest.settings import Settings


def test_settings_from_env_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STORAGE_MODE", raising=False)
    monkeypatch.delenv("LOCAL_DATA_ROOT", raising=False)
    monkeypatch.delenv("BLOB_ACCOUNT_URL", raising=False)
    monkeypatch.delenv("AZURITE_CONNECTION_STRING", raising=False)
    monkeypatch.delenv("STATCAST_CONTAINER", raising=False)
    monkeypatch.delenv("STATCAST_LOOKBACK_DAYS", raising=False)
    monkeypatch.delenv("INGESTION_MODE", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)

    settings = Settings.from_env()

    assert settings.storage_mode == "local"
    assert settings.local_data_root.as_posix() == "data"
    assert settings.blob_account_url is None
    assert settings.azurite_connection_string == "UseDevelopmentStorage=true"
    assert settings.statcast_container == "baseball-data"
    assert settings.statcast_lookback_days == 3
    assert settings.ingestion_mode == "local"
    assert settings.azure_client_id is None


def test_settings_from_env_reads_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STORAGE_MODE", "azure")
    monkeypatch.setenv("LOCAL_DATA_ROOT", "/tmp/statcast")
    monkeypatch.setenv("BLOB_ACCOUNT_URL", "https://example.blob.core.windows.net")
    monkeypatch.setenv("STATCAST_CONTAINER", "statcast")
    monkeypatch.setenv("AZURITE_CONNECTION_STRING", "UseDevelopmentStorage=true")
    monkeypatch.setenv("STATCAST_LOOKBACK_DAYS", "5")
    monkeypatch.setenv("INGESTION_MODE", "container-apps-job")
    monkeypatch.setenv("AZURE_CLIENT_ID", "client-id")

    settings = Settings.from_env()

    assert settings.storage_mode == "azure"
    assert settings.local_data_root.as_posix() == "/tmp/statcast"
    assert settings.blob_account_url == "https://example.blob.core.windows.net"
    assert settings.azurite_connection_string == "UseDevelopmentStorage=true"
    assert settings.statcast_container == "statcast"
    assert settings.statcast_lookback_days == 5
    assert settings.ingestion_mode == "container-apps-job"
    assert settings.azure_client_id == "client-id"


def test_settings_from_env_requires_blob_account_url_in_azure_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("STORAGE_MODE", "azure")
    monkeypatch.delenv("BLOB_ACCOUNT_URL", raising=False)

    with pytest.raises(ValueError, match="BLOB_ACCOUNT_URL"):
        Settings.from_env()


def test_settings_from_env_rejects_invalid_storage_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("STORAGE_MODE", "production")

    with pytest.raises(ValueError, match="STORAGE_MODE"):
        Settings.from_env()


def test_settings_from_env_rejects_invalid_lookback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("STATCAST_LOOKBACK_DAYS", "zero")

    with pytest.raises(ValueError, match="STATCAST_LOOKBACK_DAYS"):
        Settings.from_env()
