
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

FEATURES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "features"
    / "inventory_batch_features.csv"
)

PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "expiry_risk_predictions.csv"
)


def get_waste_recommendations():
    """Prioritize inventory batches and suggest waste-reduction actions."""

    if not FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Inventory features not found: {FEATURES_PATH}"
        )

    if not PREDICTIONS_PATH.exists():
        raise FileNotFoundError(
            f"Expiry-risk predictions not found: {PREDICTIONS_PATH}"
        )

    inventory = pd.read_csv(FEATURES_PATH)
    risk = pd.read_csv(PREDICTIONS_PATH)

    required_inventory = [
        "batch_id",
        "product_id",
        "category",
        "days_to_expiry",
        "quantity_remaining",
        "avg_daily_sales_7d",
        "estimated_surplus_before_expiry",
    ]

    missing = [
        col for col in required_inventory
        if col not in inventory.columns
    ]
    if missing:
        raise ValueError(
            f"Missing inventory columns: {missing}"
        )

    required_risk = [
        "batch_id",
        "predicted_risk_status",
        "high_risk_probability",
    ]
    missing = [col for col in required_risk if col not in risk.columns]
    if missing:
        raise ValueError(
            f"Missing expiry-risk prediction columns: {missing}"
        )

    # Keep only the prediction fields needed for recommendations.
    risk = risk[required_risk].drop_duplicates(
        subset=["batch_id"]
    )

    df = inventory.merge(
        risk,
        on="batch_id",
        how="left",
        validate="many_to_one",
    )

    df["days_to_expiry"] = pd.to_numeric(
        df["days_to_expiry"], errors="coerce"
    )
    df["quantity_remaining"] = pd.to_numeric(
        df["quantity_remaining"], errors="coerce"
    ).fillna(0)
    df["avg_daily_sales_7d"] = pd.to_numeric(
        df["avg_daily_sales_7d"], errors="coerce"
    ).fillna(0)
    df["estimated_surplus_before_expiry"] = pd.to_numeric(
        df["estimated_surplus_before_expiry"], errors="coerce"
    ).fillna(0)

    def recommend(row):
        days = row["days_to_expiry"]
        quantity = row["quantity_remaining"]
        sales = row["avg_daily_sales_7d"]
        surplus = row["estimated_surplus_before_expiry"]
        status = str(row["predicted_risk_status"])

        if pd.isna(days) or days <= 0:
            return (
                "Urgent review: verify expiry and food-safety requirements; "
                "do not sell expired items."
            )

        if quantity <= 0:
            return "No remaining stock; no action needed."

        if "High Risk" in status or surplus > 0:
            if sales > 0 and days <= 3:
                return (
                    "Prioritize eligible stock for sale; consider an "
                    "approved discount and monitor stock daily."
                )
            if sales > 0:
                return (
                    "Review demand and stock levels; consider an "
                    "approved promotion for eligible items."
                )
            return (
                "Review stock and demand; consider redistribution or "
                "donation only if permitted and food-safe."
            )

        return (
            "Monitor stock and expiry dates; replenish only when "
            "forecast demand justifies it."
        )

    df["recommendation"] = df.apply(recommend, axis=1)

    df["priority_score"] = (
        pd.to_numeric(
            df["high_risk_probability"], errors="coerce"
        ).fillna(0) * 100
    )

    df.loc[
        df["days_to_expiry"] <= 0,
        "priority_score",
    ] = 100

    results = df[
        [
            "batch_id",
            "product_id",
            "category",
            "days_to_expiry",
            "quantity_remaining",
            "predicted_risk_status",
            "high_risk_probability",
            "priority_score",
            "recommendation",
        ]
    ].copy()

    results = results.sort_values(
        by="priority_score",
        ascending=False,
    )

    results["priority_score"] = results["priority_score"].round(2)
    results["high_risk_probability"] = pd.to_numeric(
        results["high_risk_probability"], errors="coerce"
    ).round(4)

    return results.where(pd.notna(results), None).to_dict(
        orient="records"
    )
