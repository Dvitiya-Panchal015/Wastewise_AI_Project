
from pathlib import Path
import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Expected project datasets
DATASETS = {
    "perishable_inventory": "perishable_inventory - perishable_inventory.csv",
    "inventory_batches": "inventory_batches - inventory_batches.csv",
    "products": "products - products.csv",
    "discount_scenarios": (
        "discount_scenarios_simulated - discount_scenarios_simulated.csv"
    ),
}


def validate_dataset(dataset_name, filename):
    """Inspect a CSV file and report basic data-quality checks."""
    file_path = RAW_DATA_DIR / filename

    print("\n" + "=" * 70)
    print(f"DATASET: {dataset_name}")
    print(f"FILE: {filename}")

    if not file_path.exists():
        print("STATUS: FAILED - File not found")
        return

    try:
        df = pd.read_csv(file_path)
    except Exception as error:
        print(f"STATUS: FAILED - Could not read CSV: {error}")
        return

    print("STATUS: READ SUCCESSFULLY")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"Column names: {df.columns.tolist()}")

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    print(f"Duplicate rows: {df.duplicated().sum()}")

    if missing.empty:
        print("Missing values: None")
    else:
        print("Missing values by column:")
        print(missing.to_string())

    print("\nData types:")
    print(df.dtypes.to_string())


def main():
    print("WASTEWISE AI - DATA VALIDATION")
    print(f"Raw data directory: {RAW_DATA_DIR}")

    if not RAW_DATA_DIR.exists():
        print("ERROR: The data/raw directory does not exist.")
        return

    for dataset_name, filename in DATASETS.items():
        validate_dataset(dataset_name, filename)

    print("\n" + "=" * 70)
    print("Initial data validation completed.")


if __name__ == "__main__":
    main()
