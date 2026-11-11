
from pathlib import Path
import shutil

import pandas as pd

# WasteWise AI project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "perishable_inventory.csv"
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"

BACKUP_PATH = ARTIFACT_DIR / "perishable_inventory_before_demo_extension.csv"
EXTENSION_PATH = ARTIFACT_DIR / "synthetic_sales_extension.csv"

# Use the computer's current local date.
END_DATE = pd.Timestamp.now().normalize()

REQUIRED_COLUMNS = [
    "product_id",
    "date",
    "category",
    "opening_stock",
    "units_received",
    "units_sold",
    "unit_price",
    "discount_pct",
    "days_to_expiry",
    "temperature_c",
    "waste_units",
    "stockout_flag",
]


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Sales dataset not found: {DATA_PATH}")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Dataset is missing columns: {sorted(missing_columns)}"
        )

    df = df[REQUIRED_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise").dt.normalize()
    df = df.sort_values(["product_id", "date"]).reset_index(drop=True)

    latest_date = df["date"].max()

    print("Original latest date:", latest_date.date())
    print("Demo extension end date:", END_DATE.date())

    if latest_date >= END_DATE:
        print("Dataset already reaches the requested date. No changes made.")
        return

    # Keep an untouched backup of the original dataset.
    if not BACKUP_PATH.exists():
        shutil.copy2(DATA_PATH, BACKUP_PATH)
        print("Original dataset backup:", BACKUP_PATH)
    else:
        print("Existing original backup preserved:", BACKUP_PATH)

    numeric_columns = [
        column
        for column in df.select_dtypes(include="number").columns
        if column != "product_id"
    ]

    working = df.copy()
    generated_rows = []

    products = df["product_id"].dropna().unique().tolist()

    for target_date in pd.date_range(
        latest_date + pd.Timedelta(days=1),
        END_DATE,
        freq="D",
    ):
        daily_rows = []

        for product_id in products:
            history = working[
                (working["product_id"] == product_id)
                & (working["date"] < target_date)
            ].sort_values("date")

            if history.empty:
                continue

            # Use recent observations from the same weekday when possible.
            same_weekday = history[
                history["date"].dt.dayofweek == target_date.dayofweek
            ].tail(4)

            template = (
                same_weekday if not same_weekday.empty
                else history.tail(7)
            )

            new_row = {}

            for column in REQUIRED_COLUMNS:
                if column == "date":
                    new_row[column] = target_date

                elif column == "product_id":
                    new_row[column] = product_id

                elif column == "category":
                    categories = template["category"].dropna().mode()
                    new_row[column] = (
                        categories.iloc[0]
                        if not categories.empty
                        else history["category"].iloc[-1]
                    )

                elif column in numeric_columns:
                    values = pd.to_numeric(
                        template[column], errors="coerce"
                    ).dropna()

                    value = float(values.median()) if not values.empty else 0

                    if column in {
                        "opening_stock",
                        "units_received",
                        "units_sold",
                        "days_to_expiry",
                        "waste_units",
                        "stockout_flag",
                    }:
                        new_row[column] = int(round(value))
                    else:
                        new_row[column] = value

                else:
                    values = template[column].dropna()
                    new_row[column] = (
                        values.iloc[-1] if not values.empty else None
                    )

            daily_rows.append(new_row)

        if daily_rows:
            new_day = pd.DataFrame(daily_rows, columns=REQUIRED_COLUMNS)
            working = pd.concat([working, new_day], ignore_index=True)
            generated_rows.extend(daily_rows)

    if not generated_rows:
        print("No extension rows generated. Original dataset unchanged.")
        return

    extension = pd.DataFrame(generated_rows, columns=REQUIRED_COLUMNS)
    extension.to_csv(EXTENSION_PATH, index=False)

    updated = pd.concat([df, extension], ignore_index=True)
    updated = updated.sort_values(
        ["date", "product_id"]
    ).reset_index(drop=True)

    updated.to_csv(DATA_PATH, index=False)

    print("\nDEMO DATA EXTENSION COMPLETE")
    print("----------------------------")
    print("Synthetic rows added:", len(extension))
    print("Updated dataset rows:", len(updated))
    print("Updated latest date:", updated["date"].max().date())
    print("Next forecast date:", (updated["date"].max() + pd.Timedelta(days=1)).date())
    print("Synthetic extension saved separately:", EXTENSION_PATH)
    print("\nIMPORTANT: Added records are simulated, not real sales.")
    print("Original dataset backup:", BACKUP_PATH)


if __name__ == "__main__":
    main()
s