-- Database is POSTGRES_DB (churn_prac). Events land in schema events.
CREATE SCHEMA IF NOT EXISTS events;

CREATE TABLE events.user_actions (
    account_id text NOT NULL,
    event_time timestamp NOT NULL,
    event_type text NOT NULL,
    product_id integer,
    additional_data text
);

CREATE INDEX idx_user_actions_account_id ON events.user_actions (account_id);
CREATE INDEX idx_user_actions_event_time ON events.user_actions (event_time);
