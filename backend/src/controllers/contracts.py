# Python imports
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict

# Pip imports
import pytz
from fastapi import BackgroundTasks

# Internal imports
from src.controllers import customer_application as application_controller
from src.controllers import orders as order_controller
from src.crud.account_crud import account_crud
from src.crud.order_crud import order_crud

# from src.crud.tax_crud import tax_crud
from src.database.models.account import Account
from src.database.models.orders.order import Order
from src.schemas.customer_application import CreateUpdateCustomerApplicationResponse
from src.schemas.orders import OrderInUpdate
from src.schemas.token import Status
from src.services.contracts import esign
from src.services.notifications import email_service, email_service_mailersend
from src.controllers.event_controller import pod_signed_event, order_pod_signed_agent_notification
from src.crud.note_crud import note_crud, NoteInSchema
from loguru import logger


async def send_email_contract(order_id: str, user):
    order: Order = await order_crud.get_one(order_id)
    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    email_info: dict = {
        "customer_email": customer_info.get("email", ""),
        "display_order_id": order.display_order_id,
    }
    if order.account_id == 1:
        email_service.send_initial_email_payment_on_delivery(email_info)
    elif order.account_id == 4:
        account = await account_crud.get_one(order.account_id)
        email_info['first_name'] = customer_info['first_name']
        email_info['last_name'] = customer_info['last_name']
        email_service_mailersend.send_initial_email_payment_on_delivery(account, email_info)
    else:
        account = await account_crud.get_one(order.account_id)
        email_info['first_name'] = customer_info['first_name']
        email_info['last_name'] = customer_info['last_name']
        email_service_mailersend.send_initial_email_payment_on_delivery(account, email_info)


async def send_email_contract_from_payment(order_id: str):
    order: Order = await order_crud.get_one(order_id)
    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    email_info: dict = {
        "customer_email": customer_info.get("email", ""),
        "display_order_id": order.display_order_id,
    }
    email_service.send_initial_email_payment_on_delivery(email_info)


async def sign_pod_contract_from_payment(
    order_id: str,
    customer_application_response: CreateUpdateCustomerApplicationResponse,
    background_tasks: BackgroundTasks,
):
    customer_application_response.accepted = True
    order_old: Order = await order_crud.get_one(order_id)
    await application_controller.save_customer_app_response(customer_application_response, order_old.account_id)

    account: Account = await account_crud.get_one(order_old.account_id)
    if order_old.type == "PURCHASE":
        if not order_old.signed_at:
            await order_crud.update(
                order_old.account_id,
                order_old.id,
                OrderInUpdate(
                    **{"signed_at": datetime.now(timezone.utc), "account_id": order_old.account_id, "status": 'Pod'}
                ),
            )
            order_new = await order_crud.get_one(order_id)

            try:
                await note_crud.create(
                    NoteInSchema(
                        title="phone and address pod",
                        content=f'{customer_application_response.response_content.get("phone_number", "")}, {customer_application_response.response_content.get("confirmation_address_city_state_zipcode", "")}',
                        author_id=order_old.user.id,
                        order_id=order_new.id,
                    )
                )
            except Exception as e:
                logger.error(f"Error creating note for order {order_new.id}: {e}")

            # send paid questionnaire
            # await notifications_controller.send_paid_email(order.id, background_tasks)
            # send signed mail to agent
            email_text = f"You just had a customer sign the contract! Order #{order_old.display_order_id}"
            check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order_old)
            customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

            email_info: dict = {
                    "customer_email": customer_info.get("email", ""),
                    "display_order_id": order_old.display_order_id,
                    "order_id": order_new.id,
                    "payment_methods": "Zelle, credit and debit card payment" if account.cms_attributes.get("account_country", 'USA') == "USA" else "Credit and debit card payment",
                    "contact_phone": "1-800-304-0981" if account.cms_attributes.get("account_country", 'USA') == "USA" else "1-343-353-0602",
                }

            email_service.send_signed_pod_contract_mail(email_info)
            await pod_signed_event(order_new, customer_info, datetime.now(timezone.utc), background_tasks)
            if account.cms_attributes.get("sendInternalAgentEmails", True):
                external_integrations = account.external_integrations
                if external_integrations is not None and external_integrations.get("resources") is not None and len(external_integrations.get("resources")) > 0 and len([res for res in external_integrations.get("resources") if "update:user:signed_at" in res.get("event_types")]) > 0:
                    await order_pod_signed_agent_notification(order_new.display_order_id, True, order_old.account_id, await order_controller.get_agent(order_new), order_new, await order_controller.get_agent_emails(order_new), background_tasks)
                else:
                    email_service.send_agent_email(email_text, await order_controller.get_agent_emails(order_new))

