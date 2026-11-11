import os

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


@router.get("/status")
def auth_status():
    """Check whether demo authentication is configured."""

    configured = bool(
        os.getenv("WASTWISE_USERNAME")
        and os.getenv("WASTWISE_PASSWORD")
    )

    return {
        "service": "WasteWise AI Authentication",
        "configured": configured,
        "mode": "demo",
    }


@router.post("/login")
def login(credentials: LoginRequest):
    """
    Prototype login endpoint.

    Configure credentials through environment variables.
    This endpoint does not create a persistent session
    or issue an authentication token.
    """

    expected_username = os.getenv("WASTWISE_USERNAME")
    expected_password = os.getenv("WASTWISE_PASSWORD")

    if not expected_username or not expected_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Authentication is not configured. "
                "Set WASTWISE_USERNAME and WASTWISE_PASSWORD."
            ),
        )

    if (
        credentials.username != expected_username
        or credentials.password != expected_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return {
        "authenticated": True,
        "username": credentials.username,
        "message": "Demo login successful.",
        "notice": (
            "Prototype only. No persistent session or token "
            "has been created."
        ),
    }