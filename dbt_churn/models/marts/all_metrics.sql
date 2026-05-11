{{ config(materialized='view') }}

select
    account_id,
    metric_time,
    metric_name_id,
    metric_value
from {{ ref('metric') }}

union all

select
    account_id,
    metric_time,
    metric_name_id,
    metric_value
from {{ ref('metric_derived') }}
