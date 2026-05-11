from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

TRAIN_ID_COLUMNS = ["account_id", "observation_date"]
CURRENT_ID_COLUMNS = ["account_id", "metric_time"]
TARGET_COLUMN = "is_churn"


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    # Directory or .parquet: Athena CTAS (dbt) Parquet export under one prefix.
    if path.is_dir() or path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def get_feature_columns(train_df: pd.DataFrame, current_df: pd.DataFrame) -> list[str]:
    train_features = [
        col for col in train_df.columns if col not in TRAIN_ID_COLUMNS + [TARGET_COLUMN]
    ]

    current_features = [
        col for col in current_df.columns if col not in CURRENT_ID_COLUMNS
    ]

    missing_in_current = sorted(set(train_features) - set(current_features))
    extra_in_current = sorted(set(current_features) - set(train_features))

    if missing_in_current or extra_in_current:
        raise ValueError(
            "Feature mismatch between train and current datasets.\n"
            f"Missing in current: {missing_in_current}\n"
            f"Extra in current: {extra_in_current}"
        )

    return train_features


def preprocess(
    train_path: Path,
    current_path: Path,
    output_dir: Path,
    test_size: float,
    random_state: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    train_df = load_dataset(train_path)
    current_df = load_dataset(current_path)

    if TARGET_COLUMN not in train_df.columns:
        raise ValueError(f"Training dataset must contain '{TARGET_COLUMN}'")

    feature_columns = get_feature_columns(train_df, current_df)

    train_df[TARGET_COLUMN] = train_df[TARGET_COLUMN].astype(bool).astype(int)

    for col in feature_columns:
        train_df[col] = pd.to_numeric(train_df[col], errors="coerce").fillna(0)
        current_df[col] = pd.to_numeric(current_df[col], errors="coerce").fillna(0)

    train_part, valid_part = train_test_split(
        train_df,
        test_size=test_size,
        random_state=random_state,
        stratify=train_df[TARGET_COLUMN],
    )

    train_part.to_csv(output_dir / "train.csv", index=False)
    valid_part.to_csv(output_dir / "valid.csv", index=False)
    current_df.to_csv(output_dir / "current.csv", index=False)

    with open(output_dir / "feature_columns.json", "w") as f:
        json.dump(feature_columns, f, indent=2)

    metadata = {
        "n_train_rows": len(train_part),
        "n_valid_rows": len(valid_part),
        "n_current_rows": len(current_df),
        "n_features": len(feature_columns),
        "target_column": TARGET_COLUMN,
        "feature_columns": feature_columns,
    }

    with open(output_dir / "preprocess_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(json.dumps(metadata, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--train-path",
        type=Path,
        default=Path("outputs/churn_training_dataset.csv"),
    )
    parser.add_argument(
        "--current-path",
        type=Path,
        default=Path("outputs/current_customer_dataset.csv"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/processed"),
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    preprocess(
        train_path=args.train_path,
        current_path=args.current_path,
        output_dir=args.output_dir,
        test_size=args.test_size,
        random_state=args.random_state,
    )


if __name__ == "__main__":
    main()
