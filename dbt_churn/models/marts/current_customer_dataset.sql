{% if target.type == 'athena' %}
{{ config(
    materialized='table',
    external_location=env_var(
        'ATHENA_ML_EXPORT_CURRENT_CUSTOMER_PREFIX',
        's3://must-set-ATHENA_ML_EXPORT_CURRENT_CUSTOMER_PREFIX/'
    ),
    format='parquet',
) }}
{% else %}
    {{ config(materialized='table') }}
{% endif %}

with latest_metric_time as (
    select max(metric_time) as metric_time
    from {{ ref('all_metrics') }}
),

current_metrics as (
    select
        m.account_id,
        m.metric_time,
        mn.metric_name,
        m.metric_value
    from {{ ref('all_metrics') }} as m
    inner join {{ ref('metric_name') }} as mn
        on m.metric_name_id = mn.metric_name_id
    inner join latest_metric_time as l
        on m.metric_time = l.metric_time
)

select
    cm.account_id,
    cm.metric_time,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_EBookDownloaded_last_28d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_ebookdownloaded_last_28d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_ReadingOwnedBook_last_28d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_readingownedbook_last_28d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_ReadingFreePreview_last_28d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_readingfreepreview_last_28d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_SearchMade_last_28d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_searchmade_last_28d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_HighlightCreated_last_28d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_highlightcreated_last_28d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_BookmarkCreated_last_28d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_bookmarkcreated_last_28d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_total_events_last_90d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_total_events_last_90d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_unique_products_last_90d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_unique_products_last_90d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_free_content_actions_last_28d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_free_content_actions_last_28d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_enhanced_reading_actions_last_28d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_enhanced_reading_actions_last_28d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'pct_reading_owned_book_events_last_28d'
                    then cm.metric_value
            end
        ),
        0
    )
        as pct_reading_owned_book_events_last_28d,

    coalesce(
        max(
            case
                when
                    cm.metric_name = 'n_downloads_per_unique_product_last_90d'
                    then cm.metric_value
            end
        ),
        0
    )
        as n_downloads_per_unique_product_last_90d

from current_metrics as cm
group by
    cm.account_id,
    cm.metric_time
