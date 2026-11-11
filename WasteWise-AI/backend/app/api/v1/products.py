from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Products"])


def find_products_file() -> Path:
    """Find products.csv inside the project data folders."""

    current_file = Path(__file__).resolve()

    for parent in current_file.parents:
        candidates = [
            parent / "data" / "processed" / "products.csv",
            parent / "data" / "raw" / "products.csv",
        ]

        for candidate in candidates:
            if candidate.is_file():
                return candidate

    raise FileNotFoundError(
        "products.csv was not found in data/processed "
        "or data/raw."
    )


def load_products() -> pd.DataFrame:
    """Load and validate product records."""

    file_path = find_products_file()
    df = pd.read_csv(file_path)

    required_columns = [
        "product_id",
        "product_name",
        "category",
        "shelf_life_days",
        "selling_price",
        "unit_cost",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing product columns: {missing_columns}"
        )

    if df["product_id"].duplicated().any():
        raise ValueError(
            "Duplicate product IDs found in products.csv."
        )

    for column in [
        "shelf_life_days",
        "selling_price",
        "unit_cost",
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    if df[
        ["shelf_life_days", "selling_price", "unit_cost"]
    ].isna().any().any():
        raise ValueError(
            "Invalid numeric values found in product data."
        )

    if (
        df[["shelf_life_days", "selling_price", "unit_cost"]]
        < 0
    ).any().any():
        raise ValueError(
            "Negative product values are not allowed."
        )

    return df


def records_from_dataframe(
    df: pd.DataFrame,
) -> list[dict]:
    """Convert DataFrame rows into JSON-compatible records."""

    clean_df = df.astype(object).where(
        pd.notna(df),
        None,
    )

    return clean_df.to_dict(orient="records")


@router.get("/")
def get_products():
    """Return all products."""

    try:
        df = load_products()

        return {
            "status": "success",
            "total": len(df),
            "products": records_from_dataframe(df),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load products: {exc}",
        ) from exc


@router.get("/{product_id}")
def get_product(product_id: str):
    """Return a single product by its product ID."""

    try:
        df = load_products()

        product_ids = df["product_id"].astype(str).str.strip()

        # Also match integer IDs represented as strings,
        # such as "1001" and "1001.0".
        matches = df[
            (product_ids == product_id.strip())
            | (
                product_ids
                == product_id.strip() + ".0"
            )
        ]

        if matches.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} was not found.",
            )

        return records_from_dataframe(matches)[0]

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve product: {exc}",
        ) from exc