# Python imports
import json
import re
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

# Pip imports
import pytz
import requests
from fastapi import HTTPException, Response
from loguru import logger

# Internal imports
from src.config import settings
from src.controllers import orders as order_controller
from src.crud.tax_crud import tax_crud
from src.database.models.account import Account
from src.database.models.orders.order import Order


# from src.config import settings
AUTHORIZATION_TEMPLATE_NAME: str = "authorization"
AUTHORIZATION_TEMPLATE_WITH_PHOTO_NAME: str = "authorization_w_upload"
STAGE: str = settings.STAGE
CUSTOM_WEBHOOK_BASE_URL: str = ""
CUSTOM_WEBHOOK_URL: str = ""

# you can customize which url you want to be the webhook url. the one on the api dashboard is default
if STAGE.lower() == "dev":
    # Put your ngrok endpoint here to test webhook notifications
    CUSTOM_WEBHOOK_BASE_URL = "https://dev-api.mobilestoragetech.com"
elif STAGE.lower() == "prod":
    CUSTOM_WEBHOOK_BASE_URL = "https://api.mobilestoragetech.com"

# CUSTOM_WEBHOOK_URL = f"https://a605-2600-1700-cc1b-6010-4c63-a41d-d4bb-a0e0.ngrok-free.app/order_contract"
CUSTOM_WEBHOOK_URL = f"{CUSTOM_WEBHOOK_BASE_URL}/order_contract"


def get_contract_start_date(account) -> datetime:
    daysToAdd: int = 0
    currentDate = datetime.today()
    daysToAdd: int = account.cms_attributes.get('rent_options', {}).get('contract_delivery_days', 0)

    if daysToAdd == 0:
        return None

    updatedDate = currentDate + timedelta(days=daysToAdd)
    return updatedDate


def get_day_with_suffix(day):
    """
    Returns the day with an ordinal suffix.
    """
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}"


def validate_phone_number(phone_number):
    pattern = re.compile(r'^\(?([2-9][0-9]{2})\)?[-.\s]?([2-9][0-9]{2})[-.\s]?([0-9]{4})$')
    match = pattern.match(phone_number)
    if match:
        area_code, exchange_code, subscriber_number = match.groups()
        if area_code != "000" and exchange_code != "000":
            return True
    return False


async def get_monthly_owed_amounts(order: Order) -> dict[str, float]:

    delivery_state: str = order.address.state
    account_id: int = order.account_id

    tax_rate: Decimal = await tax_crud.get_tax_rate(account_id=account_id, state=delivery_state)

    monthly_owed: float = float(order.current_rent_period.get("amount_owed", 0))
    monthly_owed_tax: float = float(
        Decimal(Decimal(monthly_owed) * tax_rate).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
    )
    total_monthly_owed: float = float(
        Decimal(monthly_owed + monthly_owed_tax).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
    )

    return_dict: dict[str, Any] = {
        "monthly_owed_tax": monthly_owed_tax,
        "monthly_owed": monthly_owed,
        "total_monthly_owed": total_monthly_owed,
    }
    return return_dict


