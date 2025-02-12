# Pip imports
from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import fee_type
from src.dependencies import auth
from src.schemas.fee_type import FeeTypeIn, FeeTypeOut, FeeTypeUpdate


router = APIRouter(
    tags=["fee_type"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/fee_type", response_model=FeeTypeOut)
async def create_fee_type(fee_type_in: FeeTypeIn, user: Auth0User = Depends(auth.get_user)):
    return await fee_type.create_fee_type(fee_type_in, user)


@router.patch("/fee_type/{id}")
async def update_fee_type(id: str, fee_type_in: FeeTypeUpdate, user: Auth0User = Depends(auth.get_user)):
    return await fee_type.update_fee_type(id, fee_type_in, user)


@router.get("/fee_type")
@cache(namespace="fee_type", expire=60 * 10)
async def fetch_fee_types(user: Auth0User = Depends(auth.get_user)):
    return await fee_type.fetch_fee_types(user)
