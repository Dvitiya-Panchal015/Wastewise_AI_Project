from datetime import date as Date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InventoryRecord(BaseModel):
    """Model for daily inventory records."""

    model_config = ConfigDict(extra="allow")

    product_id: int | str
    date: Date | None = None
    category: str | None = None

    opening_stock: float | None = None
    units_received: float | None = None
    units_sold: float | None = None

    unit_price: float | None = None
    discount_pct: float | None = None

    days_to_expiry: float | None = None
    temperature_c: float | None = None

    waste_units: float | None = None
    stockout_flag: int | None = None

    @field_validator("date", mode="before")
    @classmethod
    def clean_date(cls, value):
        """Remove extra quotation marks from date strings."""

        if value is None or value == "":
            return None

        if isinstance(value, str):
            value = value.strip().strip('"').strip("'")

        return value


class InventoryBatch(BaseModel):
    """Model for inventory batch records."""

    model_config = ConfigDict(extra="allow")

    batch_id: int | str
    product_id: int | str

    category: str | None = None
    days_to_expiry: float | None = None
    quantity_remaining: float | None = None

    predicted_risk_status: str | None = None
    high_risk_probability: float | None = None
    priority_score: float | None = None

    prediction_note: str | None = None


class InventorySummary(BaseModel):
    """Summary of inventory information."""

    model_config = ConfigDict(extra="allow")

    total_records: int = 0
    total_products: int = 0
    total_quantity_remaining: float = 0.0
    total_waste_units: float = 0.0

    total_inventory_value: float | None = None
    estimated_waste_cost: float | None = None


class InventoryResponse(BaseModel):
    """Response containing inventory records."""

    model_config = ConfigDict(extra="allow")

    status: str = "success"
    total: int = 0
    records: list[dict[str, Any]] = Field(
        default_factory=list
    )