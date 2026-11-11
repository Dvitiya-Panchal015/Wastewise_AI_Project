from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class UserBase(BaseModel):
    """Common fields for a user."""

    model_config = ConfigDict(extra="allow")

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    full_name: str | None = Field(
        default=None,
        max_length=100,
    )


class UserCreate(UserBase):
    """Fields required when creating a user."""

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(UserBase):
    """Safe user information returned by an API."""

    id: int | str
    is_active: bool = True
    created_at: datetime | None = None


class UserUpdate(BaseModel):
    """Optional fields for updating a user."""

    model_config = ConfigDict(extra="forbid")

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    email: EmailStr | None = None

    full_name: str | None = Field(
        default=None,
        max_length=100,
    )

    is_active: bool | None = None


class UserLogin(BaseModel):
    """Credentials submitted during login."""

    username: str = Field(
        min_length=1,
        max_length=50,
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )