# crooked-numbers-statcast-ingestion

Statcast ingestion for the Crooked Numbers baseball analytics platform. The project fetches source data, validates it at the ingestion boundary, converts it to Parquet, and writes raw datasets to local storage, Azurite, or Azure Blob Storage.

GitHub Actions is the preferred production ingestion runner. Azure is used only for Blob Storage in the current production architecture. The existing Python entry point remains the source of truth:

```bash
python -m crooked_numbers_ingest.ingest_statcast
```

## Production ingestion

The [Ingest Statcast Data workflow](.github/workflows/ingest-statcast.yml) runs every day at 12:00 UTC and can also be started manually. It:

1. Authenticates to Azure with GitHub Actions OIDC and `azure/login`.
2. Installs the Python dependencies from `requirements.txt`.
3. Runs the existing Python ingestion module with a three-day lookback by default.
4. Writes Parquet files to the `baseball-data` container in the `crookednumbers` storage account.

Scheduled runs set `INGESTION_MODE=github_actions_scheduled`; manual runs set it to `github_actions_manual`.

All storage modes use the same relative blob/file layout:

```text
raw/statcast/season=YYYY/game_date=YYYY-MM-DD/statcast.parquet
```

Example:

```text
raw/statcast/season=2025/game_date=2025-04-15/statcast.parquet
```

## Configure GitHub Actions OIDC

Create or select a Microsoft Entra application or user-assigned managed identity for this repository. In its **Federated credentials** settings, add the **GitHub Actions deploying Azure resources** scenario, select this repository, choose **Branch** as the entity type, and use `main`. This configures trust in GitHub's OIDC provider with:

- Issuer: `https://token.actions.githubusercontent.com`
- Audience: `api://AzureADTokenExchange`
- Subject: the GitHub repository's `main` branch identity (configure the credential using the GitHub Actions federated-credential scenario in Azure)

In the `crooked-numbers` resource group, grant that identity the **Storage Blob Data Contributor** role at either of these scopes:

- the `crookednumbers` storage account, or
- the `baseball-data` blob container for narrower access.

Storage data-plane access is the only Azure role required by the ingestion workflow. Do not configure an Azure client secret, storage account key, or Azure Storage connection string.

In the GitHub repository, open **Settings → Secrets and variables → Actions → Variables** and create these repository variables:

- `AZURE_CLIENT_ID`: client ID of the federated Azure identity
- `AZURE_TENANT_ID`: Microsoft Entra tenant ID
- `AZURE_SUBSCRIPTION_ID`: Azure subscription ID containing the storage account

These are identifiers rather than credentials and are consumed directly by `azure/login@v2`.

## Run manually

In GitHub, go to **Actions → Ingest Statcast Data → Run workflow**. Select the `main` branch, enter `lookback_days` or leave its default value of `3`, then start the run.

The input controls the rolling date window used by the existing ingestion code. You can still use explicit date ranges for local backfills as described below.

## Verify Azure output

After a successful run, use an Azure CLI identity with permission to read blob data:

```bash
az storage blob list \
  --account-name crookednumbers \
  --container-name baseball-data \
  --prefix "raw/statcast/" \
  --auth-mode login \
  --output table
```

## Local development

Create a virtual environment and install the development dependencies, then use the repository script or invoke the module directly:

```bash
./scripts/run-local.sh
```

```bash
PYTHONPATH=src python -m crooked_numbers_ingest.ingest_statcast
```

For a one-off inclusive date range:

```bash
./scripts/run-local.sh --start-date 2026-03-28 --end-date 2026-08-28
```

The ingestion code supports three storage modes:

- `local`: writes Parquet files under `LOCAL_DATA_ROOT` (default `./data`)
- `azurite`: writes to local Azurite using `AZURITE_CONNECTION_STRING`
- `azure`: writes to Azure Blob Storage using `DefaultAzureCredential` and `BLOB_ACCOUNT_URL`

Local filesystem mode:

```bash
STORAGE_MODE=local LOCAL_DATA_ROOT=./data ./scripts/run-local.sh
```

Azurite mode remains supported for blob-compatible local testing:

```bash
STORAGE_MODE=azurite \
STATCAST_CONTAINER=baseball-data \
AZURITE_CONNECTION_STRING=UseDevelopmentStorage=true \
PYTHONPATH=src python -m crooked_numbers_ingest.ingest_statcast
```

For intentional direct Azure runs, sign in with an identity that has Blob data access and use:

```bash
STORAGE_MODE=azure \
BLOB_ACCOUNT_URL=https://crookednumbers.blob.core.windows.net \
STATCAST_CONTAINER=baseball-data \
PYTHONPATH=src python -m crooked_numbers_ingest.ingest_statcast
```

Azure mode uses `DefaultAzureCredential`. It does not use storage account keys or connection strings.

## Deprecated and optional container assets

Azure Container Apps Job and Azure Container Registry are no longer the primary ingestion runner. The following assets remain temporarily for reference or optional legacy use and should not be treated as the production path:

- `Dockerfile`
- `infra/main.bicep`
- `infra/bootstrap-github-identity.bicep`
- `scripts/deploy.sh`
- `scripts/run-job.sh`

The Docker image can still be used for local experimentation, but its Azure Container Apps/ACR deployment path is deprecated. The local and Azurite modes are still supported.

### Migration cleanup

After the GitHub Actions workflow succeeds and the expected blobs have been verified, disable or delete the old Container Apps Job, ACR, Container Apps Environment, Log Analytics workspace, and job managed identity. Confirm that none of these resources are shared before deleting them.

## Repository boundaries and security

This repository owns raw ingestion only. It does not own dashboard transforms, reporting logic, or presentation-layer shaping.

Never commit Azure credentials, account keys, client secrets, connection strings for real Azure storage, populated `.env` files, or generated authentication artifacts. Azurite's development connection string is allowed only for local Azurite use.
