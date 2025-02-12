# Pip imports
from typing import List
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.dependencies import auth
from src.schemas.cost_type import CostTypeOut
from src.controllers import cost_type


router = APIRouter(
    tags=["cost_type"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.get("/cost_type", response_model=List[CostTypeOut])
async def get_all_cost_types(user: Auth0User = Depends(auth.get_user)):
    return await cost_type.get_all_types(user)
