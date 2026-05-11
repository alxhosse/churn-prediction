# Delegates to local-db (PostgreSQL in Docker).
.PHONY: up down psql reload-data url
up down psql reload-data url:
	@$(MAKE) -C local-db $@
