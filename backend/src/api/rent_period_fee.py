# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import rent_period_fee as rent_period_fee_controller
from src.dependencies import auth
from src.schemas.rent_period_fee import RentPeriodFeeIn, UpdateRentPeriodFee
from src.schemas.token import Status


router = APIRouter(
    tags=["rent_period_fee"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/rent_period_fee", response_model=List[RentPeriodFeeIn])
async def create_fee(rent_period_fees: List[RentPeriodFeeIn], user: Auth0User = Depends(auth.get_user)):
    return await rent_period_fee_controller.create_rent_period_fees(rent_period_fees)


@router.patch("/rent_period_fee", response_model=Status)
async def update_fee(rent_period_fees: List[UpdateRentPeriodFee], user: Auth0User = Depends(auth.get_user)):
    return await rent_period_fee_controller.update_rent_period_fee(rent_period_fees)


@router.delete("/rent_period_fee/{rent_period_fee_id}", response_model=Status)
async def delete_fee(rent_period_fee_id: str, user: Auth0User = Depends(auth.get_user)):
    return await rent_period_fee_controller.delete_rent_period_fee(rent_period_fee_id, user)
    
