{{ config(materialized='table') }}

with date_vals as (

    {{ metric_date_vals_from_user_actions() }}

),

base_events as (

    select
        account_id,
        cast(event_time as timestamp) as event_time,
        event_type,
        product_id
    from {{ source('events', 'user_actions') }}

),

/* -------------------------------------------------
   TOTAL EVENTS - 90D
------------------------------------------------- */

total_events as (

    select
        e.account_id,
        d.metric_time,
        7 as metric_name_id,
        {{ as_double('count(*)') }} as metric_value
    from base_events as e
    inner join date_vals as d
        on
            e.event_time < d.metric_time
            and e.event_time >= {{ metric_window_start('d.metric_time', 90) }}
    group by
        e.account_id,
        d.metric_time

),

/* -------------------------------------------------
   UNIQUE PRODUCTS - 90D
------------------------------------------------- */

unique_products as (

    select
        e.account_id,
        d.metric_time,
        8 as metric_name_id,
        {{ as_double('count(distinct e.product_id)') }} as metric_value
    from base_events as e
    inner join date_vals as d
        on
            e.event_time < d.metric_time
            and e.event_time >= {{ metric_window_start('d.metric_time', 90) }}
    where e.product_id is not null
    group by
        e.account_id,
        d.metric_time

),

/* -------------------------------------------------
   FREE CONTENT ACTIONS
------------------------------------------------- */

free_content_actions as (

    select
        m.account_id,
        m.metric_time,
        9 as metric_name_id,
        {{ as_double('sum(m.metric_value)') }} as metric_value
    from {{ ref('metric') }} as m
    inner join {{ ref('metric_name') }} as mn
        on m.metric_name_id = mn.metric_name_id
    where
        mn.metric_name in (
            'n_ReadingFreePreview_last_28d'
        )
    group by
        m.account_id,
        m.metric_time

),

/* -------------------------------------------------
   ENHANCED READING ACTIONS
------------------------------------------------- */

enhanced_reading_actions as (

    select
        m.account_id,
        m.metric_time,
        10 as metric_name_id,
        {{ as_double('sum(m.metric_value)') }} as metric_value
    from {{ ref('metric') }} as m
    inner join {{ ref('metric_name') }} as mn
        on m.metric_name_id = mn.metric_name_id
    where
        mn.metric_name in (
            'n_HighlightCreated_last_28d'
        )
    group by
        m.account_id,
        m.metric_time

),

/* -------------------------------------------------
   RATIO: OWNED BOOK / TOTAL EVENTS
------------------------------------------------- */

owned_book_ratio as (

    select
        d.account_id,
        d.metric_time,
        11 as metric_name_id,

        {{
            as_double(
                "case when d.metric_value > 0 then "
                ~ "coalesce(n.metric_value, 0) / d.metric_value else 0 end"
            )
        }} as metric_value

    from total_events as d

    left join {{ ref('metric') }} as n
        on
            d.account_id = n.account_id
            and d.metric_time = n.metric_time
            and n.metric_name_id = 1

),

/* -------------------------------------------------
   RATIO: DOWNLOADS / UNIQUE PRODUCTS
------------------------------------------------- */

downloads_per_product as (

    select
        d.account_id,
        d.metric_time,
        12 as metric_name_id,

        {{
            as_double(
                "case when d.metric_value > 0 then "
                ~ "coalesce(n.metric_value, 0) / d.metric_value else 0 end"
            )
        }} as metric_value

    from unique_products as d

    left join {{ ref('metric') }} as n
        on
            d.account_id = n.account_id
            and d.metric_time = n.metric_time
            and n.metric_name_id = 2

)

select * from total_events

union all

select * from unique_products

union all

select * from free_content_actions

union all

select * from enhanced_reading_actions

union all

select * from owned_book_ratio

union all

select * from downloads_per_product
