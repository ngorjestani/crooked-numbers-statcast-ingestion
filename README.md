# crooked-numbers-statcast-ingestion

Ingestion repository for the Crooked Numbers baseball analytics platform.

This repo is responsible for pulling source baseball data, validating it at the ingestion boundary, and writing raw datasets to Azure Blob Storage. It is intentionally scoped to ingestion only and does not include the future .NET or React dashboard application.

## Purpose

The initial focus is Statcast ingestion for downstream baseball analytics workflows. Raw data produced by this project should remain as close to the source as practical so later transform, modeling, and presentation layers can evolve independently.

Key boundaries:

- This repo owns ingestion into raw storage.
- This repo does not own dashboard shaping or presentation-specific transforms.
- Credentials and secrets must never be committed.

## Local Development Overview

Local Python development is expected to happen in PyCharm.

Planned local workflow:

1. Create a local virtual environment.
2. Copy `.env.example` to `.env` for local configuration.
3. Leave `STORAGE_MODE=local` to write output to the local filesystem by default.
4. Switch to `azurite` or `azure` only when you explicitly want blob storage writes.

This repository does not yet define Python application code, infrastructure templates, container build assets, or CI workflows. Those should be added incrementally as implementation begins.

Python package code and a basic Docker image definition are now included. Infrastructure templates and CI workflows are still intentionally deferred.

## Storage Modes

The ingestion job supports three storage targets:

- `local`: writes parquet files under `LOCAL_DATA_ROOT`, default `./data`
- `azurite`: writes to an Azurite blob container using `AZURITE_CONNECTION_STRING`
- `azure`: writes to Azure Blob Storage using `DefaultAzureCredential` and `BLOB_ACCOUNT_URL`

All modes use the same relative path layout:

`raw/statcast/season=YYYY/game_date=YYYY-MM-DD/statcast.parquet`

### Local Mode

Default local development writes to the filesystem and does not touch Azure:

```bash
STORAGE_MODE=local
LOCAL_DATA_ROOT=./data
PYTHONPATH=src python -m crooked_numbers_ingest.ingest_statcast
```

### Azurite Mode

Use Azurite when you want blob-compatible local testing:

```bash
STORAGE_MODE=azurite
STATCAST_CONTAINER=baseball-data
AZURITE_CONNECTION_STRING=UseDevelopmentStorage=true
PYTHONPATH=src python -m crooked_numbers_ingest.ingest_statcast
```

Azurite and Azure share the same blob upload behavior after client creation. The only difference is how the `BlobServiceClient` is constructed.

### Azure Mode

Use real Azure only when explicitly intended:

```bash
STORAGE_MODE=azure
BLOB_ACCOUNT_URL=https://crookednumbers.blob.core.windows.net
STATCAST_CONTAINER=baseball-data
PYTHONPATH=src python -m crooked_numbers_ingest.ingest_statcast
```

Azure mode uses `DefaultAzureCredential`. If you need a user-assigned managed identity, set `AZURE_CLIENT_ID`.

## Docker

Build the image from the repo root:

```bash
docker build -t crooked-numbers-statcast-ingestion .
```

Run the ingestion job with a local `.env` file:

```bash
docker run --rm --env-file .env crooked-numbers-statcast-ingestion
```

For local non-container execution, use:

```bash
./scripts/run-local.sh
```

## Azure Target Architecture

The intended cloud target is Azure Container Apps Job.

Current target resource layout:

- Azure resource group: `crooked-numbers`
- Azure storage account: `crookednumbers`
- Blob container: `baseball-data`
- Planned compute target: Azure Container Apps Job

Expected runtime pattern:

1. A scheduled or manually triggered container job runs the ingestion task.
2. The job authenticates with Azure using managed identity.
3. The job pulls source baseball data.
4. The job writes raw output files to the `baseball-data` container using partitioned paths.

Managed identity should be the default production authentication model. Avoid account keys and connection strings for Azure mode. The Azurite development connection string is acceptable only for Azurite mode.

## Expected Blob Layout

Raw Statcast data should be written using this partitioned path convention:

`raw/statcast/season=YYYY/game_date=YYYY-MM-DD/statcast.parquet`

Example:

`raw/statcast/season=2025/game_date=2025-04-15/statcast.parquet`

This layout keeps raw ingestion organized by season and game date while remaining easy to consume from downstream processing systems.

## Security

Do not commit:

- Azure credentials
- account keys
- connection strings
- populated `.env` files
- any other secrets or tokens

Use environment variables locally and managed identity where available.
