from pathlib import Path

import pandas as pd


class ForecastService:
    """Service for generating sales demand forecasts."""

    def __init__(self):
        self.inventory_file = self._find_inventory_file()

    @staticmethod
    def _find_inventory_file() -> Path:
        """Locate the processed inventory CSV."""

        current_file = Path(__file__).resolve()

        for parent in current_file.parents:
            candidate = (
                parent
                / "data"
                / "processed"
                / "perishable_inventory.csv"
            )

            if candidate.is_file():
                return candidate

        raise FileNotFoundError(
            "Could not find "
            "data/processed/perishable_inventory.csv"
        )

    def load_inventory(self) -> pd.DataFrame:
        """Load inventory and clean corrupted date strings."""

        df = pd.read_csv(self.inventory_file)

        required_columns = [
            "product_id",
            "date",
            "units_sold",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        # Extract the valid date even if unwanted characters
        # appear before or after it.
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

        df["date"] = pd.to_datetime(
            date_strings,
            format="%Y-%m-%d",
            errors="coerce",
        )

        # Normalize timestamps to calendar dates.
        df["date"] = df["date"].dt.normalize()

        # Clean product IDs and sales values.
        df["product_id"] = (
            df["product_id"]
            .astype(str)
            .str.strip()
        )

        df["units_sold"] = pd.to_numeric(
            df["units_sold"],
            errors="coerce",
        )

        # Remove invalid dates, IDs, and sales values.
        df = df.dropna(
            subset=[
                "date",
                "product_id",
                "units_sold",
            ]
        ).copy()

        df = df[
            df["product_id"] != ""
        ].copy()

        if df.empty:
            raise ValueError(
                "No valid inventory records remain after "
                "date cleaning. Check the CSV date column."
            )

        if (df["units_sold"] < 0).any():
            raise ValueError(
                "Negative units_sold values were found."
            )

        return df

    def generate_forecast(self) -> dict:
        """
        Generate next-day forecasts using a seven-day
        moving-average baseline.

        This method does not use the trained ML model.
        """

        df = self.load_inventory()

        latest_date = df["date"].max().normalize()

        # Include the latest date and six preceding days.
        window_start = (
            latest_date - pd.Timedelta(days=6)
        )

        recent_data = df[
            (df["date"] >= window_start)
            & (df["date"] <= latest_date)
        ].copy()

        if recent_data.empty:
            raise ValueError(
                "No sales records found in the latest "
                "seven calendar days."
            )

        # Average daily sales for each product.
        average_sales = (
            recent_data
            .groupby("product_id")["units_sold"]
            .mean()
            .rename("predicted_units_sold")
        )

        # Most recent recorded sales for each product.
        latest_sales = (
            df[df["date"] == latest_date]
            .drop_duplicates(
                subset=["product_id"],
                keep="last",
            )
            .set_index("product_id")["units_sold"]
            .rename("last_day_units_sold")
        )

        # Keep products available in both results.
        results = pd.concat(
            [
                latest_sales,
                average_sales,
            ],
            axis=1,
            join="inner",
        ).dropna()

        if results.empty:
            raise ValueError(
                "No matching products were found for "
                "the forecast calculation."
            )

        forecast_date = (
            latest_date + pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d")

        forecasts = []

        for product_id, row in results.iterrows():
            forecasts.append(
                {
                    "product_id": str(product_id),
                    "forecast_date": forecast_date,
                    "last_day_units_sold": round(
                        float(row["last_day_units_sold"]),
                        2,
                    ),
                    "predicted_units_sold": round(
                        max(
                            0.0,
                            float(
                                row["predicted_units_sold"]
                            ),
                        ),
                        2,
                    ),
                }
            )

        return {
            "forecast_date": forecast_date,
            "forecast_method": (
                "7-day moving average baseline"
            ),
            "forecast_type": "demo_baseline",
            "forecasts": forecasts,
            "record_count": len(forecasts),
            "notice": (
                "Experimental demo forecast. This forecast "
                "uses historical CSV records and is not the "
                "trained ML model. Validate using real sales "
                "data before operational use."
            ),
        }

    # Compatibility aliases for routes that call these names.
    def get_forecast(self) -> dict:
        return self.generate_forecast()

    def forecast(self) -> dict:
        return self.generate_forecast()

    def forecast_sales(self) -> dict:
        return self.generate_forecast()

    def get_sales_forecast(self) -> dict:
        return self.generate_forecast()


# Shared service instance.
forecast_service = ForecastService()