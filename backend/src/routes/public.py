# Python imports
import base64
import hashlib
import json
import os
import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

# Pip imports
import requests
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status, File, UploadFile
from loguru import logger
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist
import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api
from cloudinary.uploader import upload

# Internal imports
from src.controllers import account as account_controller
from src.controllers import contracts as contract_controller
from src.controllers import coupon_code as coupon_controller
from src.controllers import coupon_code_order as coupon_order_controller
from src.controllers import customer_application, file_upload, notifications_controller
from src.controllers import orders as order_controller
from src.controllers import payment as payment_controller
from src.controllers import rent_period as rent_period_controller
from src.controllers.customers import (
    get_order_id,
    handle_initial_subtotal_balance,
    handle_initial_tax_balance,
    save_customer,
    save_line_item,
)
from src.controllers.event_controller import invoice_created_event, order_paid_agent_notification
from src.crud.account_crud import account_crud
from src.crud.container_product_crud import container_product_crud
from src.crud.line_item_crud import line_item_crud
from src.crud.location_price_crud import location_price_crud
from src.crud.order_crud import OrderCRUD
from src.crud.order_tax_crud import order_tax_crud
from src.crud.other_product_crud import other_product_crud
from src.crud.tax_crud import tax_crud
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.crud.total_order_balance_crud import total_order_balance_crud
from src.crud.user_crud import UserCRUD
from src.database.models.note import Note

# from src.redis import limiter
from src.schemas.coupon_code import CouponCodeInsecureOut
from src.schemas.coupon_code_order import CouponCodeOrderIn
from src.schemas.customer import CreateCustomerOrder, CustomerOut
from src.schemas.customer_application import CreateUpdateCustomerApplicationResponse
from src.schemas.file_upload import (
    CreateFileUpload,
    FileUpdateInSchema,
    FileUploadInSchema,
    FileUploadOutSchema,
    PresignedUrlInfo,
)
from src.schemas.line_items import LineItemOut
from src.schemas.location_distances import CreateLocationDistances, LocationDistancesIn, LocationDistancesOut
from src.schemas.notes import NoteInSchema, NoteOutSchema, UpdateNote
from src.schemas.order_tax import OrderTaxIn
from src.schemas.orders import CreateOrder, Order, OrderIn, OrderInUpdate, OrderOut, PublicOrderOut, UpdateOrder
from src.schemas.payment import Payment
from src.schemas.tax import AvalaraTaxItem, TaxOutSchema
from src.schemas.total_order_balance import TotalOrderBalanceIn
from src.services.notifications import email_service, email_service_mailersend
from src.services.orders.address import save_address
from src.services.payment.authorize_pay_service import charge_credit_card as authorize_charge_credit_card
from src.services.payment.stripe_service import create_payment_intent, transaction_status, webhook_received
from src.services.payment.usa_epay_service import charge_credit_card as usa_epay_charge_credit_card
from src.utils.generate_processing_cost import generate_processing_cost_options

from ..crud.customer_crud import CustomerCRUD
from ..crud.location_distance_crud import LocationDistanceCRUD


BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")

order_crud = OrderCRUD()
customer_crud = CustomerCRUD()
user_crud = UserCRUD()
location_distances_crud = LocationDistanceCRUD()


note_crud = TortoiseCRUD(
    schema=NoteOutSchema,
    create_schema=NoteInSchema,
    update_schema=UpdateNote,
    db_model=Note,
)

router = APIRouter(
    tags=["public"],
    prefix="/public",
)


class PostToPublishReports(BaseModel):
    name: str
    run_by: str
    begin_date: str
    end_date: str
    account_id: str


class StripePaymentIntent(BaseModel):
    amount: int
    order_id: str
    account_id: int


def convert_non_uuid_to_uuid(value):
    if value:
        m = hashlib.md5()
        m.update(str(value).encode("utf-8"))
        return str(uuid.UUID(m.hexdigest()))


async def save_location_distance(location_distance):
    location_distance_dict = location_distance.dict(exclude_unset=True)
    saved_location_distance = await location_distances_crud.create(LocationDistancesIn(**location_distance_dict))
    return saved_location_distance