async def customize_payload(payload: dict[str, Any], account: Account, order: Order) -> dict[str, Any]:
    custom_payload: dict[str, Any] = payload
    monthly_owed_amts_dict: dict[str, float] = await get_monthly_owed_amounts(order)
    account_name: str = account.cms_attributes.get("account_name", "")
    rent_options: dict[str, Any] = account.cms_attributes.get("rent_options", "")

    shipping_price: float = float(order.line_items[0].shipping_revenue)
    total_delivery_and_pickup: float = shipping_price * 2
    date_sent: datetime = datetime.now(tz=pytz.utc)
    day_with_suffix = get_day_with_suffix(date_sent.day)
    tax: float = float(Decimal(order.calculated_order_tax).quantize(Decimal(".01"), rounding=ROUND_HALF_UP))
    total_upfront: float = float(total_delivery_and_pickup + monthly_owed_amts_dict.get("monthly_owed", 0) + tax)
    container_plus_price: float = float(order.calculated_total_price + 800)

    contract_start_date = get_contract_start_date(account) or datetime.now(tz=None)

    cust_full_address: str = f"{order.address.street_address}, {order.address.city}, {order.address.county}, {order.address.state}, {order.address.zip}"

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    if account_name.lower() == "a mobile box":
        custom_payload["signers"] = [
            {
                "name": customer_info.get("full_name", ""),
                "email": customer_info.get("email", ""),
                "mobile": customer_info.get("phone", "")
                if validate_phone_number(customer_info.get("phone", ""))
                else "",
                "signing_order": "1",
                "auto_sign": "no",
                "signature_request_delivery_method": "",  # options are email/sms if left blank, then wont send
                "signed_document_delivery_method": "",  # options are email/sms if left blank, then wont send
                "required_identification_methods": [],
                "redirect_url": "",
            }
        ]
        custom_payload["placeholder_fields"] = [
            {"api_key": "door_type", "value": order.line_items[0].door_orientation},
            {"api_key": "containers_num", "value": len(order.line_items)},
            {"api_key": "container_size", "value": order.line_items[0].container_size},
            {
                "api_key": "container_number",
                "value": order.line_items[0].inventory.container_number if order.line_items[0].inventory else "",
            },
            {"api_key": "start_date", "value": contract_start_date.strftime('%Y-%m-%d')},
            {
                "api_key": "monthly_owed",
                "value": "{:.2f}".format(monthly_owed_amts_dict.get("monthly_owed", 0)),
            },
            {
                "api_key": "monthly_owed_tax",
                "value": "{:.2f}".format(monthly_owed_amts_dict.get("monthly_owed_tax", 0)),
            },
            {"api_key": "shipping_price", "value": "{:.2f}".format(shipping_price)},
            {
                "api_key": "total_delivery_and_pickup",
                "value": "{:.2f}".format(total_delivery_and_pickup),
            },
            {"api_key": "date_sent", "value": date_sent.strftime(f"%B {day_with_suffix}, %Y")},
            {
                "api_key": "customer_phone",
                "value": customer_info.get("phone", ""),
            },
            {"api_key": "tax", "value": "{:.2f}".format(tax)},
            {
                "api_key": "total_upfront",
                "value": "{:.2f}".format(total_upfront),
            },
            {
                "api_key": "total_monthly_owed",
                "value": "{:.2f}".format(monthly_owed_amts_dict.get("total_monthly_owed", 0)),
            },
            {"api_key": "day_of_month_rent", "value": get_day_with_suffix(date_sent.day)},
        ]

        custom_payload["signer_fields"] = [
            {"signer_field_id": "signer_name", "default_value": customer_info.get("full_name", "") or ""},
            {"signer_field_id": "location_address", "default_value": cust_full_address},
            {"signer_field_id": "mailing_address", "default_value": cust_full_address},
        ]

    elif account_name.lower() == "usa containers":
        contract_delivery_days: int = rent_options.get("contract_delivery_days", 30)
        date_sent += timedelta(days=contract_delivery_days)
        agreement_lessor_name: str = (
            rent_options.get("agreement_lessor_name", "Dani Canarin") if STAGE.lower() == "prod" else "Test lessor"
        )
        agreement_lessor_email: str = (
            rent_options.get("rentals_email", "rentals@usacontainers.co")
            if STAGE.lower() == "prod"
            else settings.EMAIL_TO
        )
        agreement_lessor_position: str = (
            rent_options.get("agreement_lessor_position", "Finance & Risk Manager")
            if STAGE.lower() == "prod"
            else "Test Position"
        )
        custom_payload["signers"] = [
            {
                "name": customer_info.get("full_name", ""),
                "email": customer_info.get("email", ""),
                "mobile": customer_info.get("phone", "")
                if validate_phone_number(customer_info.get("phone", ""))
                else "",
                "signing_order": "1",
                "auto_sign": "no",
                "signature_request_delivery_method": "",  # options are email/sms if left blank, then wont send
                "signed_document_delivery_method": "email",  # options are email/sms if left blank, then wont send
                "required_identification_methods": [],
                "redirect_url": "https://pricing.usacontainers.co/#/finished_signing",
            },
            {
                "name": agreement_lessor_name,
                "email": agreement_lessor_email,
                "signing_order": "2",
                "auto_sign": "yes",
                "signature_request_delivery_method": "email",  # options are email/sms if left blank, then wont send
                "signed_document_delivery_method": "email",  # options are email/sms if left blank, then wont send
                "required_identification_methods": [],
                "redirect_url": "",
            },
        ]
        custom_payload["placeholder_fields"] = [
            {"api_key": "order_id", "value": order.display_order_id},
            {
                "api_key": "contract_start_date",
                "value": date_sent.strftime(f"%B {day_with_suffix}, %Y"),
            },  # TODO potentially needing to make this dynamic
            {"api_key": "container_size", "value": order.line_items[0].container_size},
            {"api_key": "container_condition", "value": order.line_items[0].condition},
            {"api_key": "container_quantity", "value": len(order.line_items)},
            {"api_key": "container_price_plus", "value": "{:.2f}".format(container_plus_price)},
            {
                "api_key": "monthly_total",
                "value": "${:.2f}".format(monthly_owed_amts_dict.get("monthly_owed", 0)),
            },
            {
                "api_key": "start_date",
                "value": date_sent.strftime(f"%B {day_with_suffix}, %Y"),  # TODO make this dynamic
            },
            {
                "api_key": "delivery_price",
                "value": "{:.2f}".format(shipping_price),
            },
            {"api_key": "day_of_month_rent", "value": get_day_with_suffix(date_sent.day)},
        ]
        custom_payload["signer_fields"] = [
            {"signer_field_id": "name", "default_value": customer_info.get("full_name", "") or ""},
            {"signer_field_id": "email", "default_value": customer_info.get("email", "")},
            {"signer_field_id": "phone_number", "default_value": customer_info.get("phone", "")},
            {"signer_field_id": "billing_address", "default_value": cust_full_address},
            {"signer_field_id": "delivery_address", "default_value": cust_full_address},
            {"signer_field_id": "lessor_name", "default_value": agreement_lessor_name},
            {"signer_field_id": "lessor_position", "default_value": agreement_lessor_position},
        ]

        custom_payload["emails"] = {
            "final_contract_subject": "Your document is signed",
            "final_contract_text": "Thank you for signing your contract! \n\n Please allow 1 business day to hear from your logistics coordinator with the next steps for delivery. \n\n If you have any delivery questions, please email deliveries@usacontainers.co",
            "cc_email_addresses": [agreement_lessor_email],
            "reply_to": agreement_lessor_email,
        }

    return custom_payload


