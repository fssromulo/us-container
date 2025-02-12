# Python imports

# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import rent_period_info as rent_period_info_controller
from src.controllers import rent_period as rent_period_controller
from src.dependencies import auth
from src.schemas.rent_period_info import UpdateRentPeriodInfo, UpdatePeriodPrice, UpdatePeriodDueDate, UpdatedPeriod, AddRentalPeriods
from src.schemas.token import Status



router = APIRouter(
    tags=["rent_period_info"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/rent_period_info", response_model=Status)
async def update_rent_period_info(rent_period_info: UpdateRentPeriodInfo, user: Auth0User = Depends(auth.get_user)):
    await rent_period_info_controller.update_rent_period_info(rent_period_info)
    return Status(message="Successfully updated rent period info")

@router.put("/rent_period_price", response_model=Status)
async def update_rent_period_price(data: UpdatePeriodPrice, user: Auth0User = Depends(auth.get_user)):
    await rent_period_info_controller.update_rent_period_price(data.order_id, data.price)
    return Status(message="Successfully updated rent period cost.")
@router.put("/generate_new_periods", response_model=Status)
async def generate_new_rental_period(data: AddRentalPeriods, user: Auth0User = Depends(auth.get_user)):
    await rent_period_info_controller.generate_new_rental_period(data.order_id, data.number_of_period)
    return Status(message="Successfully updated rent period cost.")

@router.patch("/rent_period_due_date", response_model=Status)
async def update_rent_period_price(data: UpdatePeriodDueDate, user: Auth0User = Depends(auth.get_user)):
    await rent_period_controller.modify_rent_period_due_dates(data.updated_period, data.subsequent_period_ids)
    return Status(message="Successfully updated rent period due dates.")
