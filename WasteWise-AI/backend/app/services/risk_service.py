
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "models" / "expiry_risk_model.joblib"
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "features"
    / "inventory_batch_features.csv"
)

FEATURE_COLUMNS = [
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


def predict_expiry_risk():
    """Predict experimental expiry risk for inventory batches."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Feature data not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    model = joblib.load(MODEL_PATH)

    df["predicted_expiry_risk"] = model.predict(df[FEATURE_COLUMNS])
    df["high_risk_probability"] = model.predict_proba(
        df[FEATURE_COLUMNS]
    )[:, 1]

    df["predicted_risk_status"] = df["predicted_expiry_risk"].map(
        {0: "Low Risk", 1: "High Risk"}
    )

    df.loc[
        df["days_to_expiry"] <= 0,
        "predicted_risk_status",
    ] = "Expired or Expires Today - Review Before Sale"

    df["prediction_note"] = (
        "Experimental prediction based on simulated training labels; "
        "not a food-safety determination."
    )

    results = df[
        [
            "batch_id",
            "product_id",
            "category",
            "days_to_expiry",
            "quantity_remaining",
            "predicted_risk_status",
            "high_risk_probability",
            "prediction_note",
        ]
    ].copy()

    results["high_risk_probability"] = (
        results["high_risk_probability"].round(4)
    )

    return results.to_dict(orient="records")