@router.get(
    "/warmer/",
)
async def get_warmer():
    return "warm"


class MatrixRequest(BaseModel):
    origins: List[str]
    destinations: List[str]


@router.get(
    "/location_distance/{location_distance_id}",
    response_model=List[LocationDistancesOut],
)
async def get_location_distances(location_distance_id: str):
    return await location_distances_crud.get_by_origin_zip(location_distance_id)


@router.post(
    "/location_distance",
    response_model=LocationDistancesOut,
)
async def create_location_distance(location_distance: CreateLocationDistances):
    return await save_location_distance(location_distance)


@router.get(
    "/tomtom/{encoded_query}",
)
async def get_tomtom_geonames(encoded_query: str):
    r = requests.get(f'https://api.tomtom.com/search/2/geocode/{encoded_query}.json?key=')

    if r.status_code == 200:
        return r.json()
    else:
        r = requests.get(f'https://api.tomtom.com/search/2/geocode/{encoded_query}.json?key=')
        return r.json()


async def save_order(order, existing_order, order_id=None):
    order_dict = order.dict(exclude_unset=True)
    order_dict["account_id"] = existing_order.account_id

    if not order_dict.get("user_id"):
        order_dict["user_id"] = existing_order.user.id

    if order_id:
        saved_order = await order_crud.update(existing_order.account_id, order_id, OrderInUpdate(**order_dict))
    else:
        account = await account_crud.get_one(existing_order.account_id)
        account_requires_cc_application = account.cms_attributes.get("applications", {}).get("credit_card", False)
        applications_override = None
        if account_requires_cc_application:
            applications_override = [{"name": "credit_card", "overridden": False}]
        else:
            applications_override = [{"name": "credit_card", "overridden": True}]
        order_dict["applications_overridden"] = applications_override
        saved_order = await order_crud.create(OrderIn(**order_dict))

    return saved_order


def validate_email(email):
    if not email or not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email.strip()):
        return {
            "statusCode": 200,
            "body": json.dumps({"error": "invalid customer email {}".format(email)}),
        }


@router.get("/user/{user_id}/{account_id}", response_model=dict)
async def get_user(user_id: str, account_id: int) -> dict:
    user = await user_crud.get_one(account_id, user_id)
    if user is not None:
        return {
            "phone": user.phone,
            "full_name": user.display_name,
        }
    raise Exception("User not found")


@router.get(
    "/prices/{account_id}",
)
async def get_public_prices(account_id: str):
    return await container_product_crud.get_all(account_id)


@router.get(
    "/products/{account_id}",
)
async def get_public_products(account_id: str):
    return await other_product_crud.get_all(account_id)


@router.get(
    "/locations/{account_id}",
)
async def get_public_locations(account_id: str):
    return await location_price_crud.get_all(account_id)


@router.get(
    "/taxes/{account_id}",
    response_model=List[TaxOutSchema],
)
async def get_container_taxes_public(account_id: str):
    return await tax_crud.get_all(account_id)


@router.get("/coupon/code/{account_id}/{coupon_code}")
async def get_coupon_by_code(account_id: int, coupon_code: str):
    return await coupon_controller.get_public_coupon_by_code(coupon_code, account_id)


@router.post("/coupon/remove", responses={404: {"model": HTTPNotFoundError}})
async def remove_coupon(coupon: CouponCodeOrderIn, background_tasks: BackgroundTasks) -> None:
    return await coupon_order_controller.remove_coupon(coupon, background_tasks)


@router.get(
    "/taxes/has_avalara_integration/{account_id}",
)
async def has_avalara_integration(account_id: str):
    account = await account_controller.get_account_by_id(account_id)
    avalara_int = account.integrations.get("avalara", {})

    if avalara_int:
        return True
    return False


