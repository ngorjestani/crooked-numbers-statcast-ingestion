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
3. Use Azure identity-based authentication for local development.
4. Run ingestion code locally against approved Azure resources.

This repository does not yet define Python application code, infrastructure templates, container build assets, or CI workflows. Those should be added incrementally as implementation begins.

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

Managed identity should be the default production authentication model. Avoid account keys and connection strings.

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
