{% if target.type == 'athena' %}
{{ config(
    materialized='table',
    external_location=env_var(
        'ATHENA_ML_EXPORT_CHURN_TRAINING_PREFIX',
        's3://must-set-ATHENA_ML_EXPORT_CHURN_TRAINING_PREFIX/'
    ),
    format='parquet',
) }}
{% else %}
    {{ config(materialized='table') }}
{% endif %}

with observation as (
    select
        account_id,
        observation_date,
        is_churn
    from {{ ref('observation') }}
    where observation_date = date '2020-03-01'
),

metric_snapshot as (
    select max(metric_time) as metric_time
    from {{ ref('all_metrics') }}
    where metric_time <= timestamp '2020-03-01 00:00:00'
),

metrics_at_snapshot as (
    select
        m.account_id,
        mn.metric_name,
        m.metric_value
    from {{ ref('all_metrics') }} as m
    inner join {{ ref('metric_name') }} as mn
        on m.metric_name_id = mn.metric_name_id
    inner join metric_snapshot as s
        on m.metric_time = s.metric_time
)

select
    o.account_id,
    o.observation_date,
    o.is_churn,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_EBookDownloaded_last_28d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_ebookdownloaded_last_28d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_ReadingOwnedBook_last_28d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_readingownedbook_last_28d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_ReadingFreePreview_last_28d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_readingfreepreview_last_28d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_SearchMade_last_28d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_searchmade_last_28d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_HighlightCreated_last_28d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_highlightcreated_last_28d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_BookmarkCreated_last_28d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_bookmarkcreated_last_28d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_total_events_last_90d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_total_events_last_90d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_unique_products_last_90d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_unique_products_last_90d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_free_content_actions_last_28d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_free_content_actions_last_28d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_enhanced_reading_actions_last_28d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_enhanced_reading_actions_last_28d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'pct_reading_owned_book_events_last_28d'
                    then m.metric_value
            end
        ),
        0
    )
        as pct_reading_owned_book_events_last_28d,

    coalesce(
        max(
            case
                when
                    m.metric_name = 'n_downloads_per_unique_product_last_90d'
                    then m.metric_value
            end
        ),
        0
    )
        as n_downloads_per_unique_product_last_90d

from observation as o
left join metrics_at_snapshot as m
    on o.account_id = m.account_id

group by
    o.account_id,
    o.observation_date,
    o.is_churn
