# Pip imports
from typing import List
from fastapi import APIRouter, Depends, status

# Internal imports
from src.schemas.token import Status
from src.auth.auth import Auth0User
from src.dependencies import auth
from src.schemas.misc_cost import MiscCostOut, MiscCostIn, UpdateMiscCost
from src.controllers import misc_costs


router = APIRouter(
    tags=["misc_costs"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.post("/misc_costs", response_model=Status)
async def create_misc_cost(misc_cost: List[MiscCostIn], user: Auth0User = Depends(auth.get_user)):
    return await misc_costs.create_misc_cost(misc_cost, user)

@router.patch("/misc_costs", response_model=Status)
async def update_misc_cost(misc_cost: List[UpdateMiscCost], user: Auth0User = Depends(auth.get_user)):
    return await misc_costs.update_misc_cost(misc_cost, user)

@router.delete("/misc_costs/{misc_cost_id}", response_model=Status)
async def delete_misc_cost(misc_cost_id: str, user: Auth0User = Depends(auth.get_user)):
    return await misc_costs.delete_misc_cost(misc_cost_id, user)