# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import inventory_address
from src.dependencies import auth
from src.schemas.address import CreateUpdateAddress
from src.schemas.line_items import LineItemOut


router = APIRouter(
    tags=["inventory_address"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/inventory_address", response_model=LineItemOut)
async def create_inventory_address(address: CreateUpdateAddress, user: Auth0User = Depends(auth.get_user)):
    return await inventory_address.create_inventory_address(address, user)


@router.patch("/inventory_address/{id}", response_model=LineItemOut)
async def create_inventory_address(id: str, address: CreateUpdateAddress, user: Auth0User = Depends(auth.get_user)):
    return await inventory_address.update_inventory_address(id, address, user)
