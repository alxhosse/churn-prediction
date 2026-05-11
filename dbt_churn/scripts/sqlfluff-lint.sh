#!/usr/bin/env bash
# Load env for SQLFluff's dbt templater; run from churn-prediction repo root via uv.
set -euo pipefail

churn_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$churn_root"

if [[ -f dbt_churn/.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source dbt_churn/.env
  set +a
elif [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
else
  echo "sqlfluff-lint.sh: no dbt_churn/.env or repo .env to source — relying on Postgres env vars already exported (CI) / profiles.yml defaults (local)." >&2
fi

exec uv run sqlfluff lint --config dbt_churn/.sqlfluff "$@"
