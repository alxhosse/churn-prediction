{{ config(materialized='table') }}

with date_vals as (
    {{ metric_date_vals_from_user_actions() }}
),

metric_defs as (
    select
        metric_name_id,
        metric_name,
        event_type,
        lookback_days
    from {{ ref('metric_name') }}
),

metric_values as (
    select
        u.account_id,
        d.metric_time,
        m.metric_name_id,
        count(*) as metric_value
    from {{ source('events', 'user_actions') }} as u
    inner join metric_defs as m
        on u.event_type = m.event_type
    inner join date_vals as d
        on
            cast(u.event_time as timestamp) < d.metric_time
            and cast(u.event_time as timestamp)
            >= {{
                metric_lookback_lower_bound(
                    'd.metric_time',
                    'm.lookback_days'
                )
            }}
    group by
        u.account_id,
        d.metric_time,
        m.metric_name_id
)

select
    account_id,
    metric_time,
    metric_name_id,
    metric_value
from metric_values
where metric_value > 0
