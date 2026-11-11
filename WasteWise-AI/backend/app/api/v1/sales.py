
from fastapi import APIRouter, HTTPException

from app.services.forecast_service import forecast_next_day

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("/forecast")
def get_sales_forecast():
    """Return next-day demand forecasts for all products."""
    try:
        forecasts = forecast_next_day()
        return {
            "success": True,
            "count": len(forecasts),
            "forecasts": forecasts,
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
