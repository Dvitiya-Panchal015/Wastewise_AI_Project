from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(
    tags=["Inventory Batches"]
)


def find_batches_file() -> Path:
    """Find the inventory batches CSV in the project."""

    current_file = Path(__file__).resolve()

    for parent in current_file.parents:
        candidates = [
            parent / "data" / "processed" / "inventory_batches.csv",
            parent / "data" / "raw" / "inventory_batches.csv",
        ]

        for candidate in candidates:
            if candidate.is_file():
                return candidate

    raise FileNotFoundError(
        "inventory_batches.csv was not found "
        "inside data/processed or data/raw."
    )


def load_batches() -> pd.DataFrame:
    """Load inventory batch records from CSV."""

    file_path = find_batches_file()

    df = pd.read_csv(file_path)

    if df.empty:
        return df

    if "batch_id" not in df.columns:
        raise ValueError(
            "The inventory batches CSV must contain "
            "a batch_id column."
        )

    return df


def dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame rows into JSON-compatible records."""

    clean_df = df.astype(object).where(
        pd.notna(df),
        None,
    )

    return clean_df.to_dict(orient="records")


@router.get("/")
def get_batches():
    """Return all inventory batches."""

    try:
        df = load_batches()

        return {
            "total": len(df),
            "batches": dataframe_to_records(df),
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load inventory batches: {exc}",
        ) from exc


@router.get("/{batch_id}")
def get_batch(batch_id: str):
    """Return one inventory batch by its ID."""

    try:
        df = load_batches()

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="No inventory batches found.",
            )

        matching_rows = df[
            df["batch_id"].astype(str) == str(batch_id)
        ]

        if matching_rows.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Batch {batch_id} was not found.",
            )

        return dataframe_to_records(
            matching_rows
        )[0]

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve batch: {exc}",
        ) from exc