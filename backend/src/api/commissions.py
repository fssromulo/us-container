# Pip imports
from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache
from typing import List, Any, Dict

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import commission
from src.crud.commission_crud import commission_crud
from src.dependencies import auth
from src.schemas.commission import CommissionIn, CommissionOut


router = APIRouter(
    tags=["commission"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/commission", response_model=CommissionOut)
async def create_commission(commission: CommissionIn, user: Auth0User = Depends(auth.get_user)):
    return await commission.create_commission(commission, user)


@router.get(
    "/update_commission_period",
)
async def update_commission_period(
    start_date: str = None,
    end_date: str = None,
    team: bool = False,
    open: bool = False,
    user: Auth0User = Depends(auth.get_user),
    is_Manager_Only: bool = True,
):
    return await commission.update_commission_period(user, start_date, end_date, team, open, is_Manager_Only)

@router.post("/closed_commissions_date")
async def closed_commissions_date(dates: Dict[Any, Any], user: Auth0User = Depends(auth.get_user)):
    return await commission.closed_commissions_date(dates, user)

@router.get("/closed_commission_results")
async def closed_commissions_results(
    user_id: str = None,
    emulated_user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    team: bool = False,
    user: Auth0User = Depends(auth.get_user),
    is_manager_only: bool = True,
):
    return await commission.close_commission_result(
        user, user_id, emulated_user_id, start_date, end_date, team, is_manager_only
    )


@router.get("/commissions")
@cache(namespace="commissions", expire=60 * 10)
async def generate_commissions(
    user_id: str = None,
    emulated_user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    team: bool = False,
    user: Auth0User = Depends(auth.get_user),
):
    user_commissions = await commission_crud.get_all(None)
    return await commission.generate_commissions(
        user, user_id, emulated_user_id, start_date, end_date, team, user_commissions
    )
