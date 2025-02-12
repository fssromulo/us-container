# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, status
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import customer_application
from src.dependencies import auth
from src.schemas.customer_application import CreateUpdateCustomerApplicationResponse, CustomerApplicationResponseOut
from src.schemas.orders import OrderOut, PublicOrderOut
from src.schemas.token import Status


router = APIRouter(
    tags=["customer_applications"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/customer_applications", response_model=List[CustomerApplicationResponseOut])
async def get_all_customer_applications(user: Auth0User = Depends(auth.get_user)):
    return await customer_application.get_all_customer_app_responses(user)


@router.get("/customer_application/{customer_application_id}", response_model=CustomerApplicationResponseOut)
async def get_customer_app_response(
    customer_application_id: str, user: Auth0User = Depends(auth.get_user)
) -> CustomerApplicationResponseOut:
    return await customer_application.get_customer_app_response(customer_application_id, user)




@router.patch("/customer_application/{app_id}", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def update_customer_app_response(
    app_id: str, application: CreateUpdateCustomerApplicationResponse, user: Auth0User = Depends(auth.get_user)
) -> OrderOut:
    return await customer_application.update_customer_app_response(app_id, application, user)


@router.delete(
    "/customer_application/{customer_application_id}",
    response_model=Status,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def delete_customer_application(customer_application_id: str, user: Auth0User = Depends(auth.get_user)):
    return await customer_application.delete_customer_application(customer_application_id, user)


#######
# Customer application schema endpoints
#######

# @router.patch(
#     "/customer_application_schema/{customer_app_schema_id}",
#     response_model=CustomerApplicationOut,
#     responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
# )
# async def update_container_price(
#     customer_application_id: str, container_price: CreateUpdateContainerPrice, user: Auth0User = Depends(auth.get_user)
# ) -> CustomerApplicationOut:
#     return await container_pricing.update_container_price(customer_application_id, container_price, user)
