#!/usr/bin/env bash
# Load env for SQLFluff's dbt templater; run from churn-prac repo root via uv.
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
  echo "sqlfluff-fix.sh: no dbt_churn/.env or repo .env — using profiles.yml defaults." >&2
  echo "sqlfluff-fix.sh: target dev requires a reachable Postgres; see dbt_churn/.env.example." >&2
fi

exec uv run sqlfluff fix --config dbt_churn/.sqlfluff "$@"
