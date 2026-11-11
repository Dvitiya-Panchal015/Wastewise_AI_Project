
from fastapi import APIRouter, HTTPException

from app.services.recommendation_service import (
    get_waste_recommendations,
)

router = APIRouter(prefix="/waste", tags=["Waste Recommendations"])


@router.get("/recommendations")
def get_recommendations():
    """Return prioritized waste-reduction recommendations."""
    try:
        recommendations = get_waste_recommendations()
        return {
            "success": True,
            "count": len(recommendations),
            "recommendations": recommendations,
            "note": (
                "Recommendations use experimental expiry-risk predictions. "
                "Verify expiry and food-safety requirements before acting."
            ),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
