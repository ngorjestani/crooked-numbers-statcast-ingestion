#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

resource_group="${AZURE_RESOURCE_GROUP:-crooked-numbers}"
parameters_file="${1:-${repo_root}/infra/parameters/dev.bicepparam}"

az deployment group create \
  --resource-group "${resource_group}" \
  --template-file "${repo_root}/infra/main.bicep" \
  --parameters "${parameters_file}"