@router.post(
    "/taxes/avalara/{account_id}",
)
async def get_tax_rate(account_id: str, avalara_item: AvalaraTaxItem):
    account = await account_controller.get_account_by_id(account_id)
    avalara_int = account.integrations.get("avalara", {})

    if avalara_int:
        avalara_api_url = avalara_int.get("url")
        username = avalara_int.get("account")
        password = avalara_int.get("license_key")
        now = datetime.now()

        formatted_date = now.strftime("%Y-%m-%d")

        loc = await location_price_crud.get_by_city(avalara_item.container_city, account_id)

        transaction = {
            "type": "SalesOrder",
            "companyCode": "DEFAULT",
            "date": formatted_date,
            "customerCode": "ABC",
            "addresses": {
                "shipFrom": {
                    "line1": "",
                    "city": avalara_item.container_city,
                    "region": avalara_item.container_state,
                    "country": "US",
                    "postalCode": loc.zip,
                },
                "shipTo": {
                    "line1": "",
                    "city": "",
                    "region": "",
                    "country": "US",
                    "postalCode": avalara_item.customer_zip,
                },
            },
            "lines": [{"number": "1", "quantity": 1, "amount": 100, "taxCode": "P0000000"}],
        }

        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        response = requests.post(
            avalara_api_url,
            headers={"Content-Type": "application/json", "Authorization": "Basic " + encoded_credentials},
            data=json.dumps(transaction),
        )

        if response.status_code == 201:
            transaction_data = response.json()
            total_tax = transaction_data['totalTax']
            total_amount = transaction_data['totalAmount']
            tax_rate = (total_tax / total_amount) if total_amount != 0 else 0

            return tax_rate
        else:
            raise Exception(f"Can't calculate order tax rate from avalara: {response.text}")
    return -1


@router.post(
    "/esignatures",
)
async def handle_esignatures_hook(request):
    if request.status == 'contract-signed':
        singed_data = request.data.contract
        order_id = request.data.metadata
        order = await order_crud.get_one(order_id)
        order = await order_crud.update(order_id, OrderInUpdate(**{"status": "DOCS_SIGNED"}))
        logger.info(order)
        logger.info(singed_data)


@router.post(
    "/google_maps",
)
async def get_directions_matrix(matrixRequest: MatrixRequest):
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": matrixRequest.origins,
            "destinations": '|'.join(matrixRequest.destinations),
            "units": "imperial",
            "key": "",
            "travelMode": "DRIVING",
        }

        response = requests.request("GET", url, params=params)
        google_response = response.json()
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

    return google_response


@router.get(
    "/order/{order_id}",
)
async def get_order_by_id(order_id: str):
    try:
        logger.info(order_id)
        order = await order_crud.get_one(order_id, is_public=True)
        if order.is_archived:
            raise HTTPException(
                status_code=404,
                detail="Order does not exist",
            )
        return order
    except Exception as e:
        logger.info(e)
        try:
            converted_order_id = convert_non_uuid_to_uuid(order_id)
            logger.info(converted_order_id)
            return await order_crud.get_one(converted_order_id, is_public=True)
        except DoesNotExist:
            raise HTTPException(
                status_code=404,
                detail="Order does not exist",
            )


@router.get(
    "/get_delivery_days/{account_id}",
)
async def get_delivery_days(account_id: str, city: str):
    try:
        loc = await location_price_crud.get_by_city(city, account_id)
        return {"delivery_days": loc.average_delivery_days}
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Line item does not exist",
        )


