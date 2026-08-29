#!/usr/bin/env bash

set -euo pipefail

resource_group="${AZURE_RESOURCE_GROUP:-crooked-numbers}"
job_name="${AZURE_CONTAINER_APP_JOB_NAME:-job-statcast-ingest-dev}"

az containerapp job start \
  --name "${job_name}" \
  --resource-group "${resource_group}"
