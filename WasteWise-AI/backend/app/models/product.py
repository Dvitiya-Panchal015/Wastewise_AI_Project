from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Common fields for a product."""

    model_config = ConfigDict(extra="allow")

    product_name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    shelf_life_days: int = Field(gt=0)
    selling_price: float = Field(ge=0)
    unit_cost: float = Field(ge=0)


class ProductCreate(ProductBase):
    """Fields required to create a product."""

    product_id: int | str


class Product(ProductBase):
    """Product model returned by the API."""

    product_id: int | str


class ProductUpdate(BaseModel):
    """Fields that can be updated on a product."""

    model_config = ConfigDict(extra="allow")

    product_name: str | None = None
    category: str | None = None
    shelf_life_days: int | None = Field(
        default=None,
        gt=0,
    )
    selling_price: float | None = Field(
        default=None,
        ge=0,
    )
    unit_cost: float | None = Field(
        default=None,
        ge=0,
    )