async def send_rental_email_contract(order_id: str):
    order: Order = await order_crud.get_one(order_id)
    account: Account = await account_crud.get_one(order.account_id)
    rent_options: dict[str, Any] = account.cms_attributes.get("rent_options", "")
    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)
    line_items = {}
    containers = {}
    for line_item in order.line_items:
        if line_item.product_type is None or line_item.product_type != "CONTAINER_ACCESSORY":
            if line_item.container_size is not None and line_item.condition is not None:
                key = line_item.container_size + " ft " + line_item.condition
                if key not in containers:
                    containers[key] = 1
                    line_items[key] = {}
                    line_items[key]['size'] = line_item.container_size + " ft "
                    line_items[key]['quantity'] = 1
                else:
                    containers[key] += 1
                    line_items[key]['quantity'] += 1
    # delivery_state: str = order.address.state
    # account_id: int = order.account_id

    # tax_rate: Decimal = await tax_crud.get_tax_rate(account_id=account_id, state=delivery_state)

    monthly_owed: float = float(order.current_rent_period.get("amount_owed", 0))
    shipping_price: float = float(sum(x.shipping_revenue for x in order.line_items))
    total_delivery_and_pickup: float = shipping_price
    tax: float = float(Decimal(order.calculated_order_tax).quantize(Decimal(".01"), rounding=ROUND_HALF_UP))
    total_upfront: float = float(total_delivery_and_pickup + monthly_owed + tax)
    cust_full_address: str = f"{order.address.street_address}, {order.address.city}, {order.address.county}, {order.address.state}, {order.address.zip}"
    date_sent: datetime = datetime.now(tz=pytz.utc)
    contract_delivery_days: int = rent_options.get("contract_delivery_days", 30)
    date_sent += timedelta(days=contract_delivery_days)
    day_with_suffix = get_day_with_suffix(date_sent.day)
    email_info: dict = {
        "customer_email": customer_info.get("email", ""),
        "display_order_id": order.display_order_id,
        "display_id": order.id,
        "line_items": line_items,
        "monthly_owed": "{:.2f}".format(monthly_owed),
        "rent_due_on_day": day_with_suffix,
        "first_total_payment": "{:.2f}".format(total_upfront),
        "delivery_pickup_fee": "{:.2f}".format(total_delivery_and_pickup),
        "delivery_address": cust_full_address,
    }
    email_service.send_initial_rental_contract_email(email_info)
    return {"status": "Contract email sent"}


async def send_rental_agreement(order_id: str) -> Status:
    order: Order = await order_crud.get_one(order_id)
    account: Account = await account_crud.get_one(order.account_id)
    rent_options: dict[str, Any] = account.cms_attributes.get("rent_options", {})
    if rent_options.get("uses_signature_wrapper", False):
        await send_rental_email_contract(order_id)
        return {"sign_page_url": ""}
    else:
        check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order)
        customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)
        contract_url = await fetch_rental_contract(order_id)
        email_info: dict = {
            "customer_email": customer_info.get("email", ""),
            "display_order_id": order.display_order_id,
            "url": contract_url['sign_page_url'],
            "company_name": account.cms_attributes.get("company_name"),
            "account_id": account.id,
        }
        if rent_options.get("is_use_in-house_emails", False):
            await email_service_mailersend.send_rental_agreement(email_info)
        return contract_url


async def fetch_rental_contract(order_id: str) -> Status:
    order: Order = await order_crud.get_one(order_id)
    account: Account = await account_crud.get_one(order.account_id)
    sign_page_url = await esign.send_rental_agreement(order, account)
    return {"sign_page_url": sign_page_url}


async def send_authorization_agreement(order_id: str, with_photo: bool) -> Dict[str, str]:
    order: Order = await order_crud.get_one(order_id)
    account: Account = await account_crud.get_one(order.account_id)
    sign_page_url = await esign.prepare_authorization_agreement(order, account, with_photo)
    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    email_info: dict = {
        "customer_email": customer_info.get("email", ""),
        "display_order_id": order.display_order_id,
        "url": sign_page_url,
        "company_name": account.cms_attributes.get("company_name"),
    }

    email_service_mailersend.send_authorization_agreement(email_info, account)

    return {"sign_page_url": sign_page_url}


async def payment_on_delivery_contract(display_order_id: str, account_id: str) -> Dict[str, str]:
    order: Order = await order_crud.get_one_by_display_id(int(account_id), display_order_id)

    if order.pod_sign_page_url:
        return {"sign_page_url": order.pod_sign_page_url}

    if order.calculated_contract_total >= 10:
        return {"contract_limit_reached": "true"}

    account: Account = await account_crud.get_one(order.account_id)

    sign_page_url = await esign.send_payment_on_delivery_contract(order, account)
    # check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order)
    # customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    # email_info: dict = {
    #     "customer_email": customer_info.get("email", ""),
    #     "display_order_id": order.display_order_id,
    #     "url": sign_page_url,
    #     "company_name": account.cms_attributes.get("company_name"),
    # }
    await order_crud.update(
        int(account_id),
        order.id,
        OrderInUpdate(
            **{
                "pod_sign_page_url": sign_page_url,
                "account_id": account_id,
            }
        ),
    )

    if account.name.startswith("USA Containers"):
        # email_service.send_payment_on_delivery_contract_mail(email_info)
        await order_crud.updated_contracts_sent(order.id)

    return {"sign_page_url": sign_page_url}


def get_day_with_suffix(day):
    """
    Returns the day with an ordinal suffix.
    """
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}"

