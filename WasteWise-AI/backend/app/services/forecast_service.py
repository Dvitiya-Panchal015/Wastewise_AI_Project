from pathlib import Path

import joblib
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "demand_forecast_model.joblib"
)

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "perishable_inventory.csv"
)


def load_forecast_model():
    """Load the trained demand forecasting model."""

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Demand forecasting model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def load_sales_data() -> pd.DataFrame:
    """Load sales data and clean corrupted date strings."""

    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            f"Processed sales dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    # Validate required columns.
    required = {
        "product_id",
        "date",
        "units_sold",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Sales dataset is missing columns: {sorted(missing)}"
        )

    # Clean corrupted dates.
    # Example: īīī2026-04-01 -> 2026-04-01
    date_strings = (
        df["date"]
        .astype(str)
        .str.strip()
        .str.extract(
            r"(\d{4}-\d{2}-\d{2})",
            expand=False,
        )
    )

    # Parse only the cleaned date strings.
    df["date"] = pd.to_datetime(
        date_strings,
        format="%Y-%m-%d",
        errors="coerce",
    )

    # Convert sales values to numeric.
    df["units_sold"] = pd.to_numeric(
        df["units_sold"],
        errors="coerce",
    )

    # Remove invalid dates and missing required values.
    df = df.dropna(
        subset=[
            "product_id",
            "date",
            "units_sold",
        ]
    ).copy()

    df["product_id"] = (
        df["product_id"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["product_id"] != ""
    ].copy()

    if df.empty:
        raise ValueError(
            "No valid sales records remain after "
            "date cleaning. Please check the CSV file."
        )

    if (df["units_sold"] < 0).any():
        raise ValueError(
            "Negative units_sold values were found."
        )

    df["date"] = df["date"].dt.normalize()

    return df


def forecast_next_day():
    """Forecast next-day sales for each product."""

    df = load_sales_data()

    df = df.sort_values(
        ["product_id", "date"]
    )

    model = load_forecast_model()

    results = []

    for product_id, group in df.groupby("product_id"):
        group = group.sort_values("date")

        sales = (
            group["units_sold"]
            .astype(float)
            .tolist()
        )

        if not sales:
            continue

        last_date = group["date"].iloc[-1]

        forecast_date = (
            last_date + pd.Timedelta(days=1)
        )

        lag_1 = sales[-1]

        lag_7 = (
            sales[-7]
            if len(sales) >= 7
            else float("nan")
        )

        recent_sales = sales[-7:]

        avg_7d = (
            sum(recent_sales) / len(recent_sales)
            if recent_sales
            else 0.0
        )

        # Keep the feature names consistent with model training.
        features = pd.DataFrame(
            [
                {
                    "product_id": product_id,
                    "day_of_week": forecast_date.dayofweek,
                    "day_of_month": forecast_date.day,
                    "month": forecast_date.month,
                    "is_weekend": int(
                        forecast_date.dayofweek >= 5
                    ),
                    "sales_lag_1": lag_1,
                    "sales_lag_7": lag_7,
                    "sales_avg_7d": avg_7d,
                }
            ]
        )

        prediction = float(
            model.predict(features)[0]
        )

        results.append(
            {
                "product_id": product_id,
                "forecast_date": (
                    forecast_date.date().isoformat()
                ),
                "predicted_units_sold": round(
                    max(0.0, prediction),
                    2,
                ),
                "last_day_units_sold": lag_1,
                "average_sales_last_7_days": round(
                    avg_7d,
                    2,
                ),
            }
        )

    if not results:
        raise ValueError(
            "No forecast results were generated. "
            "Check the sales data and trained model."
        )

    return results