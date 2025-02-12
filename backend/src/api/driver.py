# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, status
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import driver
from src.dependencies import auth
from src.schemas.driver import DriverOutSchema, UpdateDriver
from src.schemas.token import Status


router = APIRouter(tags=["driver"], dependencies=[Depends(auth.implicit_scheme)])


@router.get("/drivers", response_model=List[DriverOutSchema])
@cache(namespace="drivers", expire=60 * 10)
async def get_drivers(user: Auth0User = Depends(auth.get_user)):
    return await driver.get_all_drivers(user)


@router.get("/driver/{container_driver_id}", response_model=DriverOutSchema)
async def get_driver(container_driver_id: str, user: Auth0User = Depends(auth.get_user)) -> DriverOutSchema:
    return await driver.get_driver(container_driver_id, user)


@router.post("/driver", response_model=DriverOutSchema, status_code=status.HTTP_201_CREATED)
async def create_driver(container_driver: UpdateDriver, user: Auth0User = Depends(auth.get_user)) -> DriverOutSchema:
    await FastAPICache.clear(namespace="drivers")
    return await driver.create_driver(driver=container_driver, user=user)


@router.patch(
    "/driver/{container_driver_id}",
    response_model=DriverOutSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def update_driver(
    container_driver_id: str, container_driver: UpdateDriver, user: Auth0User = Depends(auth.get_user)
) -> DriverOutSchema:
    await FastAPICache.clear(namespace="drivers")
    return await driver.update_container_driver(driver_id=container_driver_id, driver=container_driver, user=user)


@router.delete(
    "/driver/{container_driver_id}",
    response_model=Status,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def delete_container_driver(container_driver_id: str, user: Auth0User = Depends(auth.get_user)) -> Status:
    await FastAPICache.clear(namespace="drivers")
    return await driver.delete_container_driver(driver_id=container_driver_id, user=user)
