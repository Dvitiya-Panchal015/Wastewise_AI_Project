from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Dashboard"])


# Find project CSV files without hardcoding the
# absolute Windows path.
def find_data_file(filename: str) -> Path:
    current_file = Path(__file__).resolve()

    for parent in current_file.parents:
        for folder in ("processed", "raw"):
            candidate = (
                parent / "data" / folder / filename
            )

            if candidate.is_file():
                return candidate

    raise FileNotFoundError(
        f"Could not find {filename} in data/processed "
        "or data/raw."
    )


def normalize_id(value) -> str:
    """Normalize product IDs for matching CSV files."""
    try:
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value).strip()


def load_csv(filename: str) -> pd.DataFrame:
    """Load a CSV file from the project data folders."""
    path = find_data_file(filename)
    return pd.read_csv(path)


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dates that contain whitespace or extra quotes."""
    result = df.copy()

    if "date" in result.columns:
        result["date"] = (
            result["date"]
            .astype(str)
            .str.strip()
            .str.strip('"')
            .str.strip("'")
        )

        result["date"] = pd.to_datetime(
            result["date"],
            format="mixed",
            errors="coerce",
        )

    return result


def number(value) -> float:
    """Convert a value to a number safely."""
    result = pd.to_numeric(value, errors="coerce")

    if pd.isna(result):
        return 0.0

    return float(result)


def calculate_summary() -> dict:
    """Calculate dashboard metrics from project CSV files."""

    inventory = clean_dates(
        load_csv("perishable_inventory.csv")
    )

    products = load_csv("products.csv")

    required_inventory_columns = {
        "product_id",
        "date",
        "opening_stock",
        "units_received",
        "units_sold",
        "waste_units",
    }

    missing = (
        required_inventory_columns - set(inventory.columns)
    )

    if missing:
        raise ValueError(
            f"Inventory CSV is missing columns: {sorted(missing)}"
        )

    required_product_columns = {
        "product_id",
        "unit_cost",
    }

    missing = required_product_columns - set(products.columns)

    if missing:
        raise ValueError(
            f"Products CSV is missing columns: {sorted(missing)}"
        )

    # Build a lookup of product ID -> unit cost.
    products = products.copy()

    products["product_key"] = (
        products["product_id"].map(normalize_id)
    )

    products["unit_cost"] = pd.to_numeric(
        products["unit_cost"],
        errors="coerce",
    )

    cost_lookup = (
        products.dropna(subset=["unit_cost"])
        .drop_duplicates("product_key")
        .set_index("product_key")["unit_cost"]
        .to_dict()
    )

    inventory["product_key"] = (
        inventory["product_id"].map(normalize_id)
    )

    # Calculate recorded waste cost across the historical dataset.
    inventory["waste_units"] = pd.to_numeric(
        inventory["waste_units"],
        errors="coerce",
    )

    inventory["unit_cost"] = (
        inventory["product_key"].map(cost_lookup)
    )

    missing_cost_rows = inventory[
        inventory["unit_cost"].isna()
        & inventory["waste_units"].fillna(0).gt(0)
    ]

    if not missing_cost_rows.empty:
        raise ValueError(
            "Unit cost is missing for products with recorded waste."
        )

    estimated_waste_cost = (
        inventory["waste_units"].fillna(0)
        * inventory["unit_cost"].fillna(0)
    ).sum()

    # Calculate current inventory value from inventory batches
    # when the batch CSV contains remaining quantities.
    inventory_value = None
    inventory_source = None

    try:
        batches = load_csv("inventory_batches.csv")

        if {
            "product_id",
            "quantity_remaining",
        }.issubset(batches.columns):
            batches = batches.copy()

            batches["product_key"] = (
                batches["product_id"].map(normalize_id)
            )

            batches["quantity_remaining"] = pd.to_numeric(
                batches["quantity_remaining"],
                errors="coerce",
            )

            batches["unit_cost"] = (
                batches["product_key"].map(cost_lookup)
            )

            valid_batches = batches.dropna(
                subset=["quantity_remaining", "unit_cost"]
            )

            if len(valid_batches) == 0 and len(batches) > 0:
                raise ValueError(
                    "No valid batch quantities and unit costs "
                    "were available."
                )

            inventory_value = (
                valid_batches["quantity_remaining"]
                * valid_batches["unit_cost"]
            ).sum()

            inventory_source = "inventory_batches.csv"

    except FileNotFoundError:
        # Fall back to an estimate from the latest daily records.
        inventory_value = None

    # Fallback when batch-level remaining quantity is unavailable.
    if inventory_value is None:
        valid_inventory = inventory.dropna(subset=["date"])

        if valid_inventory.empty:
            raise ValueError(
                "No valid inventory dates were found."
            )

        latest_date = valid_inventory["date"].max()

        latest = valid_inventory[
            valid_inventory["date"] == latest_date
        ].copy()

        for column in (
            "opening_stock",
            "units_received",
            "units_sold",
            "waste_units",
        ):
            latest[column] = pd.to_numeric(
                latest[column],
                errors="coerce",
            )

        latest["remaining_estimate"] = (
            latest["opening_stock"].fillna(0)
            + latest["units_received"].fillna(0)
            - latest["units_sold"].fillna(0)
            - latest["waste_units"].fillna(0)
        ).clip(lower=0)

        latest["unit_cost"] = (
            latest["product_key"].map(cost_lookup)
        )

        if latest["unit_cost"].isna().any():
            raise ValueError(
                "Unit cost is missing for latest inventory records."
            )

        inventory_value = (
            latest["remaining_estimate"]
            * latest["unit_cost"]
        ).sum()

        inventory_source = (
            "estimated from latest daily inventory records"
        )

    latest_valid_date = inventory["date"].max()

    # Prepare category counts.
    if "category" in inventory.columns:
        category_summary = (
            inventory.groupby("category")["product_id"]
            .count()
            .to_dict()
        )
    else:
        category_summary = {}

    return {
        "status": "success",
        "inventory_value": round(float(inventory_value), 2),
        "estimated_waste_cost": round(
            float(estimated_waste_cost), 2
        ),
        "product_count": int(
            products["product_id"].nunique()
        ),
        "historical_record_count": int(len(inventory)),
        "latest_data_date": (
            latest_valid_date.strftime("%Y-%m-%d")
            if pd.notna(latest_valid_date)
            else None
        ),
        "inventory_value_source": inventory_source,
        "category_record_counts": category_summary,
        "notice": (
            "These are estimates from project demo data. "
            "Historical waste cost is cumulative, not today's waste."
        ),
    }


@router.get("/summary")
def get_dashboard_summary():
    """Return summary metrics for the dashboard."""
    try:
        return calculate_summary()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard summary failed: {exc}",
        ) from exc