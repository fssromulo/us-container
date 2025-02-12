
# Pip imports
from fastapi import APIRouter, Depends, status
from typing import List

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import role
from src.dependencies import auth
from src.schemas.role import RoleOut, RoleIn

router = APIRouter(
    tags=["roles"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.post("/roles_rate", response_model=RoleOut)
async def create_role(current_role: RoleIn, user: Auth0User = Depends(auth.get_user)):
    return await role.create_role(current_role, user)

@router.get("/roles_rate")
async def get_roles(user: Auth0User = Depends(auth.get_user)):
    return await role.fetch_account_roles(user)
