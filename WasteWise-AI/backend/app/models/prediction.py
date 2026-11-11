from datetime import date as Date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionBase(BaseModel):
    """Base model for prediction API responses."""

    model_config = ConfigDict(extra="allow")


class SalesForecast(PredictionBase):
    """Model for a product sales forecast."""

    product_id: int | str
    forecast_date: Date
    predicted_units_sold: float
    last_day_units_sold: float | None = None

    @field_validator("forecast_date", mode="before")
    @classmethod
    def clean_forecast_date(cls, value):
        """Remove accidental quotes and spaces from dates."""

        if value is None or value == "":
            return None

        if isinstance(value, str):
            value = value.strip().strip('"').strip("'")

        return value


class SalesForecastResponse(PredictionBase):
    """Response containing sales forecasts."""

    forecast_date: Date | None = None
    forecast_method: str | None = None
    forecast_type: str | None = None
    forecasts: list[SalesForecast] = Field(
        default_factory=list
    )
    record_count: int = 0
    notice: str | None = None


class ExpiryRiskPrediction(PredictionBase):
    """Model for an inventory expiry-risk prediction."""

    batch_id: int | str
    product_id: int | str
    category: str | None = None

    days_to_expiry: float
    quantity_remaining: float

    predicted_risk_status: str
    high_risk_probability: float = Field(
        ge=0,
        le=1,
    )

    prediction_note: str | None = None


class ExpiryRiskResponse(PredictionBase):
    """Response containing expiry-risk predictions."""

    total: int = 0
    predictions: list[ExpiryRiskPrediction] = Field(
        default_factory=list
    )


class WasteRecommendation(PredictionBase):
    """Model for a waste-reduction recommendation."""

    batch_id: int | str
    product_id: int | str
    category: str | None = None

    days_to_expiry: float
    quantity_remaining: float

    predicted_risk_status: str | None = None
    high_risk_probability: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    priority_score: float | None = None
    recommendation: str

    prediction_note: str | None = None


class WasteRecommendationsResponse(PredictionBase):
    """Response containing waste recommendations."""

    total: int = 0
    recommendations: list[WasteRecommendation] = Field(
        default_factory=list
    )


class PredictionSummary(PredictionBase):
    """General summary of prediction results."""

    status: str = "success"
    total_predictions: int = 0
    model_name: str | None = None
    generated_at: Date | None = None
    metrics: dict[str, Any] = Field(
        default_factory=dict
    )