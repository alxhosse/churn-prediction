from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    RocCurveDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier

TARGET_COLUMN = "is_churn"
ID_COLUMNS = ["account_id", "observation_date"]


def load_feature_columns(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Feature columns file not found: {path}")

    with open(path) as f:
        return json.load(f)


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    return pd.read_csv(path)


def split_xy(
    df: pd.DataFrame, feature_columns: list[str]
) -> tuple[pd.DataFrame, pd.Series]:
    missing = sorted(set(feature_columns + [TARGET_COLUMN]) - set(df.columns))

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    x = df[feature_columns].copy()
    y = df[TARGET_COLUMN].astype(bool).astype(int)

    return x, y


def train_model(
    x_train: pd.DataFrame,
    y_train: pd.Series,
) -> GridSearchCV:
    base_model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
    )

    param_grid = {
        "n_estimators": [100, 250],
        "max_depth": [2, 3, 4],
        "learning_rate": [0.03, 0.1],
        "subsample": [0.8, 1.0],
        "colsample_bytree": [0.8, 1.0],
    }

    search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=3,
        verbose=1,
        n_jobs=-1,
    )

    search.fit(x_train, y_train)

    return search


def evaluate_model(
    model: XGBClassifier,
    x_valid: pd.DataFrame,
    y_valid: pd.Series,
    output_dir: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    y_prob = model.predict_proba(x_valid)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "roc_auc": float(roc_auc_score(y_valid, y_prob)),
        "accuracy": float(accuracy_score(y_valid, y_pred)),
        "precision": float(precision_score(y_valid, y_pred)),
        "recall": float(recall_score(y_valid, y_pred)),
        "confusion_matrix": confusion_matrix(y_valid, y_pred).tolist(),
        "classification_report": classification_report(
            y_valid,
            y_pred,
            output_dict=True,
        ),
    }

    RocCurveDisplay.from_predictions(y_valid, y_prob)
    plt.title("XGBoost Churn ROC Curve")
    plt.tight_layout()
    plt.savefig(output_dir / "roc_curve.png")
    plt.close()

    return metrics


def save_feature_importance(
    model: XGBClassifier,
    feature_columns: list[str],
    output_dir: Path,
) -> None:
    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    importance.to_csv(output_dir / "feature_importance.csv", index=False)

    plt.figure(figsize=(8, 5))
    plt.barh(importance["feature"], importance["importance"])
    plt.gca().invert_yaxis()
    plt.xlabel("Importance")
    plt.title("XGBoost Feature Importance")
    plt.tight_layout()
    plt.savefig(output_dir / "feature_importance.png")
    plt.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--train-path",
        type=Path,
        default=Path("/opt/ml/input/data/training/train.csv"),
    )
    parser.add_argument(
        "--valid-path",
        type=Path,
        default=Path("/opt/ml/input/data/training/valid.csv"),
    )
    parser.add_argument(
        "--feature-columns-path",
        type=Path,
        default=Path("/opt/ml/input/data/training/feature_columns.json"),
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path("/opt/ml/model"),
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("/opt/ml/output/data/reports"),
    )
    parser.add_argument(
        "--figure-dir",
        type=Path,
        default=Path("/opt/ml/output/data/figures"),
    )

    args, unknown = parser.parse_known_args()

    print("UNKNOWN_ARGS:", unknown)

    return args


def main() -> None:
    args = parse_args()

    args.model_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    args.figure_dir.mkdir(parents=True, exist_ok=True)

    feature_columns = load_feature_columns(args.feature_columns_path)

    train_df = load_dataset(args.train_path)
    valid_df = load_dataset(args.valid_path)

    x_train, y_train = split_xy(train_df, feature_columns)
    x_valid, y_valid = split_xy(valid_df, feature_columns)

    search = train_model(x_train, y_train)

    best_model = search.best_estimator_

    metrics = evaluate_model(
        best_model,
        x_valid,
        y_valid,
        args.figure_dir,
    )

    metrics["best_params"] = search.best_params_
    metrics["best_cv_roc_auc"] = float(search.best_score_)

    save_feature_importance(
        best_model,
        feature_columns,
        args.figure_dir,
    )

    joblib.dump(best_model, args.model_dir / "xgboost_churn_model.joblib")

    with open(args.model_dir / "feature_columns.json", "w") as f:
        json.dump(feature_columns, f, indent=2)

    with open(args.report_dir / "training_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