@router.post(
    "/customer/{account_id}",
    response_model=CustomerOut,
)
async def create_customer(
    customer: CreateCustomerOrder, account_id: str, background_tasks: BackgroundTasks, user_id: str = None
):
    order: CreateOrder = getattr(customer, 'order', None)
    line_items = getattr(order, 'line_items', None)
    order_address = getattr(order, 'address', None)
    account = await account_crud.get_one(account_id)

    saved_address = await save_address(order_address)

    try:
        existing_customer = await customer_crud.get_by_email(account_id, customer.email)
        saved_customer = await save_customer(customer, account_id, existing_customer.id)
    except Exception:
        saved_customer = await save_customer(customer, account_id)
        logger.info("Customer exists already, carry on creating their order")

    if not user_id:
        # set default user
        if account.cms_attributes.get('default_public_agent'):
            user = await user_crud.get_by_email(account_id, account.cms_attributes.get('default_public_agent'))
            user_id = user.id
        else:
            user = await user_crud.get_by_first_created(account_id)
            user_id = user.id

    lookup_order_for_id = await get_order_id(account)

    found_id = False
    while not found_id:
        try:
            await order_crud.get_one_by_display_id(account_id, lookup_order_for_id)
        except Exception as e:
            logger.info(e)
            logger.info(type(e))
            found_id = True
            logger.info("id doesn't exist, proceed")
        else:
            lookup_order_for_id = await get_order_id(account)
            found_id = False

    credit_card_fee = account.cms_attributes.get('credit_card_fees', {}).get('is_rent_credit_card_fee_enabled', True)
    if order.type == 'PURCHASE' or order.type == 'PURCHASE_ACCESSORY':
        credit_card_fee = account.cms_attributes.get('credit_card_fees', {}).get(
            'is_purchase_credit_card_fee_enabled', True
        )
    elif order.type == 'RENT_TO_OWN':
        credit_card_fee = account.cms_attributes.get('credit_card_fees', {}).get(
            'is_rent_to_own_credit_card_fee_enabled', True
        )

    flat_rates_enabled = account.cms_attributes.get("processing_costs", {}).get("flat_rates_enabled", False)
    percentage_rates_enabled = account.cms_attributes.get("processing_costs", {}).get("percentage_rates_enabled", False)

    (
        flat_rates_enabled,
        percentage_rates_enabled,
        processing_flat_cost,
        processing_percentage_cost,
        charge_per_line_item,
    ) = generate_processing_cost_options(account, order)

    if flat_rates_enabled or percentage_rates_enabled:
        credit_card_fee = False
    account_requires_cc_application = account.cms_attributes.get("applications", {}).get("credit_card", False)
    account_requires_rent_application = account.cms_attributes.get("applications", {}).get("rent", False)
    applications_override = None
    if account_requires_cc_application:
        applications_override = [{"name": "credit_card", "overridden": False}]
    else:
        applications_override = [{"name": "credit_card", "overridden": True}]
    if account_requires_rent_application:
        applications_override.append({"name": "rent", "overridden": False})
    else:
        applications_override.append({"name": "rent", "overridden": True})

    order_db = OrderIn(
        status=order.status,
        account_id=account_id,
        customer_id=saved_customer.id,
        display_order_id=lookup_order_for_id,
        type=order.type,
        address_id=saved_address.id,
        attributes=order.attributes,
        user_id=user_id,
        campaign_url=order.campaign_url,
        referral_source=order.referral_source,
        processing_flat_cost=processing_flat_cost,
        processing_percentage_cost=processing_percentage_cost,
        charge_per_line_item=charge_per_line_item,
        credit_card_fee=credit_card_fee,
        applications_overridden=applications_override,
    )
    if order:
        saved_order: Order = await order_crud.create(order_db)
        if line_items:
            [await save_line_item(line_item, account_id, saved_order.id) for line_item in line_items]
    new_tax_amt: Decimal = order.tax
    # tax is already calculated in the remaining balance when it is sent up, so do not need to add tax to it
    new_remaining_balance: Decimal = order.remaining_balance

    create_order_tax: OrderTaxIn = OrderTaxIn(tax_amount=new_tax_amt, order_id=saved_order.id)
    await order_tax_crud.create(create_order_tax)
    create_order_balance: TotalOrderBalanceIn = TotalOrderBalanceIn(
        remaining_balance=new_remaining_balance, order_id=saved_order.id
    )
    await total_order_balance_crud.create(create_order_balance)

    if saved_order.type != "RENT":
        existing_order = await order_crud.get_one(saved_order.id)
        await handle_initial_subtotal_balance(existing_order, account, False)
        tax_rate = Decimal(new_tax_amt) / Decimal(existing_order.calculated_sub_total_without_fees)
        await handle_initial_tax_balance(existing_order, account, False, tax_rate)

    if saved_order.type == "RENT":

        account = await account_controller.get_account_by_id(account_id)
        rent_options: dict = account.cms_attributes.get("rent_options", {})
        await rent_period_controller.handle_initial_rent_period(saved_order.id, None, rent_options)

    created_customer = await customer_crud.get_latest(account_id, saved_customer.id)
    customer_dict = created_customer.dict()
    email_dict = customer_dict["order"][0]
    email_dict["customer_email"] = customer_dict["email"]
    # email_dict["url"] = f"{BASE_WEB_URL}/#/payment/{email_dict['id']}"
    email_dict["url"] = f"{BASE_INVOICE_URL}/#/{email_dict['id']}"
    account = await account_crud.get_one(account_id)
    email_dict["company_name"] = account.name
    email_dict["account_id"] = account_id

    if account.cms_attributes.get('send_public_notifiction') is not None and account.cms_attributes.get(
        'send_public_notifiction'
    ):
        links = account.cms_attributes.get("links", {})
        email_dict['mail_to'] = account.cms_attributes.get('quote_contact_email')
        email_dict["url"] = f"{links.get('invoice_email_link', '')}{email_dict['id']}"
        email_service.send_public_notifiction(email_dict)
        email_dict["company_name"] = account.cms_attributes.get('account_name')

    if not account.name.startswith("USA Containers"):
        # TODO :  Hard coded url for now
        email_dict["url"] = f"{account.cms_attributes.get('links',{}).get('invoice_email_link','')}{email_dict['id']}"
        await email_service_mailersend.send_customer_invoice_email(email_dict)
    else:
        email_text = f"You just had a customer place an order! Order #{saved_order.display_order_id}"
        if account.cms_attributes.get("sendInternalAgentEmails", True):
            email_service.send_agent_email(email_text, await order_controller.get_agent_emails(saved_order))
        await invoice_created_event(saved_order, customer_dict, saved_order.created_at, background_tasks)
        # email_service.send_customer_invoice_email(email_dict)

    return created_customer