async def send_rental_agreement(order: Order, account: Account):
    esign_integration = account.integrations.get("esignatures.io", {})
    cms: dict[str, Any] = account.cms_attributes
    rent_options: dict[str, Any] = cms.get("rent_options", {})
    is_demo_emails: bool = rent_options.get("is_demo_emails", True)

    reqUrl = f"https://esignatures.io/api/contracts?token={esign_integration.get('api_key')}"
    headersList = {
        "Accept": "*/*",
        "Content-Type": "application/json",
    }

    selected_template = esign_integration.get("template_id", {}).get(order.type.lower(), {})
    # emails = account.integrations.get("esignatures.io", {}).get("emails", {})

    title: str = f"{order.type} - Agreement, {account.cms_attributes.get('account_name')}"

    payload: dict[str, Any] = {
        "template_id": selected_template,
        "title": title,
        "test": "yes" if is_demo_emails else "no",
        "locale": "en",
        "metadata": str(order.id),
        "expires_in_hours": rent_options.get("contract_expires_in_hours", 120 + 24 * 3),
        "custom_webhook_url": CUSTOM_WEBHOOK_URL,
        "labels": ["MA", "Rental"],
        "custom_branding": {
            "company_name": account.cms_attributes.get("account_name"),
            "logo_url": account.cms_attributes.get("logo_settings", {}).get("logo_url", ""),
        },
    }

    payload = await customize_payload(payload=payload, account=account, order=order)

    json_payload: str = json.dumps(obj=payload)

    response: Response = requests.request(method="POST", url=reqUrl, data=json_payload, headers=headersList)
    logger.info(response.text)
    if int(str(response.status_code)[0]) != 2:
        raise HTTPException(
            status_code=response.status_code, detail="Something went wrong while sending the Rental Application"
        )

    response_dict = json.loads(response.text)
    sign_page_url = response_dict['data']['contract']['signers'][0]['sign_page_url']

    return sign_page_url


