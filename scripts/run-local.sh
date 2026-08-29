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
venv_python="${repo_root}/.venv/bin/python"

if [[ ! -x "${venv_python}" ]]; then
  echo "Expected virtualenv interpreter at ${venv_python}. Create the project .venv first." >&2
  exit 1
fi

"${venv_python}" -m crooked_numbers_ingest.ingest_statcast
