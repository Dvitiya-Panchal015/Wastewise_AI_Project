
from pathlib import Path
import pandas as pd

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# One copy of each unique dataset
DATASETS = {
    "products": {
        "file": "products - products.csv",
        "required": [
            "product_id", "product_name", "category",
            "shelf_life_days", "selling_price", "unit_cost"
        ],
    },
    "perishable_inventory": {
        "file": "perishable_inventory - perishable_inventory.csv",
        "required": [
            "product_id", "date", "category", "opening_stock",
            "units_received", "units_sold", "unit_price",
            "discount_pct", "days_to_expiry", "temperature_c",
            "waste_units", "stockout_flag"
        ],
    },
    "inventory_batches": {
        "file": "inventory_batches - inventory_batches.csv",
        "required": [
            "batch_id", "product_id", "category", "received_at",
            "snapshot_date", "expiry_date", "initial_quantity",
            "quantity_remaining", "days_to_expiry",
            "avg_daily_sales_7d", "expected_demand_before_expiry",
            "unit_price", "unit_cost", "discount_pct",
            "expiry_risk_label", "waste_units_actual_simulated"
        ],
    },
    "discount_scenarios": {
        "file": "discount_scenarios_simulated - discount_scenarios_simulated.csv",
        "required": [
            "batch_id", "product_id", "days_to_expiry",
            "quantity_remaining", "discount_pct",
            "estimated_units_sold_simulated",
            "estimated_revenue_simulated",
            "estimated_gross_margin_simulated"
        ],
    },
}


def main():
    products = None
    product_ids = set()
    reports = []

    for dataset_name, config in DATASETS.items():
        input_path = RAW_DIR / config["file"]

        print("\n" + "=" * 65)
        print(f"Dataset: {dataset_name}")
        print(f"Input: {input_path.name}")

        if not input_path.exists():
            print("ERROR: Input file not found. Skipping.")
            reports.append({
                "dataset": dataset_name,
                "status": "FILE NOT FOUND",
            })
            continue

        try:
            df = pd.read_csv(input_path)
        except Exception as exc:
            print(f"ERROR reading file: {exc}")
            reports.append({
                "dataset": dataset_name,
                "status": "READ ERROR",
            })
            continue

        # Required-column validation
        missing_columns = [
            col for col in config["required"]
            if col not in df.columns
        ]

        if missing_columns:
            print("ERROR: Missing required columns:", missing_columns)
            reports.append({
                "dataset": dataset_name,
                "status": "MISSING COLUMNS",
            })
            continue

        print("Original shape:", df.shape)
        print("Missing values:", int(df.isna().sum().sum()))
        print("Duplicate rows:", int(df.duplicated().sum()))

        # Validate product master before checking other datasets
        if dataset_name == "products":
            print(
                "Duplicate product IDs:",
                int(df["product_id"].duplicated().sum())
            )

            if df["product_id"].duplicated().any():
                print(
                    "ERROR: Product IDs are not unique. "
                    "Review the source before continuing."
                )
                reports.append({
                    "dataset": dataset_name,
                    "status": "DUPLICATE PRODUCT IDs",
                })
                continue

            products = df.copy()
            product_ids = set(products["product_id"].dropna())

        # Check product IDs in related datasets
        if dataset_name in {
            "perishable_inventory",
            "inventory_batches",
            "discount_scenarios",
        }:
            if products is None:
                print(
                    "WARNING: Product master has not been validated yet."
                )
            else:
                unmatched = set(df["product_id"].dropna()) - product_ids
                print("Unmatched product IDs:", len(unmatched))

        # Check discount bounds without silently altering data
        if "discount_pct" in df.columns:
            invalid_discount = (
                (df["discount_pct"] < 0) |
                (df["discount_pct"] > 100)
            )
            print(
                "Discounts outside 0-100:",
                int(invalid_discount.sum())
            )

        # Parse dates only for consistency checks; preserve source strings
        if dataset_name == "inventory_batches":
            snapshot = pd.to_datetime(
                df["snapshot_date"], errors="coerce"
            )
            expiry = pd.to_datetime(
                df["expiry_date"], errors="coerce"
            )
            received = pd.to_datetime(
                df["received_at"], errors="coerce"
            )

            print("Invalid snapshot dates:", int(snapshot.isna().sum()))
            print("Invalid expiry dates:", int(expiry.isna().sum()))
            print("Invalid receipt dates:", int(received.isna().sum()))

            expired = expiry < snapshot
            print("Expired batches:", int(expired.sum()))
            print(
                "Expired batches with stock remaining:",
                int(
                    (
                        expired &
                        (df["quantity_remaining"] > 0)
                    ).sum()
                )
            )

            # Check consistency of days_to_expiry
            calculated_days = (expiry - snapshot).dt.days
            comparable = (
                calculated_days.notna() &
                df["days_to_expiry"].notna()
            )
            mismatches = (
                calculated_days[comparable].to_numpy()
                != df.loc[comparable, "days_to_expiry"].to_numpy()
            )
            print(
                "Days-to-expiry mismatches:",
                int(mismatches.sum())
            )

            # Warn if label perfectly matches simulated waste
            if "waste_units_actual_simulated" in df.columns:
                same = (
                    (df["expiry_risk_label"] == 1)
                    == (df["waste_units_actual_simulated"] > 0)
                )
                print(
                    "Label matches simulated-waste condition for all rows:",
                    bool(same.all())
                )

        # Do not remove rows, overwrite labels, or replace negative
        # days-to-expiry values automatically.
        output_path = PROCESSED_DIR / f"{dataset_name}.csv"
        df.to_csv(output_path, index=False)
        print("Saved:", output_path.relative_to(PROJECT_ROOT))

        reports.append({
            "dataset": dataset_name,
            "rows": len(df),
            "columns": len(df.columns),
            "missing_values": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "status": "SAVED - REVIEW WARNINGS",
        })

    print("\n" + "=" * 65)
    print("PREPROCESSING SUMMARY")
    print(pd.DataFrame(reports).to_string(index=False))
    print("\nOriginal raw CSV files were not modified.")
    print("Review warnings before using the processed data for ML.")


if __name__ == "__main__":
    main()
