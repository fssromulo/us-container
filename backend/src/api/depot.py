# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, status
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import depot
from src.dependencies import auth
from src.schemas.depot import CreateOrUpdateDepot, DepotOutSchema
from src.schemas.token import Status


router = APIRouter(tags=["depot"], dependencies=[Depends(auth.implicit_scheme)])


@router.get("/depots", response_model=List[DepotOutSchema])
async def get_container_depots(user: Auth0User = Depends(auth.get_user)) -> List[DepotOutSchema]:
    return await depot.get_all_container_depots(user)


@router.get("/depot/{container_depot_id}", response_model=DepotOutSchema)
async def get_container_depot(container_depot_id: str, user: Auth0User = Depends(auth.get_user)) -> DepotOutSchema:
    return await depot.get_container_depot(container_depot_id, user)

@router.get("/depot{container_depot_name}", response_model=DepotOutSchema)
async def get_container_depot_by_name(container_depot_name:str, user:Auth0User = Depends(auth.get_user)) -> DepotOutSchema:
    return await depot.get_container_depot_by_name(container_depot_name, user)

@router.post("/depot", response_model=DepotOutSchema, status_code=status.HTTP_201_CREATED)
async def create_depot(
    container_depot: CreateOrUpdateDepot, user: Auth0User = Depends(auth.get_user)
) -> DepotOutSchema:
    return await depot.create_depot(container_depot, user)


@router.patch(
    "/depot/{container_depot_id}",
    response_model=DepotOutSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def update_depot(
    container_depot_id: str, container_depot: CreateOrUpdateDepot, user: Auth0User = Depends(auth.get_user)
) -> DepotOutSchema:
    return await depot.update_depot(container_depot_id, container_depot, user)


@router.delete(
    "/depot/{container_depot_id}",
    response_model=Status,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def delete_container_depot(container_depot_id: str, user: Auth0User = Depends(auth.get_user)) -> Status:
    return await depot.delete_container_depot(container_depot_id, user)
