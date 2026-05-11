from math import ceil
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine

OUTPUT_DIR = Path("outputs/figures/metric_qa")


QUERY = """
select
    metric_name,
    metric_time,
    avg_value,
    min_value,
    max_value,
    n_calc
from dbt_schema.metric_stats_over_time
order by metric_name, metric_time
"""


def plot_metric(df: pd.DataFrame, metric_name: str) -> None:
    metric_df = df[df["metric_name"] == metric_name].copy()

    metric_df["metric_time"] = pd.to_datetime(metric_df["metric_time"])

    fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)

    plots = [
        ("max_value", "Max Value"),
        ("avg_value", "Average Value"),
        ("min_value", "Min Value"),
        ("n_calc", "Number of Accounts"),
    ]

    for ax, (column, title) in zip(axes, plots):
        ax.plot(
            metric_df["metric_time"],
            metric_df[column],
            linewidth=2,
        )

        ymax = metric_df[column].dropna().max()

        if pd.notna(ymax) and ymax > 0:
            ax.set_ylim(0, ceil(1.1 * ymax))

        ax.set_title(title)
        ax.grid(True)

    plt.xticks(rotation=45)
    plt.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{metric_name}.png"

    plt.savefig(output_path)
    plt.close()

    print(f"Saved {output_path}")


def main() -> None:
    engine = create_engine(
        "postgresql+psycopg2://postgres:playground@localhost:5433/churn_prac"
    )

    df = pd.read_sql(QUERY, engine)

    metric_names = sorted(df["metric_name"].unique())

    for metric_name in metric_names:
        plot_metric(df, metric_name)


if __name__ == "__main__":
    main()
