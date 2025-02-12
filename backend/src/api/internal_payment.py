# Python imports
import os
from typing import List, Any, Dict
import uuid

# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import payment as payment_controller
from src.crud.order_crud import OrderCRUD
from src.crud.user_crud import UserCRUD
from src.dependencies import auth
from src.schemas.payment import (
    CreditCardObj,
    DeleteCustomerPaymentProfile,
    DeleteCustomerProfile,
    OtherPayment,
    Payment,
)

from ..crud.customer_crud import CustomerCRUD
from ..crud.location_distance_crud import LocationDistanceCRUD


BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")

order_crud = OrderCRUD()
customer_crud = CustomerCRUD()
user_crud = UserCRUD()
location_distances_crud = LocationDistanceCRUD()


router = APIRouter(
    tags=["payment"],
    prefix="/payment",
)


@router.get("/customer_profile/{customer_profile_id}")
async def credit_card_payment(customer_profile_id: str, user: Auth0User = Depends(auth.get_user)):
    return await payment_controller.get_customer_profile_by_id(customer_profile_id, user)


@router.post(
    "/rental",
)
async def credit_card_payment(payment_request: Payment, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)):
    return await payment_controller.credit_card_rentals(payment_request, background_tasks, user)


@router.post(
    "/rental/other",
)
async def rent_other_payment(other_payment: OtherPayment, user: Auth0User = Depends(auth.get_user)):
    return await payment_controller.handle_other_payment(other_payment, user=user)

@router.post(
    "/rental/other_orders",
)
async def rent_other_payment(other_payment: Dict[Any, Any], user: Auth0User = Depends(auth.get_user)):
    return await payment_controller.handle_other_orders_payment(other_payment, user=user)

class RentPeriodsRequest(BaseModel):
    rent_periods: List[Dict[Any, Any]]

@router.post(
    "/rental/waive_all_fees",
)
async def rent_other_payment(request: RentPeriodsRequest, user: Auth0User = Depends(auth.get_user)):
    rent_period_ids = [x['id'] for x in request.rent_periods]
    return await payment_controller.waive_all_fees(rent_period_ids, user)


@router.post(
    "/rental/other/credit_card",
)
async def rent_other_payment(other_payment: OtherPayment, payment_request: Payment, background_tasks: BackgroundTasks,  user: Auth0User = Depends(auth.get_user)):
    transaction_type_group_id = str(uuid.uuid4())
    return await payment_controller.handle_other_payment_credit_card(other_payment, payment_request, background_tasks, transaction_type_group_id=transaction_type_group_id, user=user)


@router.post(
    "/rental/other_orders/credit_card",
)
async def rent_other_orders_payment(other_payment: Dict[Any, Any], payment_request: Payment,  background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user),):
    return await payment_controller.handle_other_orders_payment_credit_card(other_payment, payment_request, background_tasks, user)


@router.post(
    "/change_credit_card",
)
async def change_credit_card(change_credit_card_request: CreditCardObj, background_tasks: BackgroundTasks):
    return await payment_controller.change_credit_card(change_credit_card_request, background_tasks)


@router.post(
    "/add_card_on_file",
)
async def add_card_on_file(credit_card_request: CreditCardObj, background_tasks: BackgroundTasks):
    return await payment_controller.add_card_on_file(credit_card_request, background_tasks)


@router.post(
    "/add_ach",
)
async def add_ach(credit_card_request: CreditCardObj):
    return await payment_controller.add_ach(credit_card_request)


@router.post(
    "/update_ach",
)
async def add_ach(credit_card_request: CreditCardObj):
    return await payment_controller.update_ach(credit_card_request)


@router.delete(
    "/remove_customer_profile",
)
async def remove_customer_profile(data: DeleteCustomerProfile):
    return await payment_controller.remove_customer_profile(data.order_id)


@router.delete("/remove_customer_payment_profile")
async def remove_customer_payment_profile(data: DeleteCustomerPaymentProfile):
    return await payment_controller.remove_customer_payment_profile(data.order_id, data.type)
