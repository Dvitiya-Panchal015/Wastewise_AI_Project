from pathlib import Path
from typing import Any

import pandas as pd


class InventoryService:
    """Service for loading and summarizing inventory batches."""

    def __init__(self) -> None:
        self.inventory_file = self._find_data_file(
            "inventory_batches.csv"
        )
        self.products_file = self._find_data_file(
            "products.csv"
        )

    @staticmethod
    def _find_data_file(filename: str) -> Path:
        """Find a CSV file in the project data folders."""

        current_file = Path(__file__).resolve()

        for parent in current_file.parents:
            candidates = [
                parent / "data" / "raw" / filename,
                parent / "data" / "processed" / filename,
            ]

            for candidate in candidates:
                if candidate.is_file():
                    return candidate

        raise FileNotFoundError(
            f"Could not find {filename} in the project's "
            "data/raw or data/processed folders."
        )

    @staticmethod
    def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
        """Convert DataFrame records into JSON-friendly values."""

        clean_df = df.astype(object).where(
            pd.notna(df),
            None,
        )

        return clean_df.to_dict(orient="records")

    def load_inventory(self) -> pd.DataFrame:
        """Load and validate inventory batch records."""

        df = pd.read_csv(self.inventory_file)

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
                f"Inventory file is missing columns: {missing}"
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

        if (df["quantity_remaining"] < 0).any():
            raise ValueError(
                "Negative quantity_remaining values found."
            )

        return df

    def load_products(self) -> pd.DataFrame:
        """Load product information and unit costs."""

        df = pd.read_csv(self.products_file)

        required_columns = [
            "product_id",
            "unit_cost",
        ]

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Products file is missing columns: {missing}"
            )

        df["unit_cost"] = pd.to_numeric(
            df["unit_cost"],
            errors="coerce",
        )

        return df

    def get_all_batches(self) -> dict[str, Any]:
        """Return all inventory batches."""

        df = self.load_inventory()

        return {
            "status": "success",
            "total": len(df),
            "batches": self._records(df),
        }

    def get_batch_by_id(
        self,
        batch_id: str | int,
    ) -> dict[str, Any] | None:
        """Return a batch using its batch ID."""

        df = self.load_inventory()

        matches = df[
            df["batch_id"].astype(str).str.strip()
            == str(batch_id).strip()
        ]

        if matches.empty:
            return None

        return self._records(matches)[0]

    def get_inventory_summary(self) -> dict[str, Any]:
        """Calculate inventory quantity and cost value."""

        inventory = self.load_inventory()
        products = self.load_products()

        # Normalize IDs so 1001 and 1001.0 can match.
        inventory["product_key"] = (
            inventory["product_id"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )

        products["product_key"] = (
            products["product_id"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )

        costs = (
            products
            .drop_duplicates("product_key")
            .set_index("product_key")["unit_cost"]
        )

        inventory["unit_cost"] = (
            inventory["product_key"].map(costs)
        )

        # Do not silently count unknown product costs as zero.
        missing_costs = inventory[
            inventory["unit_cost"].isna()
        ]

        inventory_value = None

        if missing_costs.empty:
            inventory_value = float(
                (
                    inventory["quantity_remaining"]
                    * inventory["unit_cost"]
                ).sum()
            )

        total_quantity = float(
            inventory["quantity_remaining"].sum()
        )

        category_summary = {}

        if "category" in inventory.columns:
            category_summary = (
                inventory.groupby("category")[
                    "quantity_remaining"
                ]
                .sum()
                .to_dict()
            )

        return {
            "status": "success",
            "total_batches": int(len(inventory)),
            "total_products": int(
                inventory["product_id"].nunique()
            ),
            "total_quantity_remaining": total_quantity,
            "total_inventory_value": (
                round(inventory_value, 2)
                if inventory_value is not None
                else None
            ),
            "missing_unit_cost_batches": int(
                len(missing_costs)
            ),
            "quantity_by_category": category_summary,
            "notice": (
                "Inventory value uses unit cost and remaining "
                "quantity. This is a demo-data estimate."
            ),
        }


# Shared service instance for use by API routes.
inventory_service = InventoryService()