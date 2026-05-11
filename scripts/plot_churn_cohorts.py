import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATASET_PATH = "outputs/churn_training_dataset.csv"

METRICS = [
    "n_ebookdownloaded_last_28d",
    "n_readingownedbook_last_28d",
    "n_readingfreepreview_last_28d",
    "n_searchmade_last_28d",
    "n_highlightcreated_last_28d",
    "n_bookmarkcreated_last_28d",
    "n_total_events_last_90d",
    "n_unique_products_last_90d",
    "n_free_content_actions_last_28d",
    "n_enhanced_reading_actions_last_28d",
    "pct_reading_owned_book_events_last_28d",
    "n_downloads_per_unique_product_last_90d",
]


def cohort_plot(
    data_set_path: str,
    metric_to_plot: str,
    ncohort: int = 10,
    exclude_zeros: bool = False,
    log_scale: bool = False,
) -> None:
    assert os.path.isfile(data_set_path), (
        f'"{data_set_path}" is not a valid dataset path'
    )

    churn_data = pd.read_csv(data_set_path, index_col=[0, 1])

    if exclude_zeros:
        churn_data = churn_data[churn_data[metric_to_plot] != 0]

    groups = pd.qcut(
        churn_data[metric_to_plot],
        ncohort,
        duplicates="drop",
    )

    cohort_means = churn_data.groupby(groups, observed=False)[metric_to_plot].mean()
    cohort_churns = churn_data.groupby(groups, observed=False)["is_churn"].mean()

    plot_frame = pd.DataFrame(
        {
            metric_to_plot: cohort_means.values,
            "churn_rate": cohort_churns.values,
        }
    )

    plt.figure(figsize=(6, 4))
    plt.plot(
        metric_to_plot,
        "churn_rate",
        data=plot_frame,
        marker="o",
        linewidth=2,
    )

    plt.xlabel(f'Cohort Average of "{metric_to_plot}"')
    plt.ylabel("Cohort Churn Rate")
    plt.grid()
    plt.gca().set_ylim(bottom=0)

    if log_scale:
        plt.gca().set_xscale("log")

    output_dir = Path("outputs/figures/churn_cohorts")
    output_dir.mkdir(parents=True, exist_ok=True)

    save_path = output_dir / f"{metric_to_plot}_churn_cohort.png"
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

    print(f"Saved plot to {save_path}")


def main() -> None:
    for metric in METRICS:
        cohort_plot(
            DATASET_PATH,
            metric_to_plot=metric,
            ncohort=10,
            exclude_zeros=False,
            log_scale=False,
        )


if __name__ == "__main__":
    main()
