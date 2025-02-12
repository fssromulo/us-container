# Python imports
from datetime import datetime
from typing import Any, List

# Pip imports
from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import contracts
from src.crud.account_crud import account_crud
from src.crud.customer_app_response import customer_app_response_crud
from src.crud.customer_crud import customer_crud
from src.crud.order_crud import order_crud
from src.database.models.account import Account
from src.database.models.orders.order import Order
from src.schemas.customer import CustomerIn
from src.schemas.customer_application import (
    CreateUpdateCustomerApplicationResponse,
    CustomerApplicationResponseIn,
    CustomerApplicationResponseOut,
)
from src.schemas.orders import OrderInUpdate, OrderOut, PublicOrderOut
from src.schemas.token import Status
from src.services.notifications import email_service, email_service_mailersend


async def save_customer_app_response(
    customer_app_response: CreateUpdateCustomerApplicationResponse,
    account_id: int,
    customer_app_response_id: str = None,
) -> CustomerApplicationResponseOut:
    customer_app_response_dict = customer_app_response.dict(exclude_unset=True)
    customer_app_response_dict['customer_application_schema_id'] = customer_app_response_dict["schema_id"]
    customer_app_response_dict.pop("schema_id")
    accepted = customer_app_response.accepted
    del customer_app_response_dict["accepted"]

    if customer_app_response_id:
        dates_dict = {}
        if accepted:
            dates_dict["date_accepted"] = datetime.now()
        else:
            dates_dict["date_rejected"] = datetime.now()

        saved_customer_app_response = await customer_app_response_crud.update(
            account_id,
            customer_app_response_id,
            CustomerApplicationResponseIn(**customer_app_response_dict, **dates_dict),
        )
    else:
        saved_customer_app_response = await customer_app_response_crud.create(
            CustomerApplicationResponseIn(**customer_app_response_dict)
        )

    return saved_customer_app_response


async def get_all_customer_app_responses(user: Auth0User) -> List[CustomerApplicationResponseOut]:
    return await customer_app_response_crud.get_all(user.app_metadata.get("account_id"))


async def get_customer_app_response(customer_app_response_id: str, user: Auth0User) -> CustomerApplicationResponseOut:
    try:
        return await customer_app_response_crud.get_one(user.app_metadata.get("account_id"), customer_app_response_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container price does not exist")


@atomic()
async def create_customer_app_response(
    customer_application_response: CreateUpdateCustomerApplicationResponse,
) -> PublicOrderOut:
    customer_application_response.accepted = False
    order: OrderOut = await order_crud.get_one(customer_application_response.order_id, is_public=True)
    customer_app_response = await save_customer_app_response(customer_application_response, order.account_id)
    await order_crud.set_schema_id(customer_application_response.order_id, customer_application_response.schema_id)
    order: OrderOut = await order_crud.get_one(customer_app_response.order_id, is_public=True)

    account: Account = await account_crud.get_one(order.account_id)
    rent_options: dict[str, Any] = account.cms_attributes.get('rent_options')

    if account.name.startswith("USA Containers"):
        for key in customer_app_response.response_content:
            if 'email' in key:
                new_email = customer_app_response.response_content[key]

                if new_email != order.customer.email:
                    await customer_crud.update(
                        order.account_id,
                        order.customer.id,
                        CustomerIn(**{"account_id": order.account_id, "email": new_email}),
                    )

        rent_email = rent_options.get('rent_email', "rentals@usacontainers.co")
        email_service.send_application_submitted_email(
            rent_email, display_order_id=order.display_order_id, order_id=order.id
        )

        email_service.send_application_submitted_email_to_customer(order.customer.email, order.display_order_id)
    elif account.id == 2:
        rent_email = rent_options.get('agreement_lessor_email', "paul@amobilebox.co")
        email_service_mailersend.send_application_submitted_email(
            rent_email, display_order_id=order.display_order_id, order_id=order.id
        )

        email_service_mailersend.send_application_submitted_email_to_customer(order.customer.email)

    if rent_options.get("is_use_in-house_emails", False):
        email_service_mailersend.send_submitted_application_email(order, account)
    return order


def check_line_items_container_attached(order: OrderOut):
    for line_item in order.line_items:
        if line_item.inventory is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One of your line items does not have a container associated with it. Please add a container to the line item and resubmit.",
            )


@atomic()
async def update_customer_app_response(
    app_id: str, customer_app_response: CreateUpdateCustomerApplicationResponse, user: Auth0User
) -> OrderOut:
    order: Order = await order_crud.get_one(customer_app_response.order_id)
    account: Account = await account_crud.get_one(order.account_id)
    accepted = customer_app_response.accepted
    if customer_app_response.accepted:
        if account.cms_attributes.get('send_contract_without_container_attached', False):
            check_line_items_container_attached(order)
        await contracts.send_rental_agreement(order.id)
    else:
        email_service_mailersend.send_declined_application_email(order, account)
    customer_app_response = await save_customer_app_response(
        customer_app_response, user.app_metadata.get("account_id"), app_id
    )

    if not accepted:
        await order_crud.update(
            order.account_id,
            str(customer_app_response.order_id),
            OrderInUpdate(
                **{
                    "status": "Cancelled",
                    "account_id": user.app_metadata.get("account_id"),
                }
            ),
        )
    return await order_crud.get_one(str(customer_app_response.order_id))


async def delete_customer_app_response(customer_app_response_id: str, user: Auth0User) -> Status:
    await customer_app_response_crud.delete_one(user.app_metadata.get("account_id"), customer_app_response_id)
    return Status(message=f"Deleted container price {customer_app_response_id}")
