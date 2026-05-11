from math import ceil
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine

EVENTS = [
    "AddOrUpdateCoupon",
    "AddProductOffering",
    "BookmarkCreated",
    "CommentCreated",
    "CrossReferenceTermOpened",
    "DashboardLivebookLinkOpened",
    "EBookDownloaded",
    "EBookRegistration",
    "ExerciseSolved",
    "FirstLivebookAccess",
    "FirstManningAccess",
    "FreeContentCheckout",
    "GoToManningShoppingCart",
    "HighlightCreated",
    "LivebookAccountConfirmation",
    "LivebookLogin",
    "LivebookRegistration",
    "NoteCreated",
    "OrderConfirmationLivebookLinkOpened",
    "ProductLiveaudioUpsell",
    "ProductLookInsideLivebookLinkOpened",
    "ProductSeeFreeLinkOpened",
    "ProductTocLivebookLinkOpened",
    "ReadingFreePreview",
    "ReadingOpenChapter",
    "ReadingOwnedBook",
    "RemoveProductOffering",
    "SearchMade",
    "SearchResultOpened",
    "ShareableLinkCreated",
    "ShareableLinkOpened",
    "SherlockHolmesClueFound",
    "UnknownOriginLivebookLinkOpened",
    "UpvoteGiven",
    "WishlistItemAdded",
]


QUERY = """
with date_range as (
    select generate_series(
        (select min(event_time)::date from events.user_actions),
        (select max(event_time)::date from events.user_actions),
        interval '1 day'
    )::date as event_date
),
the_event as (
    select *
    from events.user_actions
    where event_type = %(event_type)s
)
select
    d.event_date,
    count(e.*) as n_event
from date_range d
left join the_event e
    on d.event_date = e.event_time::date
group by d.event_date
order by d.event_date;
"""


def plot_event(df: pd.DataFrame, event_type: str, output_dir: Path) -> None:
    df["event_date"] = pd.to_datetime(df["event_date"])

    plt.figure(figsize=(8, 4))
    plt.plot(df["event_date"], df["n_event"], linewidth=2)

    plt.ylim(0, ceil(1.1 * df["n_event"].max()))
    plt.title(f"{event_type} event count")
    plt.xlabel("Date")
    plt.ylabel("Number of events")
    plt.xticks(rotation=45)
    plt.tight_layout()

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{event_type}_event_count.png"
    plt.savefig(output_path)
    plt.close()

    print(f"Saved {output_path}")


def main() -> None:
    engine = create_engine(
        "postgresql+psycopg2://postgres:playground@localhost:5433/churn_prac"
    )

    output_dir = Path("outputs/figures")

    for event_type in EVENTS:
        df = pd.read_sql(QUERY, engine, params={"event_type": event_type})
        plot_event(df, event_type, output_dir)


if __name__ == "__main__":
    main()
