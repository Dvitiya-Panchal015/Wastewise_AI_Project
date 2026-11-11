from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Waste Recommendations"])


def find_batches_file() -> Path:
    """Find inventory_batches.csv in the project."""

    current_file = Path(__file__).resolve()

    for parent in current_file.parents:
        candidates = [
            parent / "data" / "raw" / "inventory_batches.csv",
            parent / "data" / "processed" / "inventory_batches.csv",
        ]

        for candidate in candidates:
            if candidate.is_file():
                return candidate

    raise FileNotFoundError(
        "inventory_batches.csv was not found "
        "in data/raw or data/processed."
    )


def load_batches() -> pd.DataFrame:
    """Load and validate inventory batches."""

    df = pd.read_csv(find_batches_file())

    required_columns = [
        "batch_id",
        "product_id",
        "days_to_expiry",
        "quantity_remaining",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    for column in [
        "days_to_expiry",
        "quantity_remaining",
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=[
            "batch_id",
            "product_id",
            "days_to_expiry",
            "quantity_remaining",
        ]
    ).copy()

    if df.empty:
        raise ValueError(
            "No valid inventory batch records were found."
        )

    if (df["quantity_remaining"] < 0).any():
        raise ValueError(
            "Negative remaining quantities were found."
        )

    return df


def create_recommendation(row: dict) -> dict:
    """Generate an illustrative, rule-based recommendation."""

    days = float(row["days_to_expiry"])
    quantity = float(row["quantity_remaining"])

    if days < 0:
        risk_status = "Expired"
        risk_score = 1.0
        priority_score = 100.0

        recommendation = (
            "Batch is past its recorded expiry date. "
            "Do not sell it. Verify food-safety requirements "
            "and follow the applicable disposal procedure."
        )

    elif days <= 2:
        risk_status = "High Risk"
        risk_score = 0.90
        priority_score = 90.0

        recommendation = (
            "Urgently review the expiry date and condition. "
            "Prioritize rotation or sale only if the product "
            "is still safe and legally saleable."
        )

    elif days <= 5:
        risk_status = "High Risk"
        risk_score = 0.75
        priority_score = 75.0

        recommendation = (
            "Review this batch soon. Check demand, stock "
            "rotation, and whether a permitted discount "
            "could reduce waste."
        )

    else:
        risk_status = "Low Risk"
        risk_score = 0.25
        priority_score = 25.0

        recommendation = (
            "Monitor stock levels and expiry dates. "
            "Use regular stock rotation and demand planning."
        )

    result = {
        "batch_id": row["batch_id"],
        "product_id": row["product_id"],
        "category": row.get("category", "Uncategorized"),
        "days_to_expiry": int(days),
        "quantity_remaining": int(quantity),
        "predicted_risk_status": risk_status,
        "high_risk_probability": risk_score,
        "priority_score": priority_score,
        "recommendation": recommendation,
        "prediction_note": (
            "Illustrative rule-based demo score, not a trained "
            "model probability or food-safety determination."
        ),
    }

    return result


@router.get("/")
def get_recommendations():
    """Return inventory batches with recommendations."""

    try:
        df = load_batches()

        recommendations = [
            create_recommendation(row)
            for row in df.to_dict(orient="records")
        ]

        recommendations.sort(
            key=lambda item: (
                item["priority_score"],
                item["quantity_remaining"],
            ),
            reverse=True,
        )

        return {
            "status": "success",
            "total": len(recommendations),
            "recommendations": recommendations,
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {exc}",
        ) from exc