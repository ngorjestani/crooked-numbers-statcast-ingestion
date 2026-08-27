# AGENTS.md

Guidance for future Codex runs in this repository.

## Repository Scope

- Treat this repository as the ingestion boundary for Crooked Numbers baseball analytics.
- Keep raw ingestion concerns separate from dashboard transforms, reporting logic, and presentation-layer shaping.
- Do not introduce .NET or React dashboard work into this repo unless explicitly requested.

## Architecture and Authentication

- Prefer Azure managed identity and `DefaultAzureCredential` for Azure access.
- Do not use Azure account keys.
- Do not use Azure storage connection strings unless the user explicitly directs otherwise.
- Preserve the raw blob layout convention for Statcast ingestion:
  `raw/statcast/season=YYYY/game_date=YYYY-MM-DD/statcast.parquet`

## Engineering Conventions

- Keep modules small, focused, and testable.
- Favor clear boundaries between data acquisition, validation, serialization, and Azure I/O.
- Avoid mixing ingestion logic with downstream transform logic.
- Do not add infrastructure deployment steps unless explicitly asked.
- Do not deploy Azure resources unless explicitly asked.

## Safety and Change Scope

- Never commit secrets, credentials, `.env`, or generated auth artifacts.
- If authentication is needed, prefer identity-based local and cloud flows.
- Make the minimum set of changes required for the requested task.
- If a change would broaden this repo beyond ingestion responsibilities, stop and ask.