async def prepare_authorization_agreement(order: Order, account: Account, with_photo: bool):
    esign_integration = account.integrations.get("esignatures.io", {})

    cms: dict[str, Any] = account.cms_attributes
    rent_options: dict[str, Any] = cms.get("rent_options", {})
    is_demo_emails: bool = rent_options.get("is_demo_emails", True)

    reqUrl = f"https://esignatures.io/api/contracts?token={esign_integration.get('api_key')}"
    headersList = {
        "Accept": "*/*",
        "Content-Type": "application/json",
    }
    if with_photo is not None and with_photo == True:
        selected_template = esign_integration.get("template_id", {}).get(AUTHORIZATION_TEMPLATE_WITH_PHOTO_NAME, {})
    else:
        selected_template = esign_integration.get("template_id", {}).get(AUTHORIZATION_TEMPLATE_NAME, {})
    # emails = account.integrations.get("esignatures.io", {}).get("emails", {})
    links = account.cms_attributes.get("links", {})
    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    monthly_owed_amts_dict: dict[str, float] = await get_monthly_owed_amounts(order)

    contract_start_date = get_contract_start_date(account) or datetime.now(tz=None)

    payload = json.dumps(
        {
            "template_id": selected_template,
            "title": f"{order.display_order_id} - Authorization Form",
            "test": "yes" if is_demo_emails else "no",
            "locale": "en",
            "metadata": str(order.id),
            "expires_in_hours": "48",
            "custom_webhook_url": CUSTOM_WEBHOOK_URL,
            "labels": ["MA", "Rental"],
            "signers": [
                {
                    "name": customer_info.get("full_name", ""),
                    "email": customer_info.get("email", ""),
                    "mobile": customer_info.get("phone", "")
                    if validate_phone_number(customer_info.get("phone", ""))
                    else "",
                    "signing_order": "1",
                    "auto_sign": "no",
                    "signature_request_delivery_method": "",  # options are email/sms/blank. if left blank, then wont send
                    "signed_document_delivery_method": "",  # options are email/sms/blank. if left blank, then wont send
                    "required_identification_methods": [],
                    "redirect_url": "",
                }
            ],
            "placeholder_fields": [
                {"api_key": "total_price", "value": monthly_owed_amts_dict.get("total_monthly_owed", 0)},
                {"api_key": "current_date", "value": contract_start_date.strftime('%Y-%m-%d')},
                {"api_key": "upload_url", "value": f"{links.get('invoice_email_link', '')}{order.id}"},
                {"api_key": "order_type", "value": order.type},
            ],
            "signer_fields": [
                {"signer_field_id": "billing_address", "default_value": order.address.street_address},
                {
                    "signer_field_id": "phone_number",
                    "default_value": customer_info.get("phone", ""),
                },
                {"signer_field_id": "city", "default_value": order.address.city},
                {"signer_field_id": "state", "default_value": order.address.state},
                {"signer_field_id": "zip", "default_value": order.address.zip},
                {
                    "signer_field_id": "email",
                    "default_value": customer_info.get("email", ""),
                },
            ],
            "custom_branding": {
                "company_name": account.cms_attributes.get("account_name"),
                "logo_url": account.cms_attributes.get("logo_settings", {}).get("logo_url", ""),
            },
        }
    )

    response = requests.request("POST", reqUrl, data=payload, headers=headersList)

    logger.info(response.text)

    response_dict = json.loads(response.text)

    sign_page_url = response_dict['data']['contract']['signers'][0]['sign_page_url']

    return sign_page_url


