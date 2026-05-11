{{ config(materialized='view') }}

select
    mn.metric_name,

    count(distinct m.metric_time) as n_metric_dates,

    min(m.metric_time) as earliest_metric,
    max(m.metric_time) as latest_metric,

    min(m.metric_value) as min_metric_value,
    avg(m.metric_value) as avg_metric_value,
    max(m.metric_value) as max_metric_value

from {{ ref('all_metrics') }} as m

inner join {{ ref('metric_name') }} as mn
    on m.metric_name_id = mn.metric_name_id

group by
    mn.metric_name

order by
    mn.metric_name
