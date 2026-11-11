
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FEATURE_DIR = PROCESSED_DIR / "features"

FEATURE_DIR.mkdir(parents=True, exist_ok=True)


def add_expiry_features(df):
    """Add expiry-status features without changing the original expiry values."""
    df = df.copy()

    df["expiry_status"] = "Unknown"
    df.loc[df["days_to_expiry"] < 0, "expiry_status"] = "Expired"
    df.loc[df["days_to_expiry"] == 0, "expiry_status"] = "Expires Today"
    df.loc[
        df["days_to_expiry"].between(1, 3),
        "expiry_status",
    ] = "Critical: 1-3 Days"
    df.loc[
        df["days_to_expiry"].between(4, 7),
        "expiry_status",
    ] = "High: 4-7 Days"
    df.loc[
        df["days_to_expiry"].between(8, 14),
        "expiry_status",
    ] = "Medium: 8-14 Days"
    df.loc[df["days_to_expiry"] > 14, "expiry_status"] = "Low: Over 14 Days"

    # Safety flag: expired stock is not eligible for sale or discount recommendations.
    df["sale_eligible"] = df["days_to_expiry"] > 0

    return df


def engineer_inventory_batch_features(df):
    """Create features for inventory analysis and future model preparation."""
    df = df.copy()

    df = add_expiry_features(df)

    df["remaining_stock_ratio"] = 0.0
    valid_initial = df["initial_quantity"] > 0

    df.loc[valid_initial, "remaining_stock_ratio"] = (
        df.loc[valid_initial, "quantity_remaining"]
        / df.loc[valid_initial, "initial_quantity"]
    )

    df["expected_demand_coverage_days"] = 0.0
    valid_demand = df["avg_daily_sales_7d"] > 0

    df.loc[valid_demand, "expected_demand_coverage_days"] = (
        df.loc[valid_demand, "quantity_remaining"]
        / df.loc[valid_demand, "avg_daily_sales_7d"]
    )

    df["estimated_surplus_before_expiry"] = (
        df["quantity_remaining"]
        - df["expected_demand_before_expiry"]
    ).clip(lower=0)

    # Do not use expiry labels or simulated waste as input features.
    # Those columns are outcomes/targets or may leak target information.
    return df


def engineer_daily_inventory_features(df):
    """Create useful derived features from daily inventory records."""
    df = df.copy()

    df = add_expiry_features(df)

    df["total_available_stock"] = (
        df["opening_stock"] + df["units_received"]
    )

    df["sales_to_available_stock_ratio"] = 0.0
    valid_stock = df["total_available_stock"] > 0

    df.loc[valid_stock, "sales_to_available_stock_ratio"] = (
        df.loc[valid_stock, "units_sold"]
        / df.loc[valid_stock, "total_available_stock"]
    )

    df["estimated_closing_stock"] = (
        df["total_available_stock"] - df["units_sold"] - df["waste_units"]
    ).clip(lower=0)

    df["potential_waste_value"] = (
        df["waste_units"] * df["unit_price"]
    )

    return df


def main():
    batch_path = PROCESSED_DIR / "inventory_batches.csv"
    daily_path = PROCESSED_DIR / "perishable_inventory.csv"
    products_path = PROCESSED_DIR / "products.csv"
    discounts_path = PROCESSED_DIR / "discount_scenarios.csv"

    required_files = [
        batch_path,
        daily_path,
        products_path,
        discounts_path,
    ]

    missing_files = [path.name for path in required_files if not path.exists()]

    if missing_files:
        raise FileNotFoundError(
            f"Missing processed datasets: {missing_files}. "
            "Run preprocessing.py first."
        )

    batches = pd.read_csv(batch_path)
    daily = pd.read_csv(daily_path)
    products = pd.read_csv(products_path)
    discounts = pd.read_csv(discounts_path)

    # Validate the minimum columns needed for these transformations.
    batch_columns = [
        "days_to_expiry",
        "initial_quantity",
        "quantity_remaining",
        "avg_daily_sales_7d",
        "expected_demand_before_expiry",
    ]
    daily_columns = [
        "days_to_expiry",
        "opening_stock",
        "units_received",
        "units_sold",
        "waste_units",
        "unit_price",
    ]

    for column in batch_columns:
        if column not in batches.columns:
            raise ValueError(f"Missing inventory batch column: {column}")

    for column in daily_columns:
        if column not in daily.columns:
            raise ValueError(f"Missing daily inventory column: {column}")

    # Create feature datasets in a separate folder.
    batch_features = engineer_inventory_batch_features(batches)
    daily_features = engineer_daily_inventory_features(daily)
    discount_features = add_expiry_features(discounts)

    batch_output = FEATURE_DIR / "inventory_batch_features.csv"
    daily_output = FEATURE_DIR / "daily_inventory_features.csv"
    discount_output = FEATURE_DIR / "discount_scenario_features.csv"

    batch_features.to_csv(batch_output, index=False)
    daily_features.to_csv(daily_output, index=False)
    discount_features.to_csv(discount_output, index=False)

    print("\nFEATURE ENGINEERING COMPLETED")
    print("-" * 55)
    print(f"Inventory batch features: {batch_features.shape}")
    print(f"Daily inventory features: {daily_features.shape}")
    print(f"Discount scenario features: {discount_features.shape}")
    print(f"\nOutput folder: {FEATURE_DIR}")
    print("\nExpiry safety check:")
    print(
        "Expired discount scenarios marked ineligible:",
        int((discount_features["days_to_expiry"] < 0).sum()),
    )
    print(
        "Scenarios eligible for sale:",
        int(discount_features["sale_eligible"].sum()),
    )
    print("\nOriginal raw and processed CSV files were not overwritten.")
    print("Note: These features require validation before model training.")


if __name__ == "__main__":
    main()
