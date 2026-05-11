with date_range as (
    select
        min(event_time) as start_date,
        max(event_time) as end_date
    from events.user_actions
),

account_count as (
    select count(distinct u.account_id) as n_account
    from events.user_actions as u
    cross join date_range as d
    where u.event_time >= d.start_date and u.event_time <= d.end_date
)

select
    u.event_type,
    ac.n_account,
    count(*) as n_event,
    count(*)::float / nullif(ac.n_account, 0)::float as events_per_account,
    (d.end_date::date - d.start_date::date)::float / 28.0 as n_months,
    (count(*)::float / nullif(ac.n_account, 0)::float)
    / nullif((d.end_date::date - d.start_date::date)::float / 28.0, 0)
        as events_per_account_per_month
from events.user_actions as u
cross join account_count as ac
cross join date_range as d
where u.event_time >= d.start_date and u.event_time <= d.end_date
group by u.event_type, ac.n_account, d.start_date, d.end_date
order by events_per_account_per_month desc;
