from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap

TARGET_COLUMN = "is_churn"


def load_feature_columns(path: Path) -> list[str]:
    with open(path) as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data-path",
        type=Path,
        default=Path("outputs/processed/valid.csv"),
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path("outputs/models/xgboost_churn_model.joblib"),
    )
    parser.add_argument(
        "--feature-columns-path",
        type=Path,
        default=Path("outputs/models/feature_columns.json"),
    )
    parser.add_argument(
        "--figure-dir",
        type=Path,
        default=Path("outputs/figures/model"),
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("outputs/reports"),
    )

    args = parser.parse_args()

    args.figure_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    model = joblib.load(args.model_path)
    feature_columns = load_feature_columns(args.feature_columns_path)

    df = pd.read_csv(args.data_path)
    x = df[feature_columns].copy()

    for col in feature_columns:
        x[col] = pd.to_numeric(x[col], errors="coerce").fillna(0)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x)

    shap.summary_plot(
        shap_values,
        x,
        show=False,
        max_display=12,
    )
    plt.tight_layout()
    plt.savefig(args.figure_dir / "shap_summary.png", bbox_inches="tight")
    plt.close()

    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "mean_abs_shap": abs(shap_values).mean(axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False)

    importance.to_csv(
        args.report_dir / "shap_feature_importance.csv",
        index=False,
    )

    print(importance)


if __name__ == "__main__":
    main()
