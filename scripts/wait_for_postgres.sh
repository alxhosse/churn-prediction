#!/usr/bin/env bash
# Wait until PostgreSQL accepts TCP on POSTGRES_HOST:POSTGRES_PORT (mirror .github/workflows/dbt-ci.yml).
# Loads dbt_churn/.env or repo-root .env when present — same precedence as sqlfluff-lint.sh.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

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

host="${POSTGRES_HOST:-127.0.0.1}"
port="${POSTGRES_PORT:-5433}"

for i in $(seq 1 60); do
  if (exec 3<>"/dev/tcp/${host}/${port}") 2>/dev/null; then
    exec 3>&-
    echo "PostgreSQL reachable on ${host}:${port}"
    exit 0
  fi
  echo "waiting for ${host}:${port} (${i}/60)..."
  sleep 1
done

echo "PostgreSQL never became reachable on ${host}:${port} (hint: run \`make up\`)." >&2
exit 1
