with account_count as (
    select count(distinct account_id) as n_account
    from {{ source('events', 'user_actions') }}
)

select
    mn.metric_name,

    ac.n_account,

    count(distinct m.account_id) as count_with_metric,

    count(distinct m.account_id)::float
    / nullif(ac.n_account, 0)::float
        as pcnt_with_metric,

    avg(m.metric_value) as avg_value,
    min(m.metric_value) as min_value,
    max(m.metric_value) as max_value,

    min(m.metric_time) as earliest_metric,
    max(m.metric_time) as latest_metric

from {{ ref('metric') }} as m

inner join {{ ref('metric_name') }} as mn
    on m.metric_name_id = mn.metric_name_id

cross join account_count as ac

group by
    mn.metric_name,
    ac.n_account

order by
    pcnt_with_metric desc;
