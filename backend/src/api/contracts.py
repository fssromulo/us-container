# Python imports
from typing import Dict, Optional

# Pip imports
from fastapi import APIRouter, Depends

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import contracts as contract_controller
from src.dependencies import auth


router = APIRouter(
    tags=["contracts"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={404: {"description": "Not found"}},
    prefix="/contracts",
)


@router.get("/send_main_contract", response_model=Dict[str, str])
async def send_main_contract(order_id: str, user: Auth0User = Depends(auth.get_user)) -> Dict[str, str]:
    if user.app_metadata['account_id'] == 1 :
        return await contract_controller.send_rental_email_contract(order_id)
    else:
        return await contract_controller.send_rental_agreement(order_id)


@router.get("/send_authorization_form", response_model=Dict[str, str])
async def send_authorization_agreement(order_id: str, with_photo: Optional[bool] = False, user: Auth0User = Depends(auth.get_user)) -> Dict[str, str]:
    return await contract_controller.send_authorization_agreement(order_id, with_photo)


@router.get("/send_payment_on_delivery_contract_real/{display_order_id}/{account_id}")
async def send_payment_on_delivery_contract_real(display_order_id, account_id):
    return await contract_controller.payment_on_delivery_contract(display_order_id, account_id)


@router.get("/send_payment_on_delivery_contract/{order_id}")
async def payment_on_delivery_contract(order_id: str, user: Auth0User = Depends(auth.get_user)) -> Dict[str, str]:
    return await contract_controller.send_email_contract(order_id, user)

@router.get("/send_rental_contract_real/{display_order_id}")
async def send_rental_contract_real(display_order_id):
    return await contract_controller.send_rental_email_contract(display_order_id)

