{% macro metric_date_vals_from_user_actions() %}
    {% if target.type == 'athena' %}
        select cast(u.day as timestamp) as metric_time
        from (
            select
                cast(min(cast(event_time as timestamp)) as date) as d0,
                cast(max(cast(event_time as timestamp)) as date) as d1
            from {{ source('events', 'user_actions') }}
        ) as bounds
        cross join unnest(sequence(bounds.d0, bounds.d1, interval '7' day)) as u (day)
    {% else %}
        select generate_series(
            (select min(event_time)::date from {{ source('events', 'user_actions') }}),
            (select max(event_time)::date from {{ source('events', 'user_actions') }}),
            interval '7 day'
        )::timestamp as metric_time
    {% endif %}
{% endmacro %}

{% macro metric_lookback_lower_bound(metric_time_col, lookback_days_col) %}
    {% if target.type == 'athena' %}
        date_add('day', -cast({{ lookback_days_col }} as integer), {{ metric_time_col }})
    {% else %}
        {{ metric_time_col }} - ({{ lookback_days_col }} || ' day')::interval
    {% endif %}
{% endmacro %}

{% macro metric_window_start(metric_time_col, n_days) %}
    {% if target.type == 'athena' %}
        date_add('day', -{{ n_days }}, {{ metric_time_col }})
    {% else %}
        {{ metric_time_col }} - interval '{{ n_days }} day'
    {% endif %}
{% endmacro %}

{% macro as_double(expr) %}
    {% if target.type == 'athena' %}
        cast({{ expr }} as double)
    {% else %}
        cast({{ expr }} as double precision)
    {% endif %}
{% endmacro %}
