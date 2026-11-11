
from fastapi import APIRouter, HTTPException

from app.services.risk_service import predict_expiry_risk

router = APIRouter(prefix="/risk", tags=["Expiry Risk"])


@router.get("/expiry")
def get_expiry_risk():
    """Return experimental expiry-risk predictions for inventory batches."""
    try:
        predictions = predict_expiry_risk()
        return {
            "success": True,
            "count": len(predictions),
            "predictions": predictions,
            "note": (
                "Experimental predictions from simulated labels; "
                "not a food-safety determination."
            ),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
