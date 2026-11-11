from datetime import date as Date

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class SalesRecord(BaseModel):
    """Model for daily sales and inventory records."""

    model_config = ConfigDict(extra="allow")

    product_id: int | str
    date: Date | None = None
    category: str | None = None

    opening_stock: float | None = Field(
        default=None,
        ge=0,
    )
    units_received: float | None = Field(
        default=None,
        ge=0,
    )
    units_sold: float | None = Field(
        default=None,
        ge=0,
    )

    unit_price: float | None = Field(
        default=None,
        ge=0,
    )
    discount_pct: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    days_to_expiry: float | None = None
    temperature_c: float | None = None

    waste_units: float | None = Field(
        default=None,
        ge=0,
    )
    stockout_flag: int | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    @field_validator("date", mode="before")
    @classmethod
    def clean_date(cls, value):
        """Remove surrounding whitespace and quotes from dates."""

        if value is None or value == "":
            return None

        if isinstance(value, str):
            value = value.strip().strip('"').strip("'")

        return value


class SalesCreate(SalesRecord):
    """Schema for creating a sales record."""

    pass


class SalesResponse(SalesRecord):
    """Schema for returning a sales record."""

    pass


class SalesForecastItem(BaseModel):
    """Model for one product's forecast."""

    model_config = ConfigDict(extra="allow")

    product_id: int | str
    forecast_date: Date
    last_day_units_sold: float | None = None
    predicted_units_sold: float = Field(ge=0)

    @field_validator("forecast_date", mode="before")
    @classmethod
    def clean_forecast_date(cls, value):
        """Clean forecast date strings before validation."""

        if value is None or value == "":
            return None

        if isinstance(value, str):
            value = value.strip().strip('"').strip("'")

        return value


class SalesForecastResponse(BaseModel):
    """Response schema for the sales forecasting API."""

    model_config = ConfigDict(extra="allow")

    forecast_date: Date | None = None
    forecast_method: str | None = None
    forecast_type: str | None = None

    forecasts: list[SalesForecastItem] = Field(
        default_factory=list
    )

    record_count: int = 0
    notice: str | None = None