from typing import Annotated

from fastapi import Depends

from app.services.inventory_service import InventoryService


def get_inventory_service() -> InventoryService:
    """Provide an inventory service instance to API routes."""

    return InventoryService()


InventoryServiceDependency = Annotated[
    InventoryService,
    Depends(get_inventory_service),
]