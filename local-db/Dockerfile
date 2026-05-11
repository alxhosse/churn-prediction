# PostgreSQL for churn-prediction (same pattern as sqlplayground).
FROM postgres:16-alpine

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=playground
ENV POSTGRES_DB=churn_prac

# Runs once on first start when the data volume is empty.
COPY sql_load/01_schema.sql /docker-entrypoint-initdb.d/01_schema.sql
COPY sql_load/02_load_actions.sql /docker-entrypoint-initdb.d/02_load_actions.sql

EXPOSE 5432