async def send_payment_on_delivery_contract(order: Order, account: Account):
    esign_integration = account.integrations.get("esignatures.io", {})

    cms: dict[str, Any] = account.cms_attributes
    pay_on_delivery_options: dict[str, Any] = cms.get("pay_on_delivery_contract", {})
    is_prod: bool = pay_on_delivery_options.get("is_prod", False)
    convenience_percentage = cms.get("convenience_fee_rate", 0)

    reqUrl = f"https://esignatures.io/api/contracts?token={esign_integration.get('api_key')}"
    headersList = {
        "Accept": "*/*",
        "Content-Type": "application/json",
    }

    # selected_template = esign_integration.get("template_id", {}).get(AUTHORIZATION_TEMPLATE_NAME, {})
    # emails = account.integrations.get("esignatures.io", {}).get("emails", {})

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    # monthly_owed_amts_dict: dict[str, float] = await get_monthly_owed_amounts(order)

    contract_start_date = datetime.now(tz=None)
    cust_full_address: str = f"{order.address.street_address}, {order.address.city}, {order.address.county}, {order.address.state}, {order.address.zip}"
    total_bank_fees = round(
        ((order.calculated_sub_total_price + order.calculated_order_tax) * Decimal(convenience_percentage)), 2
    )

    payload = json.dumps(
        {
            "template_id": esign_integration.get('template_id', {}).get("pod"),
            "title": f"{order.display_order_id} - Pay On Delivery Contract",
            "test": "no" if is_prod else "yes",
            "locale": "en",
            "metadata": str(order.id),
            "expires_in_hours": "48",
            "custom_webhook_url": CUSTOM_WEBHOOK_URL,
            "labels": ["MA", "Rental", "PayOnDelivery"],
            "signers": [
                {
                    "name": customer_info.get("full_name", ""),
                    "email": customer_info.get("email", ""),
                    "mobile": customer_info.get("phone", "")
                    if validate_phone_number(customer_info.get("phone", ""))
                    else "",
                    "signing_order": "1",
                    "auto_sign": "no",
                    "signature_request_delivery_method": "",  # options are email/sms/blank. if left blank, then wont send
                    "signed_document_delivery_method": "",  # options are email/sms/blank. if left blank, then wont send
                    "required_identification_methods": [],
                    "redirect_url": "",
                }
            ],
            "placeholder_fields": [
                {"api_key": "date", "value": contract_start_date.strftime('%Y-%m-%d')},
                {"api_key": "customer-name", "value": customer_info.get("full_name", "")},
                {"api_key": "delivery-address", "value": cust_full_address},
                {"api_key": "invoice-number", "value": order.display_order_id},
                {
                    "api_key": "invoice-price-with-card",
                    "value": str(
                        format(order.calculated_sub_total_price + order.calculated_order_tax + total_bank_fees, ".2f")
                    ),
                },
                {
                    "api_key": "invoice-price",
                    "value": str(order.calculated_sub_total_price + order.calculated_order_tax),
                },
                {"api_key": "container-quantity", "value": str(order.calculated_abreviated_line_items_title)},
                {"api_key": "printed-name", "value": ""},
                {"api_key": "phone-number", "value": ""},
                {"api_key": "email-address", "value": ""},
                {"api_key": "date-signed", "value": ""},
            ],
            "signer_fields": [
                {"signer_field_id": "billing_address", "default_value": order.address.street_address},
                {
                    "signer_field_id": "phone_number",
                    "default_value": customer_info.get("phone", ""),
                },
                {
                    "signer_field_id": "printed_name",
                    "default_value": customer_info.get("full_name", ""),
                },
                {
                    "signer_field_id": "printed_number",
                    "default_value": customer_info.get("phone", ""),
                },
                {
                    "signer_field_id": "printed_email",
                    "default_value": customer_info.get("email", ""),
                },
                {
                    "signer_field_id": "printed_date",
                    "default_value": contract_start_date.strftime('%Y-%m-%d'),
                },
                {"signer_field_id": "city", "default_value": order.address.city},
                {"signer_field_id": "state", "default_value": order.address.state},
                {"signer_field_id": "zip", "default_value": order.address.zip},
                {
                    "signer_field_id": "email",
                    "default_value": customer_info.get("email", ""),
                },
            ],
            "emails": {"cc_email_addresses": ["cod@usacontainers.co"], "reply_to": "cod@usacontainers.co"},
            "custom_branding": {
                "company_name": account.cms_attributes.get("account_name"),
                "logo_url": account.cms_attributes.get("logo_settings", {}).get("logo_url", ""),
            },
        }
    )

    response = requests.request("POST", reqUrl, data=payload, headers=headersList)

    logger.info(response.text)

    response_dict = json.loads(response.text)

    sign_page_url = response_dict['data']['contract']['signers'][0]['sign_page_url']
    logger.info(sign_page_url)

    return sign_page_url
