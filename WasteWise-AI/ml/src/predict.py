
from pathlib import Path

import joblib
import pandas as pd


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
FEATURE_DIR = DATA_DIR / "features"
MODEL_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "artifacts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load saved models
# --------------------------------------------------
def load_model(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Model not found: {path}\n"
            "Train the relevant model before running predictions."
        )
    return joblib.load(path)


# --------------------------------------------------
# 3. Predict expiry risk
# --------------------------------------------------
def predict_expiry_risk():
    model_path = MODEL_DIR / "expiry_risk_model.joblib"
    data_path = FEATURE_DIR / "inventory_batch_features.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Feature dataset not found: {data_path}")

    model = load_model(model_path)
    df = pd.read_csv(data_path)

    feature_columns = [
        "category",
        "initial_quantity",
        "quantity_remaining",
        "days_to_expiry",
        "avg_daily_sales_7d",
        "expected_demand_before_expiry",
        "unit_price",
        "unit_cost",
        "discount_pct",
    ]

    missing = [c for c in feature_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expiry-risk features: {missing}")

    # Do not recommend selling expired products.
    df["predicted_expiry_risk"] = model.predict(df[feature_columns])
    df["high_risk_probability"] = model.predict_proba(
        df[feature_columns]
    )[:, 1]

    df["predicted_risk_status"] = df["predicted_expiry_risk"].map(
        {0: "Low Risk", 1: "High Risk"}
    )

    # These are simulated-label predictions, not validated food-safety decisions.
    df["prediction_note"] = (
        "Experimental prediction from a model trained on simulated labels"
    )

    expired = df["days_to_expiry"] < 0
    df.loc[expired, "predicted_risk_status"] = (
        "Expired - Do Not Recommend Sale"
    )

    output_path = OUTPUT_DIR / "expiry_risk_predictions.csv"
    df.to_csv(output_path, index=False)

    print("\nEXPIRY RISK PREDICTIONS")
    print("----------------------")
    print("Records:", len(df))
    print("Predicted labels:")
    print(df["predicted_risk_status"].value_counts().to_string())
    print("Saved to:", output_path)


# --------------------------------------------------
# 4. Predict next-day demand
# --------------------------------------------------
def predict_next_day_demand():
    model_path = MODEL_DIR / "demand_forecast_model.joblib"
    data_path = DATA_DIR / "perishable_inventory.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Sales dataset not found: {data_path}")

    model = load_model(model_path)
    df = pd.read_csv(data_path)

    required = ["product_id", "date", "units_sold"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing demand columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df = df.sort_values(["product_id", "date"]).copy()

    # Create features for the day after each product's latest observation.
    latest = df.groupby("product_id", as_index=False).tail(1).copy()
    latest["forecast_date"] = latest["date"] + pd.Timedelta(days=1)

    latest["day_of_week"] = latest["forecast_date"].dt.dayofweek
    latest["day_of_month"] = latest["forecast_date"].dt.day
    latest["month"] = latest["forecast_date"].dt.month
    latest["is_weekend"] = (
        latest["day_of_week"] >= 5
    ).astype(int)

    grouped = df.groupby("product_id")["units_sold"]
    latest_sales = grouped.last()
    lag7_sales = grouped.apply(
        lambda s: s.iloc[-7] if len(s) >= 7 else float("nan")
    )

    latest["sales_lag_1"] = latest["product_id"].map(latest_sales)
    latest["sales_lag_7"] = latest["product_id"].map(lag7_sales)

    rolling_avg = grouped.apply(
        lambda s: s.tail(7).mean() if len(s) >= 7 else s.mean()
    )
    latest["sales_avg_7d"] = latest["product_id"].map(rolling_avg)

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

    latest["predicted_units_sold"] = model.predict(
        latest[feature_columns]
    ).clip(min=0)

    output = latest[
        [
            "product_id",
            "forecast_date",
            "sales_lag_1",
            "sales_lag_7",
            "sales_avg_7d",
            "predicted_units_sold",
        ]
    ].copy()

    output["predicted_units_sold"] = (
        output["predicted_units_sold"].round(2)
    )

    output_path = OUTPUT_DIR / "next_day_demand_predictions.csv"
    output.to_csv(output_path, index=False)

    print("\nNEXT-DAY DEMAND FORECAST")
    print("------------------------")
    print(output.to_string(index=False))
    print("Saved to:", output_path)


# --------------------------------------------------
# 5. Run both prediction tasks
# --------------------------------------------------
def main():
    predict_expiry_risk()
    predict_next_day_demand()


if __name__ == "__main__":
    main()
