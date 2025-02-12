# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import line_item
from src.dependencies import auth
from src.schemas.line_items import LineItemOut, UpdateLineItem
from src.schemas.token import Status
from src.schemas.rental_history import RentalHistoryOut, RentalHistoryIn
from src.controllers import rental_history


router = APIRouter(
    tags=["rental_history"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.post("/rental_history", response_model=RentalHistoryOut)
async def create_rental_history(rental_History: RentalHistoryIn, user: Auth0User = Depends(auth.get_user)):
    return await rental_history.create_rental_history(rental_History, user)