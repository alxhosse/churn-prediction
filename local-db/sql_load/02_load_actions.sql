-- CSV at repo root; docker-compose mounts repo root at /workspace.
SET client_encoding = 'UTF8';

COPY events.user_actions (account_id, event_time, event_type, product_id, additional_data)
FROM '/workspace/actions2load.csv'
WITH (FORMAT csv, HEADER true);
