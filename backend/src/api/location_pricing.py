# Python imports
import os
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, status
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import location_pricing
from src.dependencies import auth
from src.schemas.container_locations import CreateUpdateLocationPrice, LocationPriceOutSchema
from src.schemas.location_price import LocationPriceOut
from src.schemas.token import Status
from src.crud.fixed_location_price_crud import fixed_location_price_crud

BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")

router = APIRouter(
    tags=["location_pricing"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/locations", response_model=List[LocationPriceOut])
@cache(namespace="locations", expire=60 * 20)
async def get_container_locations(user: Auth0User = Depends(auth.get_user)):
    # get_ware_house = [p for p in user.permissions if p == "read:order_column-warehouse"]
    # if not get_ware_house:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You do not have permission to retrieve container location",
    #     )
    return await location_pricing.get_container_locations(user)


@router.get("/location/{container_location_id}", response_model=LocationPriceOut)
async def get_container_location(
    container_location_id: str, user: Auth0User = Depends(auth.get_user)
) -> LocationPriceOutSchema:
    # get_ware_house = [p for p in user.permissions if p == "read:order_column-warehouse"]
    # if not get_ware_house:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You do not have permission to retrieve container location",
    #     )
    return await location_pricing.get_container_location(container_location_id, user)


@router.post("/location", response_model=LocationPriceOut)
async def create_location(
    container_location: CreateUpdateLocationPrice, user: Auth0User = Depends(auth.get_user)
) -> LocationPriceOut:
    await FastAPICache.clear(namespace="locations")
    return await location_pricing.create_location(container_location, user)


@router.patch(
    "/location/{container_location_id}",
    response_model=LocationPriceOut,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def update_location(
    container_location_id: str, container_location: CreateUpdateLocationPrice, user: Auth0User = Depends(auth.get_user)
) -> LocationPriceOut:
    await FastAPICache.clear(namespace="locations")
    return await location_pricing.save_location(container_location, user, container_location_id)


@router.delete(
    "/location/{container_location_id}",
    response_model=Status,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def delete_container_location(container_location_id: str, user: Auth0User = Depends(auth.get_user)):
    await FastAPICache.clear(namespace="locations")
    return await location_pricing.delete_container_location(container_location_id, user)


@router.get("/fixed_location_prices/{postal_code}")
async def get_all_fixed_location_prices(postal_code: str, user: Auth0User = Depends(auth.get_user)):
    result = await fixed_location_price_crud.get_by_postal_code(postal_code)
    return result