@router.get(
    "/account/{account_id}",
)
async def get_cms(account_id: str):
    account = await account_crud.get_one(account_id)
    attributes = account.cms_attributes
    # check if stripe is enabled
    attributes["stripe_enabled"] = account.cms_attributes.get("stripe", {}).get("enabled", False)
    attributes.pop("delivered_sms_text", None)
    attributes.pop("sms_follow_up_text", None)
    attributes.pop("pickup_email", None)
    attributes.pop("sales_internal_link1", None)
    attributes.pop("sales_internal_link2", None)
    attributes.pop("sales_internal_link1_desc", None)
    attributes.pop("sales_internal_link2_desc", None)
    attributes.pop("sales_quotes_message", None)
    attributes.pop("nav_item_link", None)
    attributes.pop("nav_item_name", None)
    attributes.pop("agent_guide_link", None)
    attributes.pop("auth", None)
    attributes.pop("sms_text_messages", None)
    attributes.pop("emails", None)

    # attributes.pop("rent_to_own_rates", None)
    attributes.pop("order_status_options", None)
    attributes.pop("container_colors", None)
    attributes.pop("inventory_status_options", None)
    attributes.pop("inventory_status_list", None)
    attributes.pop("role_commissions", None)

    return attributes


@router.patch(
    "/order/{order_id}",
    response_model=OrderOut,
)
async def update_customer(order_id: str, order: UpdateOrder):
    exisiting_order = await order_crud.get_one(order_id)
    return await save_order(order, exisiting_order, order_id)


def subTotalNoFee(item):
    # return Decimal(item.revenue or 0) + Decimal(item.shipping_revenue or 0) + Decimal(item.tax or 0)
    return Decimal(item.revenue or 0) + Decimal(item.shipping_revenue or 0)


def calculateTotal(i, fee_percentage):
    return subTotalNoFee(i) * (Decimal(fee_percentage) + 1)


def calculateFee(i, fee_percentage):
    return subTotalNoFee(i) * round((Decimal(fee_percentage)), 4)


