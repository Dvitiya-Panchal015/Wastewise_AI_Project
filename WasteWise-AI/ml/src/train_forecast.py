
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "perishable_inventory.csv"
MODEL_DIR = PROJECT_ROOT / "models"
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def add_features(df):
    """Create features that are available before the sales day."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df = df.sort_values(["product_id", "date"]).reset_index(drop=True)

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Lag features use previous sales only.
    grouped = df.groupby("product_id")["units_sold"]
    df["sales_lag_1"] = grouped.shift(1)
    df["sales_lag_7"] = grouped.shift(7)

    # Rolling average excludes the current day's sales.
    df["sales_avg_7d"] = (
        df.groupby("product_id")["units_sold"]
        .transform(lambda s: s.shift(1).rolling(7, min_periods=3).mean())
    )

    return df


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required = ["product_id", "date", "units_sold"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df.duplicated(["product_id", "date"]).any():
        raise ValueError("Duplicate product-date records detected.")

    if (df["units_sold"].dropna() < 0).any():
        raise ValueError("units_sold contains negative values.")

    df = df.dropna(subset=required).copy()
    df = add_features(df)

    # Only use information available before the target date.
    feature_columns = [
        "product_id",
        "day_of_week",
        "day_of_month",
        "month",
        "is_weekend",
        "sales_lag_1",
        "sales_lag_7",
        "sales_avg_7d",
    ]

    categorical = ["product_id"]
    numeric = [c for c in feature_columns if c not in categorical]

    df = df.dropna(subset=["sales_lag_1", "sales_lag_7"]).copy()
    df = df.sort_values("date").reset_index(drop=True)

    # Chronological split: latest 20% of unique dates is test data.
    unique_dates = np.sort(df["date"].unique())
    split_index = int(len(unique_dates) * 0.80)
    split_index = min(max(split_index, 1), len(unique_dates) - 1)
    cutoff_date = pd.Timestamp(unique_dates[split_index])

    train = df[df["date"] < cutoff_date].copy()
    test = df[df["date"] >= cutoff_date].copy()

    if train.empty or test.empty:
        raise ValueError("Chronological split produced an empty dataset.")

    X_train = train[feature_columns]
    y_train = train["units_sold"].astype(float)
    X_test = test[feature_columns]
    y_test = test["units_sold"].astype(float)

    numeric_pipeline = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric),
            ("categorical", categorical_pipeline, categorical),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=200,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    # Simple baseline: predict the most recent observed sales value.
    baseline_predictions = test["sales_lag_1"].to_numpy()

    metrics = {
        "model": "RandomForestRegressor",
        "target": "units_sold",
        "training_rows": int(len(train)),
        "testing_rows": int(len(test)),
        "training_last_date": str(train["date"].max().date()),
        "testing_first_date": str(test["date"].min().date()),
        "testing_last_date": str(test["date"].max().date()),
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
        "r2": float(r2_score(y_test, predictions)),
        "baseline_mae": float(
            mean_absolute_error(y_test, baseline_predictions)
        ),
        "baseline_rmse": float(
            np.sqrt(mean_squared_error(y_test, baseline_predictions))
        ),
        "note": (
            "Historical sales simulation. Test results are an initial "
            "evaluation, not proof of real-world forecasting performance."
        ),
    }

    model_path = MODEL_DIR / "demand_forecast_model.joblib"
    metrics_path = ARTIFACT_DIR / "demand_forecast_metrics.json"

    joblib.dump(model, model_path)

    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    print("\nDATA SUMMARY")
    print("------------")
    print("Rows after feature preparation:", len(df))
    print("Products:", df["product_id"].nunique())
    print("Training rows:", len(train))
    print("Testing rows:", len(test))
    print("Test period:", metrics["testing_first_date"], "to",
          metrics["testing_last_date"])

    print("\nFORECAST METRICS")
    print("----------------")
    for name, value in metrics.items():
        print(f"{name}: {value}")

    print("\nSAVED FILES")
    print("-----------")
    print("Model:", model_path)
    print("Metrics:", metrics_path)


if __name__ == "__main__":
    main()
