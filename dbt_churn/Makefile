# dbt + uv + SQLFluff + Ruff — uses the churn-prediction repo root venv (run: make sync from here).
# Optional: dbt_churn/.env or repo-root .env for Postgres.

SHELL := /bin/bash

REPO_ROOT := $(abspath $(CURDIR)/..)
PROJECT_DIR ?= dbt_churn
PROFILES_DIR ?= dbt_churn
SQLFLUFF_PATHS := dbt_churn/models dbt_churn/macros dbt_churn/analyses dbt_churn/snapshots dbt_churn/tests dbt_churn/seeds

.PHONY: help sync install lint fix fmt dbt-deps dbt-parse dbt-run dbt-build dbt-test dbt-clean pre-commit

help:
	@echo "Targets (uv runs from repo root: $(REPO_ROOT)):"
	@echo "  make sync          cd repo root; uv sync --frozen --group dev --group dbt"
	@echo "  make install       same as sync"
	@echo "  make lint          ruff + sqlfluff lint ($(SQLFLUFF_PATHS))"
	@echo "  make fix           sqlfluff fix (needs .env for dbt templater)"
	@echo "  make fmt           ruff format ."
	@echo "  make dbt-deps      dbt deps"
	@echo "  make dbt-parse     dbt parse"
	@echo "  make dbt-run       dbt run (profile target from DBT_TARGET; default dev=Postgres)"
	@echo "  make dbt-build     dbt build (runs seeds; Athena: set ATHENA_ML_EXPORT_* for CTAS to S3 Parquet)"
	@echo "  make dbt-test      dbt test"
	@echo "  make dbt-clean     dbt clean"
	@echo "  make pre-commit    pre-commit run --all-files (from repo root)"

install: sync

sync:
	cd "$(REPO_ROOT)" && uv sync --frozen --group dev --group dbt

lint:
	cd "$(REPO_ROOT)" && uv run ruff check .
	cd "$(REPO_ROOT)" && uv run ruff format --check .
	cd "$(REPO_ROOT)" && bash dbt_churn/scripts/sqlfluff-lint.sh $(SQLFLUFF_PATHS)

fix:
	cd "$(REPO_ROOT)" && bash dbt_churn/scripts/sqlfluff-fix.sh $(SQLFLUFF_PATHS)

fmt:
	cd "$(REPO_ROOT)" && uv run ruff format .

dbt-deps:
	@cd "$(REPO_ROOT)" && _env() { if [[ -f dbt_churn/.env ]]; then set -a && source dbt_churn/.env && set +a; elif [[ -f .env ]]; then set -a && source .env && set +a; fi; }; \
		_env && uv run dbt deps --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILES_DIR)

dbt-parse:
	@cd "$(REPO_ROOT)" && _env() { if [[ -f dbt_churn/.env ]]; then set -a && source dbt_churn/.env && set +a; elif [[ -f .env ]]; then set -a && source .env && set +a; fi; }; \
		_env && uv run dbt parse --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILES_DIR)

dbt-run:
	@cd "$(REPO_ROOT)" && _env() { if [[ -f dbt_churn/.env ]]; then set -a && source dbt_churn/.env && set +a; elif [[ -f .env ]]; then set -a && source .env && set +a; fi; }; \
		_env && uv run dbt run --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILES_DIR)

dbt-build:
	@cd "$(REPO_ROOT)" && _env() { if [[ -f dbt_churn/.env ]]; then set -a && source dbt_churn/.env && set +a; elif [[ -f .env ]]; then set -a && source .env && set +a; fi; }; \
		_env && uv run dbt build --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILES_DIR)

dbt-test:
	@cd "$(REPO_ROOT)" && _env() { if [[ -f dbt_churn/.env ]]; then set -a && source dbt_churn/.env && set +a; elif [[ -f .env ]]; then set -a && source .env && set +a; fi; }; \
		_env && uv run dbt test --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILES_DIR)

dbt-clean:
	@cd "$(REPO_ROOT)" && _env() { if [[ -f dbt_churn/.env ]]; then set -a && source dbt_churn/.env && set +a; elif [[ -f .env ]]; then set -a && source .env && set +a; fi; }; \
		_env && uv run dbt clean --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILES_DIR)

pre-commit:
	cd "$(REPO_ROOT)" && uv run pre-commit run --all-files
