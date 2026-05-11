from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd

ID_COLUMNS = ["account_id", "metric_time"]


def load_feature_columns(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Feature columns file not found: {path}")

    with open(path) as f:
        return json.load(f)


def load_current_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Current dataset not found: {path}")

    return pd.read_csv(path)


def prepare_features(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    missing = sorted(set(feature_columns) - set(df.columns))

    if missing:
        raise ValueError(f"Current dataset is missing features: {missing}")

    x = df[feature_columns].copy()

    for col in feature_columns:
        x[col] = pd.to_numeric(x[col], errors="coerce").fillna(0)

    return x


def save_prediction_histogram(predictions: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.hist(predictions["churn_probability"], bins=30)
    plt.xlabel("Predicted churn probability")
    plt.ylabel("Number of customers")
    plt.title("Distribution of Churn Probabilities")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def run_inference(
    current_path: Path,
    model_path: Path,
    feature_columns_path: Path,
    prediction_output_path: Path,
    histogram_output_path: Path,
) -> None:
    model = joblib.load(model_path)
    feature_columns = load_feature_columns(feature_columns_path)

    current_df = load_current_dataset(current_path)
    x_current = prepare_features(current_df, feature_columns)

    churn_probability = model.predict_proba(x_current)[:, 1]
    churn_prediction = (churn_probability >= 0.5).astype(int)

    output_columns = [col for col in ID_COLUMNS if col in current_df.columns]

    predictions = current_df[output_columns].copy()
    predictions["churn_probability"] = churn_probability
    predictions["predicted_is_churn"] = churn_prediction

    predictions = predictions.sort_values(
        "churn_probability",
        ascending=False,
    )

    prediction_output_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(prediction_output_path, index=False)

    save_prediction_histogram(predictions, histogram_output_path)

    summary = {
        "n_customers_scored": len(predictions),
        "mean_churn_probability": float(predictions["churn_probability"].mean()),
        "median_churn_probability": float(predictions["churn_probability"].median()),
        "min_churn_probability": float(predictions["churn_probability"].min()),
        "max_churn_probability": float(predictions["churn_probability"].max()),
        "n_predicted_churn_at_0_5": int(predictions["predicted_is_churn"].sum()),
        "prediction_output_path": str(prediction_output_path),
        "histogram_output_path": str(histogram_output_path),
    }

    print(json.dumps(summary, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--current-path",
        type=Path,
        default=Path("outputs/processed/current.csv"),
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
        "--prediction-output-path",
        type=Path,
        default=Path("outputs/predictions/current_customer_churn_predictions.csv"),
    )
    parser.add_argument(
        "--histogram-output-path",
        type=Path,
        default=Path("outputs/figures/model/churn_probability_histogram.png"),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    run_inference(
        current_path=args.current_path,
        model_path=args.model_path,
        feature_columns_path=args.feature_columns_path,
        prediction_output_path=args.prediction_output_path,
        histogram_output_path=args.histogram_output_path,
    )


if __name__ == "__main__":
    main()