def charge_card(account, payment_info, new_balance):
    usa_epay_int = account.integrations.get("usa_epay", {})
    authorize_int_purchase = account.integrations.get("authorize", {}).get("purchase", {})
    credit_card_response = {}
    if new_balance >= 0:
        if authorize_int_purchase.get("in_use"):
            credit_card_response = authorize_charge_credit_card(
                payment_info,
                live_name=authorize_int_purchase.get("api_login_id"),
                live_trans_key=authorize_int_purchase.get("transaction_key"),
                url=authorize_int_purchase.get("url"),
            )
        if usa_epay_int.get("in_use"):
            credit_card_response = usa_epay_charge_credit_card(payment_info, usa_epay_int["api_key"])
    else:
        if authorize_int_purchase.get("in_use"):
            credit_card_response = authorize_charge_credit_card(
                payment_info,
                live_name=authorize_int_purchase.get("api_login_id"),
                live_trans_key=authorize_int_purchase.get("transaction_key"),
                url=authorize_int_purchase.get("url"),
            )
        if usa_epay_int.get("in_use"):
            credit_card_response = usa_epay_charge_credit_card(payment_info, usa_epay_int["api_key"])
    return credit_card_response


async def send_payment_emails(updated_order):
    updated_order_d = updated_order.dict()
    if not updated_order.is_pickup:
        notifications_controller.send_paid_email(updated_order_d)
        email_service.send_customer_general_receipt_email(updated_order_d)

    email_text = "You just had a customer just pay via Credit Card. Order #{}".format(
        updated_order_d["display_order_id"]
    )

    order_user = await user_crud.get_one(updated_order_d['account_id'], updated_order_d["user"]['id'])
    account = await account_crud.get_one(updated_order_d['account_id'])
    emails = [order_user.assistant.manager.email, order_user.email] if order_user.assistant else [order_user.email]
    if account.cms_attributes.get("sendInternalAgentEmails", True):
        external_integrations = account.external_integrations
        if (
            external_integrations is not None
            and external_integrations.get("resources") is not None
            and len(external_integrations.get("resources")) > 0
            and len(
                [
                    res
                    for res in external_integrations.get("resources")
                    if "update:user:paid_at" in res.get("event_types")
                ]
            )
            > 0
        ):
            await order_paid_agent_notification(
                updated_order.display_order_id,
                False if updated_order.signed_at is None else True,
                account.id,
                await order_controller.get_agent(updated_order),
                updated_order,
                emails,
                None,
            )
        else:
            email_service.send_agent_email(email_text, emails)


@router.post(
    "/payment",
)
async def credit_card_payment(payment_request: Payment, background_tasks: BackgroundTasks):
    return await payment_controller.credit_card_payment_purchase_public(payment_request, background_tasks)


@router.get("/coupons", response_model=List[CouponCodeInsecureOut])
async def get_coupons(account_id: str):
    return await coupon_controller.get_all_coupons_insecure(account_id)


@router.post("/generate_presigned_post_url", response_model=PresignedUrlInfo, status_code=status.HTTP_200_OK)
async def generate_presigned_post_url(file_data: CreateFileUpload, request: Request) -> PresignedUrlInfo:
    # client_ip = request.client.host
    # ttl: int = 60  # time to live in seconds
    # limit_per_ttl: int = 5  # number of calls that will be allowed per {ttl} seconds

    # res = limiter(client_ip,limit_per_ttl, ttl)
    res = {"call": True, "ttl": 0}
    if res["call"]:
        return await file_upload.generate_presigned_post_url(file_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"message": "call limit reached", "ttl": res["ttl"]}
        )


@router.post("/db_upload_file", response_model=FileUploadOutSchema, status_code=status.HTTP_201_CREATED)
async def db_upload_file(s3_file_data: FileUploadInSchema) -> FileUploadOutSchema:
    return await file_upload.create_file_upload(s3_file_data)


@router.patch("/db_upload_file/{id}", response_model=FileUploadOutSchema, status_code=status.HTTP_201_CREATED)
async def db_update_file(s3_file_data: FileUpdateInSchema, id: str) -> FileUploadOutSchema:
    return await file_upload.update_file_upload(id, s3_file_data)


@router.delete("/db_delete_file/{file_id}/{account_id}", status_code=status.HTTP_201_CREATED)
async def db_delete_file(file_id: str, account_id: int):
    return await file_upload.delete_file_upload(file_id, account_id)


