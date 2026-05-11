# Repo root helpers: local Postgres (Docker), plus CI-equivalent lint (mirror .github/workflows/dbt-ci.yml).
SHELL := /bin/bash
REPO_ROOT := $(abspath $(CURDIR))

# Delegates to local-db (PostgreSQL in Docker).
.PHONY: up down psql reload-data url
up down psql reload-data url:
	@$(MAKE) -C local-db $@

.PHONY: sync wait-postgres dbt-ci ci
.PHONY: lint-check

sync:
	cd "$(REPO_ROOT)" && uv sync --frozen --group dev --group dbt

wait-postgres:
	@bash "$(REPO_ROOT)/scripts/wait_for_postgres.sh"

# Full pipeline (postgres must be reachable: e.g. `make up`).
dbt-ci ci:
	bash "$(REPO_ROOT)/scripts/run_local_dbt_ci.sh"

# Same checks as CI after `uv sync`, but skips sync (faster re-runs with DB up).
lint-check:
	bash "$(REPO_ROOT)/scripts/run_local_dbt_ci.sh" --lint-only
