# PostgreSQL for churn-prac — run from repo root with: make -C local-db up
# Defaults: user postgres / password playground / database churn_prac / schema events.user_actions.
#
# Host port defaults to 5433 (see docker-compose.yml). Tools that assume 5432 will fail unless you set
# POSTGRES_PORT=5432 in .env or use: make url

.PHONY: up down psql reload-data url

up:
	docker compose up -d --build

down:
	docker compose down

psql:
	docker compose exec postgres psql -U postgres -d churn_prac

# Connection string for GUI clients / psql from the host (uses POSTGRES_* from .env if present).
url:
	@echo "postgresql://$${POSTGRES_USER:-postgres}:$${POSTGRES_PASSWORD:-playground}@127.0.0.1:$${POSTGRES_PORT:-5433}/$${POSTGRES_DB:-churn_prac}"

# If you already have a volume from a previous run, init scripts do not re-run.
# Recreate volume and rebuild to reload CSV: docker compose down -v && make up
reload-data:
	docker compose exec -T postgres psql -U postgres -d churn_prac -v ON_ERROR_STOP=1 -c "TRUNCATE events.user_actions;"
	docker compose exec -T postgres psql -U postgres -d churn_prac -v ON_ERROR_STOP=1 -f /workspace/local-db/sql_load/02_load_actions.sql