@router.patch("/accept_quote/{order_id}", status_code=status.HTTP_201_CREATED)
async def accept_quote(order_id: str) -> OrderOut:
    update_order = UpdateOrder(status="Invoiced")
    return await order_controller.accept_order_public(order_id, update_order)


@router.post("/customer_application", response_model=PublicOrderOut, status_code=status.HTTP_201_CREATED)
async def create_customer_app_response(app: CreateUpdateCustomerApplicationResponse) -> PublicOrderOut:
    return await customer_application.create_customer_app_response(app)


@router.post("/google_analytics")
async def send_post_to_google_analytics(data: Dict):
    measurementId = ""
    apiSecret = ""
    r = requests.post(
        f"https://www.google-analytics.com/mp/collect?measurement_id={measurementId}&api_secret={apiSecret}", data=data
    )
    if r.status_code == 204:
        return {"status": "success"}
    else:
        raise Exception("Post to google analytics failed.")


@router.post("/report")
async def generate_report(data: PostToPublishReports):
    API_GATEWAY_URL = "https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/your-stage"
    url = f"{API_GATEWAY_URL}/report?name={data.name}&run_by={data.run_by}&begin_date={data.begin_date}&end_date={data.end_date}&account_id={data.account_id}"
    API_KEY = "YOUR_API_KEY"
    headers = {"x-api-key": API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return {"message": "Data sent to Publish Reports successfully"}
    else:
        return {"error": "Failed to send data to Publish Reports"}


@router.get("/line_item/{account_id}/{line_item_id}", response_model=LineItemOut)
async def get_line_item(account_id: str, line_item_id: str) -> LineItemOut:
    return await line_item_crud.get_one(int(account_id), line_item_id)


@router.get("/send_rental_contract/{order_id}")
async def send_rental_contract(order_id: str) -> Dict[str, str]:
    return await contract_controller.fetch_rental_contract(order_id)


@router.post(
    "/init_stripe_payment",
)
async def create_payment(data: StripePaymentIntent):
    return await create_payment_intent(data.account_id, data.order_id, data.amount)


@router.post(
    "/stripe_webhook/{account_id}",
)
async def stripe_webhook(account_id: int, request: Request, backround_tasks: BackgroundTasks):
    return await webhook_received(account_id, await request.body(), backround_tasks)


@router.get(
    "/stripe_transaction_status/{order_token}/{payment_intent}/{account_id}",
)
async def check_transaction_status(
    order_token: str, payment_intent: str, account_id, background_tasks: BackgroundTasks
):
    return await transaction_status(order_token, payment_intent, account_id, background_tasks)


@router.get("/contracts/send_payment_on_delivery_contract_from_payment/{order_id}")
async def payment_on_delivery_contract_from_payment(order_id: str) -> Dict[str, str]:
    return await contract_controller.send_email_contract_from_payment(order_id)


@router.post("/contracts/sign_payment_on_delivery_contract_from_payment/{order_id}")
async def sign_payment_on_delivery_contract_from_payment(
    order_id: str, app: CreateUpdateCustomerApplicationResponse, background_tasks: BackgroundTasks
):
    return await contract_controller.sign_pod_contract_from_payment(order_id, app, background_tasks)


@router.post("/endpoint")
async def endpoint(data: Dict[Any, Any]):
    logger.info(data)


@router.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):

    uploaded_files = []
    account = await account_crud.get_one(1)
    cloudinary_config = account.integrations.get("cloudinary", {})

    cloudinary.config(
        cloud_name=cloudinary_config.get('cloud_name'),
        api_key=cloudinary_config.get('api_key'),
        api_secret=cloudinary_config.get('api_secret'),
    )
    for file in files:

        # Read file content
        content = await file.read()

        upload_result = upload(
            content,
            folder="inventory",
            resource_type="auto",
            public_id=file.filename.split('.')[0],
        )

        uploaded_files.append(
            {
                "filename": file.filename,
                "url": upload_result["secure_url"],
                "public_id": upload_result["public_id"],
                "resource_type": upload_result["resource_type"],
            }
        )

    return {"status": "success", "files": uploaded_files}
