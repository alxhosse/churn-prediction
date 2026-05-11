{{ config(materialized='table') }}

with purchase_events as (
    select
        account_id,
        cast(cast(event_time as timestamp) as date) as purchase_date
    from {{ source('events', 'user_actions') }}
    where event_type in ('ReadingOwnedBook', 'EBookDownloaded')
),

first_period_purchasers as (
    select
        account_id,
        min(purchase_date) as first_purchase_date
    from purchase_events
    where purchase_date < date '2020-03-01'
    group by account_id
),

second_period_purchasers as (
    select distinct account_id
    from purchase_events
    where purchase_date >= date '2020-03-01'
)

select
    p.account_id,
    date '2020-03-01' as observation_date,
    (s.account_id is null) as is_churn
from first_period_purchasers as p
left join second_period_purchasers as s
    on p.account_id = s.account_id
