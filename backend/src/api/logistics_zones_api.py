# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.crud.logistics_zones_crud import logistics_zones_crud
from src.dependencies import auth
from src.schemas.logistics_zones import CreateUpdateLogisticsZone, LogisticsZonesInSchema, LogisticsZonesOutSchema
from src.schemas.token import Status


router = APIRouter(
    tags=["logistics_zones"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/logistics_zones", response_model=list[LogisticsZonesOutSchema])
async def get_logistics_zones(user: Auth0User = Depends(auth.get_user)):
    return await logistics_zones_crud.get_all(account_id=user.app_metadata['account_id'])


@router.patch("/logistics_zones/{id}")
async def update_logistics_zones(id: str, dataReq: CreateUpdateLogisticsZone, user: Auth0User = Depends(auth.get_user)):
    reqDict = dataReq.dict()
    reqDict['account_id'] = user.app_metadata['account_id']
    return await logistics_zones_crud.update(user.app_metadata['account_id'], id, LogisticsZonesInSchema(**reqDict))


@router.post("/logistics_zones/{id}")
async def create_logistics_zones(id: str, dataReq: CreateUpdateLogisticsZone, user: Auth0User = Depends(auth.get_user)):
    reqDict = dataReq.dict()
    reqDict['account_id'] = user.app_metadata['account_id']
    await logistics_zones_crud.create(LogisticsZonesInSchema(**reqDict))
    return Status(message="Successfully created logistiscs zone")


@router.delete("/logistics_zones/{id}")
async def delete_logistics_zones(id: str, user: Auth0User = Depends(auth.get_user)):
    await logistics_zones_crud.delete_one(user.app_metadata['account_id'], id)
    return Status(message="Successfully deleted logistics zone.")
