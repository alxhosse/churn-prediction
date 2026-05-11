#!/usr/bin/env bash
# Mirrors .github/workflows/dbt-ci.yml:
#   default: uv sync → wait Postgres → dbt deps/parse → SQLFluff → ruff check + ruff format --check
#   --lint-only: skip uv sync (rest unchanged — still waits for DB).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

skip_sync=false
if [[ "${1:-}" == "--lint-only" ]]; then
  skip_sync=true
fi

sqlfluff_paths=(
  dbt_churn/models
  dbt_churn/macros
  dbt_churn/analyses
  dbt_churn/tests
  dbt_churn/seeds
)

if [[ "$skip_sync" != true ]]; then
  uv sync --frozen --group dev --group dbt
fi

bash "$(dirname "${BASH_SOURCE[0]}")/wait_for_postgres.sh"

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
fi

export DBT_TARGET="${DBT_TARGET:-dev}"

uv run dbt deps --project-dir dbt_churn --profiles-dir dbt_churn
uv run dbt parse --project-dir dbt_churn --profiles-dir dbt_churn
bash dbt_churn/scripts/sqlfluff-lint.sh "${sqlfluff_paths[@]}"
uv run ruff check .
uv run ruff format --check .
