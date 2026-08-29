#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

if [[ -f "${repo_root}/.env" ]]; then
  set -a
  source "${repo_root}/.env"
  set +a
fi

export PYTHONPATH="${repo_root}/src"

python -m crooked_numbers_ingest.ingest_statcast
