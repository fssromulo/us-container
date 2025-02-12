# Python imports
from typing import List, Optional, Any

# Pip imports
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import container_pricing
from src.dependencies import auth
from src.schemas.container_product import ContainerProductOut, GlobalPodSettings, IsPayOnDeliveryRequest
from src.schemas.token import Status
from src.schemas.container_locations import CreateUpdateContainerPrice

class RentalPriceSize(BaseModel):
    container_size: Optional[str]
    rental_price: Optional[int]


router = APIRouter(
    tags=["container_pricing"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/prices", response_model=List[ContainerProductOut])
async def get_all_container_prices(user: Auth0User = Depends(auth.get_user)):
    return await container_pricing.get_all_container_prices(user)


@router.post("/set_rental_price")
async def set_rental_price(data: RentalPriceSize, user: Auth0User = Depends(auth.get_user)):
    return await container_pricing.set_rental_price(
        data.container_size, data.rental_price, user.app_metadata['account_id']
    )


@router.get("/price/{container_price_id}", response_model=ContainerProductOut)
async def get_container_price(
    container_price_id: str, user: Auth0User = Depends(auth.get_user)
):
    get_container_price = [p for p in user.permissions if p == "read:navigation-products"]
    if not get_container_price:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to retrieve container prices",
        )
    return await container_pricing.get_container_price(container_price_id, user)


@router.post("/price", response_model=ContainerProductOut, status_code=status.HTTP_201_CREATED)
async def create_container_price(
    container_price: CreateUpdateContainerPrice, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    create_container_price = [p for p in user.permissions if p == "create:product"]
    if not create_container_price:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to retrieve create container price",
        )
    return await container_pricing.create_container_price(container_price, user, background_tasks)


@router.patch(
    "/price/{container_price_id}",
    response_model=ContainerProductOut,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def update_container_price(
    container_price_id: str, background_tasks: BackgroundTasks, container_price: CreateUpdateContainerPrice, user: Auth0User = Depends(auth.get_user)
):
    create_container_price = [p for p in user.permissions if p == "update:product"]
    if not create_container_price:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission update container price",
        )
    return await container_pricing.update_container_price(container_price_id, container_price, user, background_tasks)


@router.delete(
    "/price/{container_price_id}",
    response_model=Status,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def delete_container_price(container_price_id: str,  background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)):
    return await container_pricing.delete_container_price(container_price_id, user, background_tasks)

@router.get("/get_all_container_attributes")
async def get_all_container_attributes():
    return await container_pricing.get_all_container_attributes()



@router.post("/set_global_pod")
async def set_global_pod(body: GlobalPodSettings, user: Auth0User = Depends(auth.get_user)):
    return await container_pricing.set_global_pod(body, user)

@router.post("/is_pay_on_delivery")
async def is_pay_on_delivery(body: IsPayOnDeliveryRequest, user: Auth0User = Depends(auth.get_user)):
    return await container_pricing.is_pay_on_delivery(body, user)