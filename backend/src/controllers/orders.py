# Python imports
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

# Pip imports
from fastapi import BackgroundTasks, HTTPException, status
from loguru import logger
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic
from twilio.rest import Client

# Internal imports
import redis
from src.auth.auth import Auth0User
from src.config import settings
from src.controllers import notifications_controller
from src.controllers import order_fee_balance as order_fee_balance_controller
from src.controllers import order_tax
from src.controllers import rent_period as rent_period_controller
from src.controllers import subtotal_balance as subtotal_balance_controller
from src.controllers import tax_balance as tax_balance_controller
from src.controllers.customers import (
    get_order_id,
    handle_initial_order_balance,
    handle_initial_subtotal_balance,
    handle_order_tax,
)
from src.controllers.event_controller import (
    accessory_invoice_created_event,
    completed_at_event,
    invoice_created_event,
    order_paid_agent_notification,
    order_pod_signed_agent_notification,
    rental_period_invoice_event,
    send_event,
)
from src.crud._types import PAGINATION
from src.crud.account_crud import account_crud
from src.crud.container_inventory_crud import container_inventory_crud
from src.crud.coupon_code_order_crud import coupon_code_order_crud
from src.crud.customer_app_response import customer_app_response_crud
from src.crud.customer_contact_crud import customer_contact_crud
from src.crud.customer_crud import customer_crud
from src.crud.exported_order_crud import exported_order_crud
from src.crud.fee_crud import fee_crud
from src.crud.file_upload_crud import file_upload_crud
from src.crud.line_item_crud import line_item_crud
from src.crud.location_price_crud import location_price_crud
from src.crud.misc_cost import misc_cost_crud
from src.crud.note_crud import note_crud
from src.crud.order_card_info_crud import order_credit_card_crud
from src.crud.order_contract_crud import order_contract_crud
from src.crud.order_crud import OrderCRUD
from src.crud.order_fee_balance_crud import order_fee_balance_crud
from src.crud.order_tax_crud import order_tax_crud
from src.crud.other_inventory_crud import other_inventory_crud
from src.crud.other_product_crud import other_product_crud
from src.crud.partial_order_crud import partial_order_crud
from src.crud.rent_period_crud import rent_period_crud
from src.crud.rental_history_crud import rental_history_crud
from src.crud.single_customer_crud import single_customer_crud
from src.crud.subtotal_balance_crud import subtotal_balance_crud
from src.crud.tax_balance_crud import tax_balance_crud
from src.crud.total_order_balance_crud import total_order_balance_crud
from src.crud.transaction_type_crud import transaction_type_crud
from src.crud.user_crud import UserCRUD
from src.database.models.customer.old_customer import Customer
from src.database.models.customer.order_customer import OrderCustomer
from src.database.models.orders.order import Order
from src.database.models.rent_period import RentPeriod
from src.schemas.acccessory_line_items import CreateAccessoryLineItem
from src.schemas.line_items import LineItemIn, LineItemOut
from src.schemas.notes import NoteInSchema
from src.schemas.order_fee_balance import OrderFeeBalanceIn
from src.schemas.order_tax import OrderTaxIn
from src.schemas.orders import (
    CreateUpdateAddress,
    OrderIn,
    OrderInUpdate,
    OrderOut,
    OrderSearchFilters,
    Receipt,
    UpdateOrder,
)
from src.schemas.rent_period_info import UpdatedPeriod
from src.schemas.subtotal_balance import SubtotalBalanceIn
from src.schemas.tax_balance import TaxBalanceIn
from src.schemas.token import Status
from src.schemas.total_order_balance import TotalOrderBalanceIn
from src.services.invoice.invoice_generator import InvoiceGenerator
from src.services.invoice.pdf_generation import (
    PdfGeneratorPurchaseInvoice,
    PdfGeneratorRentalInvoice,
    PdfGeneratorRentalReceipt,
)
from src.services.notifications import email_service, email_service_mailersend

# from src.services.esign import send_signature
from src.services.orders.address import save_address
from src.services.payment.authorize_pay_service import get_customer_profile
from src.utils.number_formatter import fc
from src.utils.order_zone import fetch_region
from src.utils.rental_invoice_data_parser import (
    filter_subtotals,
    get_visible_columns_and_data,
    last_payment_date,
    rent_period_dates,
    selected_rent_period_number,
)
from src.utils.users import ROLES_DICT, get_user_ids
from src.utils.utility import make_json_serializable
from src.crud.assistant_crud import assistant_crud
from src.utils.order_update_in_cache import clear_cache

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {self.default(key): self.default(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.default(item) for item in obj]
        else:
            return super().default(obj)


logger = logger.bind(name="orders")

user_crud = UserCRUD()
order_crud = OrderCRUD()

BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")
STAGE: str = settings.STAGE


# ids from mongo converted to UUIDs
def convert_non_uuid_to_uuid(value):
    if value:
        m = hashlib.md5()
        m.update(value.encode("utf-8"))
        return str(uuid.UUID(m.hexdigest()))


def remove_driver_inventory_dict(order):
    for line_item in order['line_items']:
        line_item['driver'] = None
        line_item['potential_driver'] = None
        line_item['inventory'] = None
    return order


def remove_driver_inventory(order):

    if isinstance(order, dict):
        order['line_item_driver'] = None
        order['line_item_potential_driver'] = None
        order['line_item_inventory'] = None
        order['line_item_potential_driver_id'] = None
        order['line_item_inventory_id'] = None
        order['line_item_inventory_container_release_number'] = None
    else:
        for line_item in order.line_items:
            line_item.driver = None
            line_item.potential_driver = None
            line_item.inventory = None

    return order


async def notify_driver_on_payment(order_id: str, containers_paid_for: list, user):
    existing_order: Order = await order_crud.get_one(order_id)
    order_driver = await user_crud.get_one(user.app_metadata["account_id"], existing_order.user.id)
    await line_item_crud.db_model.filter(id__in=containers_paid_for).update(paid_at=datetime.now())
    # TODO Send SMS
    account = await account_crud.get_one(user.app_metadata['account_id'])
    account_sid = account.integrations.get("twilio", {}).get("account_sid", "")
    logistics_email = account.cms_attributes.get("logistics_email", "")
    auth_token = account.integrations.get("twilio", {}).get("auth_token", "")
    from_phone = account.integrations.get("twilio", {}).get("from_phone", "")

    if auth_token != '' and account_sid != '':
        client = Client(account_sid, auth_token)
        message_to_customer = f"Order {existing_order.display_order_id} - *{existing_order.address.city}, {existing_order.address.zip} * is PAID!"

        try:
            message = client.messages.create(body=message_to_customer, from_=from_phone, to=order_driver.phone)
            logger.info(f"Message sent successfully. SID: {message.sid}")
        except Exception as e:
            logger.info(f"An error occurred: {str(e)}")

    return await email_service.send_driver_paid_email(order_driver.email, logistics_email, existing_order)


async def save_order(order: UpdateOrder, user, existing_order: Order, order_id=None, background_tasks=None) -> Order:
    note = order.note
    del order.note
    # adding these deletes bc of this error receieved:
    del order.address
    del order.display_order_id
    del order.line_items
    del order.order_type
    del order.amount_paid
    del order.payment_option
    del order.payment_strategy
    del order.transaction_type_id

    del order.override_distribution
    del order.subtotal_to_be_paid
    del order.tax_to_be_paid
    del order.fees_to_be_paid
    del order.remaining_balance

    order_dict = order.dict(exclude_unset=True)
    order_dict["account_id"] = existing_order.account_id

    if not order_dict.get("user_id"):
        order_dict["user_id"] = existing_order.user.id

    if order_dict.get("calculated_delivered_at"):
        order_dict['delivered_at'] = datetime.strptime(
            order_dict.get("calculated_delivered_at"), "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        del order_dict['calculated_delivered_at']

    if order_id:
        saved_order = await order_crud.update(order_dict["account_id"], order_id, OrderInUpdate(**order_dict))
        if background_tasks:
            background_tasks.add_task(
                send_event,
                saved_order.account_id,
                str(saved_order.id),
                make_json_serializable(order_dict),
                "order",
                "update",
            )
    else:
        account = await account_crud.get_one(existing_order.account_id)
        account_requires_cc_application = account.cms_attributes.get("applications", {}).get("credit_card", False)
        applications_override = None
        if account_requires_cc_application:
            applications_override = [{"name": "credit_card", "overridden": False}]
        else:
            applications_override = [{"name": "credit_card", "overridden": True}]
        order_dict["applications_overridden"] = applications_override
        logger.info(f"applications_override: {applications_override}")
        saved_order = await order_crud.create(OrderIn(**order_dict))
        if background_tasks:
            background_tasks.add_task(
                saved_order.account_id, str(saved_order.id), make_json_serializable(order_dict), "order", "create"
            )

    if note:
        noteInSchema = NoteInSchema(
            title=note.title,
            content=note.content,
            author_id=user.app_metadata.get("id"),
            order_id=saved_order.id,
        )
        await note_crud.create(noteInSchema)
        # send event to event controller
        if background_tasks:
            background_tasks.add_task(
                send_event,
                user.app_metadata['account_id'],
                str(saved_order.id),
                make_json_serializable(noteInSchema.dict()),
                "note",
                "create",
            )

    return saved_order


async def get_one_by_inventory(inventory_id: str):
    return await order_crud.get_one_by_inventory(inventory_id)


async def get_by_inventory_ids(inventory_ids: List[str]):
    return await order_crud.get_by_inventory_ids(inventory_ids)


async def get_card_on_file(found_order):
    if found_order.customer_profile_id:
        account = await account_crud.get_one(found_order.account_id)
        authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})
        if authorize_int_rentals.get("in_use"):

            customer_profile_response = get_customer_profile(
                str(found_order.customer_profile_id),
                authorize_int_rentals["api_login_id"],
                authorize_int_rentals["transaction_key"],
                url=authorize_int_rentals["url"],
            )

            logger.info(customer_profile_response)

            credit_card = (
                customer_profile_response.get('profile', {})
                .get('paymentProfiles', [{}])[0]
                .get('payment', {})
                .get('creditCard', {})
                .get('cardNumber', 'XXXX')
            )
            ExtendedItem = create_extended_model(OrderOut, "credit_card_number", str)
            attributes = found_order.dict()
            attributes['credit_card_number'] = credit_card
            found_order = ExtendedItem(**attributes)
    return found_order


async def get_order_line_items_history(order_id: str, user: Auth0User):
    order = await order_crud.get_one(order_id)
    line_items = order.line_items

    rental_history_lst = []
    for line_item in line_items:
        obj = await rental_history_crud.get_one_by_line_item_id(line_item.id)
        if obj:
            inventory_item = await container_inventory_crud.get_one(user.app_metadata['account_id'], obj.inventory.id)
            rental_history_lst.append(inventory_item)

    return rental_history_lst


async def get_order_by_display_id(order_id: str, user: Auth0User):
    try:
        can_read_all = [p for p in user.permissions if p == "read:all_orders"]
        can_read_inventory = [p for p in user.permissions if p == "read:inventory-containers"]

        found_order = await order_crud.get_one_by_display_id(user.app_metadata["account_id"], order_id)
        found_order = await get_card_on_file(found_order)

        if can_read_all:
            return found_order
        if not can_read_all:
            user_id = user.id.replace("auth0|", "")
            user_ids = await get_user_ids(user.app_metadata["account_id"], user_id, includeManager=True)
            user_ids.append(user_id)
            if str(found_order.user.id) not in user_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order does not exist or you don't have access to it",
                )
            if not can_read_inventory:
                return remove_driver_inventory(found_order)
            else:
                return found_order

    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist")


async def get_order_by_id(order_id: str, user: Auth0User):
    can_read_inventory = (
        [p for p in user.permissions if p == "read:inventory-containers"] if user is not None else False
    )
    try:
        if not can_read_inventory:
            return remove_driver_inventory(await order_crud.get_one(order_id))
        order = await order_crud.get_one(order_id)
        order = await get_card_on_file(order)
        return order
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist")


async def send_agent_status_email(order_id: str, user: Auth0User, background_tasks: BackgroundTasks):
    try:
        order = await order_crud.get_one(order_id)
        order_user = await user_crud.get_one(order.account_id, order.user.id)
        email_service.send_agent_status_email(order_user.email, order.display_order_id)
        return Status(message="success")
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist")


async def preview_payment(order_id, amount):
    existing_order: Order = await order_crud.get_one(order_id)
    tax_rate = existing_order.calculated_order_tax_rate

    subtotal_to_be_paid = 0
    tax_to_be_paid = 0
    fees_to_be_paid = 0

    max_subtotal_to_be_paid = existing_order.calculated_order_subtotal_balance
    tax_to_be_paid_on_max_subtotal = Decimal(max_subtotal_to_be_paid) * Decimal(tax_rate)

    if tax_to_be_paid_on_max_subtotal > existing_order.calculated_order_tax_balance:
        tax_to_be_paid_on_max_subtotal = existing_order.calculated_order_tax_balance

    if max_subtotal_to_be_paid + tax_to_be_paid_on_max_subtotal < Decimal(amount):
        subtotal_to_be_paid = Decimal(max_subtotal_to_be_paid)
        tax_to_be_paid = Decimal(tax_to_be_paid_on_max_subtotal)

        fees_to_be_paid = 0

        fees = existing_order.fees
        amount_left_for_fees = Decimal(amount) - Decimal(subtotal_to_be_paid) - Decimal(tax_to_be_paid)
        tax_to_pay_from_fees = Decimal(0)

        sorted_fees = sorted(fees, key=lambda fee: (fee.calculated_is_taxable, fee.calculated_remaining_balance))

        remaining_tax = existing_order.calculated_order_tax_balance - tax_to_be_paid

        for fee in sorted_fees:
            is_taxable = fee.calculated_is_taxable
            if amount_left_for_fees > Decimal(0):
                amount_to_pay = fee.calculated_remaining_balance
                calculated_tax_owed = Decimal(0)
                if is_taxable:
                    is_taxable = True
                    # This is a taxable fee add tax to amount to pay
                    calculated_tax_owed = fee.calculated_remaining_balance * tax_rate
                    amount_to_pay += calculated_tax_owed
                if fee.calculated_remaining_balance > Decimal(0):
                    amount_paid = Decimal(0)
                    if amount_left_for_fees >= amount_to_pay:
                        # we will be paying all fees plus tax
                        amount_paid = fee.calculated_remaining_balance
                        tax_component = calculated_tax_owed

                        # Pay remaining tax only
                        if tax_component >= remaining_tax:
                            tax_component = remaining_tax
                        tax_to_pay_from_fees += tax_component
                        amount_left_for_fees -= amount_paid + tax_component
                        remaining_tax -= tax_component

                    else:
                        # Funds left for fee payment is less than the fee total plus tax so paying off what can be paid
                        if is_taxable:
                            tax_component = amount_left_for_fees / (1 + tax_rate) * tax_rate
                            if tax_component >= remaining_tax:
                                tax_component = remaining_tax
                            tax_to_pay_from_fees += tax_component
                            amount_paid = amount_left_for_fees - tax_component
                            amount_left_for_fees -= amount_paid + tax_component
                        else:
                            # Not taxed so everything is for fee
                            amount_paid = amount_left_for_fees
                            amount_left_for_fees -= amount_paid

                    fees_to_be_paid += amount_paid
            else:
                break
        tax_to_be_paid += tax_to_pay_from_fees

        if subtotal_to_be_paid + fees_to_be_paid + tax_to_be_paid < Decimal(amount):
            tax_to_be_paid = Decimal(amount) - subtotal_to_be_paid - fees_to_be_paid

    else:
        subtotal_to_be_paid = Decimal(amount) / Decimal(1 + tax_rate)
        tax_to_be_paid = Decimal(subtotal_to_be_paid) * Decimal(tax_rate)

        if tax_to_be_paid > existing_order.calculated_order_tax_balance:
            subtotal_to_be_paid += tax_to_be_paid - existing_order.calculated_order_tax_balance
            tax_to_be_paid = existing_order.calculated_order_tax_balance

        fees_to_be_paid = Decimal(0)

    return {
        "subtotal_to_be_paid": subtotal_to_be_paid,
        "tax_to_be_paid": tax_to_be_paid,
        "fees_to_be_paid": fees_to_be_paid,
    }


async def send_invoice_email(
    order_id: str,
    contact_id: str,
    user: Auth0User,
    at_least_one_accessory: bool,
    at_least_one_shipping_container: bool,
    background_tasks: BackgroundTasks,
    period_id: str,
):
    try:
        order = await order_crud.get_one(order_id)
        existing_order = order
        order = order.dict()
        email_dict = order

        account = await account_crud.get_one(user.app_metadata["account_id"])
        emails = account.cms_attributes.get("emails", {})
        links = account.cms_attributes.get("links", {})

        email_dict['at_least_one_accessory'] = at_least_one_accessory
        email_dict['at_least_one_shipping_container'] = at_least_one_shipping_container

        if order.get("status", {}) == 'Estimate':
            email_dict["subject"] = f"Your Estimate #{email_dict['display_order_id']}"
            email_dict['text'] = emails.get("estimate", "")

        if order.get("status", {}) == 'Approved':
            email_dict["subject"] = f"Your Order is Approved #{email_dict['display_order_id']}"
            email_dict['text'] = emails.get("approved", "")

        if order.get("status", {}) == 'Invoiced':
            email_dict["subject"] = f"Your Invoice #{email_dict['display_order_id']}"
            email_dict['text'] = emails.get("invoice", "")

        if order.get("status", {}) == 'Quote':
            email_dict["subject"] = f"Your Quote #{email_dict['display_order_id']}"
            email_dict['text'] = emails.get("quote", "")
        email_dict["url"] = f"{BASE_INVOICE_URL}/#/{email_dict['id']}"
        if order.get("customer", {}):
            email_dict["customer_email"] = order["customer"]["email"]
            email_dict["customer_name"] = order.get("customer", {}).get("full_name")
            email_dict["company_name"] = account.name
        else:
            email_dict["customer_email"] = order["single_customer"]['customer_contacts'][0]["email"]
            email_dict["customer_name"] = order.get("single_customer", {}).get("full_name")
            email_dict["company_name"] = account.name

        if contact_id is not None:
            customer_contact = await customer_contact_crud.get_one(user.app_metadata["account_id"], contact_id)
            customer_contact = customer_contact.dict()
            email_dict["customer_email"] = customer_contact["email"]
            email_dict["customer_name"] = f"{customer_contact['first_name']} {customer_contact['last_name']}"

        if account.name == 'Amobilebox':
            email_dict["company_name"] = 'A Mobile Box'
        # logger.info(email_dict)
        if not account.name.startswith("USA Containers"):
            email_dict["url"] = f"{links.get('invoice_email_link', '')}{email_dict['id']}"
            if order.get("type") == "RENT" and period_id is not None:
                email_dict["url"] = f"{links.get('rental_email_link', '')}{email_dict['id']}/{period_id}"
            email_dict["account_id"] = account.id
            await email_service_mailersend.send_customer_invoice_email(email_dict)
        else:
            if order.get("type") == "RENT":
                payment_warranties = account.cms_attributes.get("rental_warranties", [])
                # await contract_controller.send_rental_email_contract(order_id)
            else:
                payment_warranties = account.cms_attributes.get("payment_warranties", [])
            email_dict['payment_warranties'] = payment_warranties
            if order.get("type") == "PURCHASE_ACCESSORY":
                await accessory_invoice_created_event(
                    existing_order, order.get("customer", {}), existing_order.created_at, background_tasks
                )
            elif period_id is not None:
                await rental_period_invoice_event(
                    existing_order, order.get("customer", {}), existing_order.created_at, period_id, background_tasks
                )
            else:
                await invoice_created_event(
                    existing_order, order.get("customer", {}), existing_order.created_at, background_tasks
                )
            # email_service.send_customer_invoice_email(email_dict)
        return Status(message="success")
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist")


async def get_orders_with_inventory(
    order_status: str, order_type: str, user: Auth0User, pagination: PAGINATION = order_crud.pagination_depends
):
    try:
        can_read_inventory = len([p for p in user.permissions if p == "read:inventory-containers"])
        if not can_read_inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order does not exist or you don't have access to it",
            )
        return await order_crud.get_by_inventory(
            order_status, order_type, user.app_metadata.get("account_id"), pagination
        )
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist")


def create_extended_model(base_model, attr_name, attr_type):
    # Get the existing annotations from the base model
    annotations = base_model.__annotations__.copy()
    # Add the new attribute to the annotations
    annotations[attr_name] = attr_type

    # Create a new class dynamically using type()
    ExtendedModel = type(f"{base_model.__name__}Extended", (OrderOut,), {"__annotations__": annotations})
    return ExtendedModel


def _manage_line_item_filtering(product_type, order_result):
    filtered_orders = 0
    order_result_filtered = []
    for order in order_result['orders']:
        if isinstance(order, dict):
            filtered_orders = order['line_item_product_type'] == product_type
        else:
            filtered_orders = len(
                [line_item for line_item in order.line_items if line_item.product_type == product_type]
            )

        if filtered_orders:
            order_result_filtered.append(order)

    order_result['orders'] = order_result_filtered
    return order_result


async def get_orders_by_status_type(
    order_status: str,
    order_type: str,
    auth_user: Auth0User,
    pagination: PAGINATION,
    get_all: bool = False,
    emulated_user_id: str = None,
    product_type: str = None,
    pull_all: bool = False,
):
    try:
        start_time = time.perf_counter()
        user = await user_crud.get_one(auth_user.app_metadata['account_id'], auth_user.id.replace("auth0|", ""))
        user_role = ROLES_DICT.get(STAGE, {}).get(str(user.role_id), {})

        can_read_inventory = len([p for p in auth_user.permissions if p == "read:inventory-containers"])
        can_see_only_accessory_orders = len([p for p in auth_user.permissions if p == "view:only_accessories"])

        can_read_potential_driver = len(
            [p for p in auth_user.permissions if p == "read:order_column-potential_driver_id"]
        )
        can_read_all = len([p for p in auth_user.permissions if p == "read:all_orders"])
        user_ids = None
        if not can_read_all:
            user_ids = await get_user_ids(
                auth_user.app_metadata["account_id"],
                auth_user.id.replace("auth0|", ""),
                includeManager=True,
            )
        if emulated_user_id and len([p for p in auth_user.permissions if p == "emulate:users"]):
            user_ids = await get_user_ids(
                auth_user.app_metadata["account_id"],
                emulated_user_id,
                includeManager=True,
            )

        # ensure order status looks like first letter capatilized
        if "_" in order_status:
            order_status_words: list[str] = order_status.split('_')
            for i, word in enumerate(order_status_words):
                order_status_words[i] = word.capitalize()

            order_status = "_".join(order_status_words)
        else:
            order_status = order_status.capitalize()

        limit = None
        if user_role not in ['sales_director', 'sales_manager', 'sales_agent', 'internal_sales']:
            limit = 50

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.info(f'permissions_checks_timer - Execution time: {execution_time:.4f} seconds')

        start_time = time.perf_counter()

        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

        if not can_read_all:
            redis_key = f"{str(user.id)}:{order_type}:{auth_user.app_metadata['account_id']}:order:{order_status}"
        else:
            redis_key = f"{order_type}:{auth_user.app_metadata['account_id']}:order:{order_status}"

        skip = pagination['skip']
        if not skip:
            skip = 0

        cached_value = r.get(redis_key)
        if not cached_value:
            start_time_cache_miss = time.perf_counter()

            pagination['limit'] = None
            pagination['skip'] = 0

            order_result = await partial_order_crud.get_by_status_type(
                auth_user.app_metadata["account_id"],
                order_status,
                order_type,
                user_ids,
                pagination,
                get_all,
            )
            r.set(redis_key, json.dumps(order_result, cls=CustomJSONEncoder))

            end_time_cache_miss = time.perf_counter()
            execution_time = end_time_cache_miss - start_time_cache_miss
            logger.info(f'Redis Cache Miss - Execution time: {execution_time:.4f} seconds')
        else:
            order_result = json.loads(cached_value)

        if not pull_all and limit:
            order_result['count'] = len(order_result['orders'])
            order_result['orders'] = order_result['orders'][skip : skip + limit]

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.info(f'Redis Get Orders - Execution time: {execution_time:.4f} seconds')

        start_time = time.perf_counter()
        if product_type is not None and product_type != 'ALL':
            if product_type == 'CONTAINER_ACCESSORY':
                order_result = _manage_line_item_filtering(product_type, order_result)

            elif product_type == 'SHIPPING_CONTAINER' or product_type == 'CONTAINER':
                order_result = _manage_line_item_filtering(product_type, order_result)

        if can_see_only_accessory_orders:
            order_result = _manage_line_item_filtering("CONTAINER_ACCESSORY", order_result)

        if can_read_inventory and can_read_potential_driver:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            logger.info(f'Filtering post cache - Execution time: {execution_time:.4f} seconds')
            return order_result
        else:
            for o in order_result.get("orders"):
                remove_driver_inventory(o)
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            logger.info(f'Filtering post cache - Execution time: {execution_time:.4f} seconds')
            return order_result

    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="No orders for query")


def CustomerOutToOrderOut(customer) -> List[OrderOut]:
    orders = customer.order
    del customer.order

    order_outs = []
    for order in orders:
        try:
            line_items = [LineItemOut(**line_item.dict()) for line_item in order.line_items]
            order_outs.append(
                OrderOut(
                    id=order.id,
                    display_order_id=order.display_order_id,
                    type=order.type,
                    status=order.status,
                    customer=customer,
                    user=order.user,
                    created_at=order.created_at,
                    modified_at=order.modified_at,
                    paid_at=order.paid_at,
                    payment_type=order.payment_type,
                    remaining_balance=order.remaining_balance,
                    sub_total_price=order.calculated_sub_total_price,
                    total_price=order.total_price,
                    gateway_cost=order.gateway_cost,
                    profit=order.calculated_profit,
                    attributes=order.attributes,
                    delivered_at=order.delivered_at,
                    completed_at=order.completed_at,
                    line_items=line_items,
                    account_id=customer.account_id,
                    note=order.note,
                )
            )
        except Exception as e:
            logger.info(order.id)
            logger.info(e)
    return order_outs


def LineItemOutToOrderOut(line_item) -> List[OrderOut]:
    try:
        order = line_item.order.dict()
        del line_item.order
        order["line_items"] = [line_item.dict()]
        return [OrderOut(**order)]
    except Exception as e:
        logger.info(line_item.id)
        logger.info(e)
        return []


async def get_all_team_leads(account_id):
    return await user_crud.get_all_team_leads(account_id=account_id)


def remove_extra_properties(order):
    order.pop("line_items", None)
    order.pop("note", None)
    order.pop("attributes", None)
    order.pop("address", None)
    order.pop("credit_card", None)

    return order


async def generate_rankings(
    user: Auth0User,
    searched_user_ids: str = None,
    emulated_user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    pod_mode: bool = False,
):
    try:
        searched_user_ids = searched_user_ids.split(",") if searched_user_ids else None
        can_read_all = [p for p in user.permissions if p == "read:all-rankings"]

        if not can_read_all:
            searched_user_ids = await get_user_ids(
                user.app_metadata["account_id"], user.id.replace("auth0|", ""), includeManager=True, includeTeam=True
            )
        is_emulating = len([p for p in user.permissions if p == "emulate:users"]) and emulated_user_id
        if is_emulating:
            searched_user_ids = await get_user_ids(
                user.app_metadata["account_id"], emulated_user_id, includeManager=True, includeTeam=True
            )

        # searched_user_ids = searched_user_ids[0] if searched_user_ids else None
        # if searched_user_ids is not None:
        #     logger.info(searched_user_ids)
        #     searched_user_ids = await get_user_ids(
        #         user.app_metadata["account_id"],
        #         searched_user_ids,
        #         includeManager=True,
        #         includeTeam=True,
        #     )

        if pod_mode is False:
            searched_user_ids = [str(user_id) for user_id in searched_user_ids] if searched_user_ids else None
            orders = await order_crud.filter_rankings(
                user.app_metadata["account_id"],
                user_ids=searched_user_ids,
                status="Paid,Delivered,Completed,Partially Paid,Delayed",
                paid_at=True,
                start_date=start_date,
                end_date=end_date,
                pod_mode=pod_mode,
            )
            orders = [remove_extra_properties(order.dict()) for order in orders]

            orders_pod = await order_crud.filter_rankings(
                user.app_metadata["account_id"],
                user_ids=searched_user_ids,
                status="Paid,Delivered,Completed,Pod,Delayed",
                signed_at=True,
                start_date=start_date,
                end_date=end_date,
                pod_mode=True,
            )
            orders_pod = [remove_extra_properties(order.dict()) for order in orders_pod]
            for order in orders_pod:
                orders.append(order)
        else:
            searched_user_ids = [str(user_id) for user_id in searched_user_ids] if searched_user_ids else None

            contracts = await order_contract_crud.get_contracts_by_signed_date(start_date, end_date)
            orders = await order_crud.get_by_ids(user.app_metadata['account_id'], [x.order_id for x in contracts])

            filtered_orders = []
            for order in filtered_orders:
                if order.user_id in searched_user_ids and not order.signed_at:
                    filtered_orders.append(order)

            orders = [remove_extra_properties(order.dict()) for order in filtered_orders]
        return orders
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="No orders for query")


async def search_orders_by_query_param(user: Auth0User, pagination: PAGINATION, filters: OrderSearchFilters):
    try:
        searched_user_ids = filters.searched_user_ids.split(",") if isinstance(filters.searched_user_ids, str) else filters.searched_user_ids
        can_read_all = [p for p in user.permissions if p == "read:all_orders"]
        # can_read_only_themselves = len([p for p in auth_user.permissions if p == "read:only_themselves"])

        user_ids = None
        if not can_read_all:
            user_ids = await get_user_ids(
                user.app_metadata["account_id"],
                user.id.replace("auth0|", ""),
                includeManager=True,
                includeTeam=False,
            )
            if searched_user_ids:
                searched_user_ids = [str(user_id) for user_id in searched_user_ids]
                searched_user_ids = list(set(searched_user_ids) & set(user_ids))
            else:
                searched_user_ids = user_ids

        if filters.emulated_user_id and len([p for p in user.permissions if p == "emulate:users"]):
            searched_user_ids = await get_user_ids(user.app_metadata["account_id"], filters.emulated_user_id)
            if filters.searched_user_ids:
                searched_user_ids = list(set(searched_user_ids) & set(filters.searched_user_ids))

        searched_user_ids = [str(user_id) for user_id in searched_user_ids] if searched_user_ids else None
        filters.searched_user_ids = searched_user_ids

        final_orders = []
        order_ids = []
        customers_searched = False
        if filters.customer_email or filters.customer_phone or filters.customer_name or filters.customer_company_name:
            customers = await customer_crud.search_customers(
                user.app_metadata["account_id"],
                filters.customer_email,
                filters.customer_phone,
                filters.customer_name,
                filters.customer_company_name,
                pagination,
            )
            for customer in customers:
                order_ids.extend([str(order.id) for order in customer.order])

            single_customers = await single_customer_crud.search_customers(
                user.app_metadata["account_id"],
                filters.customer_company_name,
                filters.customer_name,
            )

            for single_customer in single_customers:
                order_ids.extend([str(order.id) for order in single_customer.order])

            customer_contacts = await customer_contact_crud.get_by_filters_all(
                user.app_metadata["account_id"], filters.customer_email, filters.customer_phone, filters.customer_name
            )
            for customer_contact in customer_contacts:
                order_ids.extend([str(order.id) for order in customer_contact.customer.order])
            customers_searched = True
        if customers_searched and not order_ids:
            return final_orders
        display_order_ids = None

        city_region_map = None
        if filters.regions:
            city_region_map = await location_price_crud.get_city_region_map(user.app_metadata["account_id"])

        city_pickup_region_map = None
        if filters.pickup_regions:
            city_pickup_region_map = await location_price_crud.get_city_pickup_region_map(
                user.app_metadata["account_id"]
            )

        orders = await partial_order_crud.search_orders_dto_mapping(
            account_id=user.app_metadata["account_id"],
            order_ids=order_ids,
            display_order_ids=display_order_ids,
            city_region_map=city_region_map,
            city_pickup_region_map=city_pickup_region_map,
            pagination=pagination,
            filters=filters,
        )
        return orders
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="No orders for query")


async def get_all_orders(
    user: Auth0User,
    pagination: PAGINATION = order_crud.pagination_depends,
):
    try:
        logger.info(pagination)
        return await order_crud.get_all(user.app_metadata["account_id"], pagination=pagination)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="No orders for query")


async def get_emails(order, existing_order, user):
    order_user = None
    if order.user_id:
        order_user = await user_crud.get_one_without_account(order.user_id)
    else:
        order_user = await user_crud.get_one_without_account(existing_order.user.id)
    return [order_user.assistant.manager.email, order_user.email] if order_user.assistant else [order_user.email]


async def get_agent_emails(order):
    order_user = None
    order_user = await user_crud.get_one(order.account_id, order.user.id)
    return [order_user.assistant.manager.email, order_user.email] if order_user.assistant else [order_user.email]


async def get_agent(order):
    order_user = await user_crud.get_one_without_account(order.user.id)
    return order_user.dict()


async def accept_order_public(order_id: str, order: UpdateOrder) -> OrderOut:
    existing_order = await order_crud.get_one(order_id)
    return await save_order(order, existing_order.user, existing_order, order_id)


@atomic()
async def update_order(order_id: str, order: UpdateOrder, user: Auth0User, background_tasks: BackgroundTasks):
    can_read_inventory = len([p for p in user.permissions if p == "read:inventory-containers"])
    existing_order: Order = await order_crud.get_one(order_id)
    account = await account_crud.get_one(user.app_metadata.get("account_id"))

    logger.info(f"Attempting to update order: {order.display_order_id}")

    if account.cms_attributes.get("charge_tax", True):
        if order.calculated_order_tax or order.calculated_order_tax == 0:
            logger.info(f"Attempting to create tax: {order.display_order_id}")

            new_order_tax = OrderTaxIn(tax_amount=order.calculated_order_tax, order_id=order_id)
            await order_tax.create_order_tax(new_order_tax, user)

    del order.calculated_order_tax

    if order.remaining_balance == 0:
        order.status = "Paid"

    if (
        order.remaining_balance
        and order.remaining_balance > 0
        and order.remaining_balance != existing_order.calculated_total_price
    ):
        logger.info(f"Order partially paid: {order.display_order_id}")

        order.status = "Partially Paid"
        create_order_balance = TotalOrderBalanceIn(
            remaining_balance=order.remaining_balance, order_id=existing_order.id
        )
        await total_order_balance_crud.create(create_order_balance)

    if order.status == "Approved":
        pass
        # cms_crud.get
        # send_signature()

    if order.status == "Cancelled":
        text = f"You've had a customer cancel their order. Order number #{existing_order.display_order_id}"
        if account.cms_attributes.get("sendInternalAgentEmails", True):
            # background_tasks.add_task(
            #     email_service.send_agent_email, text, await get_emails(order, existing_order, user)
            # )
            email_service.send_agent_email(text, await get_emails(order, existing_order, user))

    if order.status == "Paid":
        logger.info(f"Order changed status to paid: {order.display_order_id}")

        at_least_one_accessory = False
        for line_item in existing_order.line_items:
            if line_item.product_type == 'CONTAINER_ACCESSORY':
                at_least_one_accessory = True

        logger.info(f"Order paid at teast one accessory ({at_least_one_accessory}): {order.display_order_id}")

        if account.name.startswith("USA Containers") and existing_order.status != "Paid" and at_least_one_accessory:
            logger.info(f"Before sending accessory paid email: {order.display_order_id}")

            await email_service.send_accessory_paid_email(existing_order.display_order_id)
        if existing_order.status == "Delayed":
            email_text = f"Order #{existing_order.display_order_id} is now back under the status PAID and the delivery process has started. Please check the order's notes! "
            if account.cms_attributes.get("sendInternalAgentEmails", True) and account.name.startswith(
                "USA Containers"
            ):
                order_user = await user_crud.get_one(user.app_metadata["account_id"], existing_order.user.id)
                email_service.send_agent_email(email_text, [order_user.email, "delayed@usacontainers.co"])
        else:
            create_order_balance = TotalOrderBalanceIn(remaining_balance=0, order_id=existing_order.id)
            await total_order_balance_crud.create(create_order_balance)

            email_text = f"order just pay! Order #{existing_order.display_order_id}"

            logger.info(email_text)
            # background_tasks.add_task(send_sms_invite, existing_order.customer.phone, user.app_metadata["account_id"])
            if account.cms_attributes.get("sendInternalAgentEmails", True):
                # background_tasks.add_task(
                #     email_service.send_agent_email, email_text, await get_emails(order, existing_order, user)
                # )
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
                        existing_order.display_order_id,
                        False if existing_order.signed_at is None else True,
                        account.id,
                        await get_agent(existing_order),
                        existing_order,
                        await get_emails(order, existing_order, user),
                        background_tasks
                    )
                else:
                    email_service.send_agent_email(email_text, await get_emails(order, existing_order, user))

            if order.transaction_type_id:
                transaction_type = await transaction_type_crud.get_one(account.id, order.transaction_type_id)
                order.paid_at = transaction_type.created_at
            else:
                order.paid_at = datetime.now()

        if not existing_order.paid_at:
            if order.transaction_type_id:
                transaction_type = await transaction_type_crud.get_one(account.id, order.transaction_type_id)
                order.paid_at = transaction_type.created_at
            else:
                order.paid_at = datetime.now()
            # if not existing_order.signed_at:
            #     await paid_at_event(existing_order, order.paid_at, background_tasks)

    if order.status == 'Delayed' and (existing_order.status == 'Paid' or existing_order.status == 'Pod'):
        if account.name.startswith("USA Containers"):
            order_user = await user_crud.get_one(user.app_metadata["account_id"], existing_order.user.id)

            email_list: list[str] = [order_user.email, "delayed@usacontainers.co"]

            email_text = ""
            product_cities = [
                line_item.product_city for line_item in existing_order.line_items if line_item.product_city
            ]
            if not product_cities:
                region = None
            else:
                region = await fetch_region(product_cities[0], existing_order.account_id)
            if region and len(region) > 0:
                region = region[0]
                email_text = f"Order #{existing_order.display_order_id} ({region}) just had the status changed to DELAYED due to the customer request. Please check the order's notes! "
            else:
                region = None
                email_text = f"Order #{existing_order.display_order_id}  just had the status changed to DELAYED due to the customer request. Please check the order's notes! "

            # background_tasks.add_task(email_service.send_agent_email, email_text, email_list)
            email_service.send_agent_email(email_text, email_list)

    if order.status == "Delivered":
        # background_tasks.add_task(send_sms_invite, existing_order.customer.phone, user.app_metadata["account_id"])
        if not existing_order.delivered_at:
            order.delivered_at = datetime.now()
            if existing_order.type == "RENT":
                if len(existing_order.rent_periods) == 0:
                    raise HTTPException(status_code=422, detail="Rent order has no rent periods.")

                first_rent_period = existing_order.rent_periods[0]
                updated_period = UpdatedPeriod(
                    date=order.delivered_at.strftime("%m/%d/%Y"),
                    id=str(first_rent_period.id),
                    order_id=str(existing_order.id),
                    rent_due_on_day=datetime.now().day,
                )
                await rent_period_controller.modify_rent_period_due_dates(updated_period, [])

    if order.status == "Completed":
        if not existing_order.completed_at:
            order.completed_at = datetime.now()
            await completed_at_event(existing_order, order.completed_at, background_tasks)

    if order.status == "Returned":
        if not existing_order.returned_at:
            order.returned_at = datetime.now()

    if order.status == "Pod":
        if existing_order.status != "Pod" and not existing_order.signed_at:
            # Status just changed to Pod and it has not been signed already
            order.signed_at = datetime.now(timezone.utc)

        if existing_order.status == "Delayed":
            email_text = f"Order #{existing_order.display_order_id} is now back under the status Pod and the delivery process has started. Please check the order's notes! "
            if account.name.startswith("USA Containers"):
                order_user = await user_crud.get_one(user.app_metadata["account_id"], existing_order.user.id)
                background_tasks.add_task(
                    email_service.send_agent_email, email_text, [order_user.email, "delayed@usacontainers.co"]
                )

    if hasattr(order, "calculated_delivered_at") and order.calculated_delivered_at is not None:
        order.delivered_at = order.calculated_delivered_at

    if order.delivered_at:
        if existing_order.status == "Pod" or existing_order.status == "Paid":
            order.status = "Delivered"

        if existing_order.type == 'RENT':
            if len(existing_order.rent_periods) == 0:
                raise Exception("Order doesn't have any rent periods.")

            first_rent_period = existing_order.rent_periods[0]
            # check the format/type of delivered_at
            if not isinstance(order.delivered_at, datetime):
                order.delivered_at = datetime.fromisoformat(order.delivered_at.replace('Z', '+00:00'))

            updated_period = UpdatedPeriod(
                date=order.delivered_at.strftime("%m/%d/%Y"),
                id=str(first_rent_period.id),
                order_id=str(existing_order.id),
                rent_due_on_day=order.delivered_at.day,
            )

            if len(existing_order.rent_periods) == 1:
                await rent_period_controller.modify_rent_period_due_dates(updated_period, [])
            else:
                rent_periods = existing_order.rent_periods[1:]
                rent_periods_sorted = sorted(rent_periods, key=lambda x: x.start_date)
                await rent_period_controller.modify_rent_period_due_dates(
                    updated_period, [x.id for x in rent_periods_sorted]
                )

            if len(existing_order.rent_periods) == 1:
                existing_order_aux = await order_crud.get_one(str(existing_order.id))
                initial_rent_period: RentPeriod = existing_order_aux.rent_periods[0]
                # TODO all awaits here can go into background tasks
                await rent_period_controller.handle_rent_period_dates_update(
                    initial_rent_period, existing_order_aux, order.delivered_at.day, initial_rent_period.start_date
                )
                rent_options: dict = account.cms_attributes.get("rent_options")
                rent_options['rolling_rent_periods'] = 12
                rent_options['start_date'] = initial_rent_period.start_date
                await rent_period_controller.generate_rolling_rent_periods(rent_options, initial_rent_period, existing_order_aux)


        # send event to event controller
        if background_tasks:
            background_tasks.add_task(
                send_event,
                user.app_metadata['account_id'],
                str(existing_order.id),
                make_json_serializable({"delivered_at": order.delivered_at}),
                "order",
                "update_delivered_at",
            )

    if order.status == "Partially Paid":
        if not order.override_distribution:
            await handle_order_balances_paydown(
                existing_order,
                order.amount_paid,
                order.transaction_type_id,
                order.payment_strategy,
                order.payment_option,
            )
        else:
            await handle_order_balances_paydown_distribution(
                existing_order,
                order.subtotal_to_be_paid,
                order.tax_to_be_paid,
                order.fees_to_be_paid,
                order.transaction_type_id,
            )
    if order.status == "Paid":
        await handle_pay_all_balances(existing_order, order.transaction_type_id)
    if existing_order.status == "Pod" and order.status == "Partially Paid":
        order.status = "Pod"
    updated_order = await save_order(order, user, existing_order, order_id, background_tasks=background_tasks)

    if order.status == "Pod":
        if existing_order.status != "Pod" and not existing_order.signed_at:
            # Status just changed to Pod and it has not been signed already
            await notifications_controller.send_paid_email(order_id, background_tasks)
            email_text = f"You just had a customer sign the contract! Order #{existing_order.display_order_id}"
            # background_tasks.add_task(send_sms_invite, existing_order.customer.phone, user.app_metadata["account_id"])
            if account.cms_attributes.get("sendInternalAgentEmails", True):
                # background_tasks.add_task(
                #     email_service.send_agent_email, email_text, await get_emails(order, existing_order, user)
                # )
                external_integrations = account.external_integrations
                if (
                    external_integrations is not None
                    and external_integrations.get("resources") is not None
                    and len(external_integrations.get("resources")) > 0
                    and len(
                        [
                            res
                            for res in external_integrations.get("resources")
                            if "update:user:signed_at" in res.get("event_types")
                        ]
                    )
                    > 0
                ):
                    await order_pod_signed_agent_notification(
                        existing_order.display_order_id,
                        True,
                        account.id,
                        await get_agent(existing_order),
                        existing_order,
                        await get_emails(order, existing_order, user),
                        background_tasks,
                    )
                else:
                    email_service.send_agent_email(email_text, await get_emails(order, existing_order, user))

    if order.status == "Paid":
        if existing_order.status == "Delayed":
            pass
        else:
            updated_order_d = updated_order.dict()
            if not updated_order.is_pickup:
                if account.name.startswith("USA Containers"):
                    email_service.send_customer_general_receipt_email(updated_order_d)
                    if existing_order.status != "Pod":
                        await notifications_controller.send_paid_email(order_id, background_tasks)
                else:
                    email_info = {
                        "text": account.cms_attributes.get("emails", {}).get("payment", ""),
                        "order_title": updated_order_d.get("status", "Invoice"),
                        "account_name": account.name,
                        "display_order_id": updated_order_d.get("display_order_id"),
                        **updated_order_d,
                    }
                    if existing_order.status != "Pod":
                        await email_service_mailersend.send_paid_email(email_info)

    # just for good measure, pull the order again
    updated_order = await order_crud.get_one(order_id)

    if not can_read_inventory:
        return remove_driver_inventory(updated_order)
    return updated_order


async def handle_pay_all_balances(
    existing_order: Order, transaction_type_id: str = None, order_credit_card_id: str = None
):
    await subtotal_balance_controller.create_subtotal_balance(
        SubtotalBalanceIn(
            balance=0,
            order_id=existing_order.id,
            transaction_type_id=transaction_type_id,
            order_credit_card_id=order_credit_card_id,
        )
    )
    await tax_balance_controller.create_tax_balance(
        TaxBalanceIn(
            balance=0,
            order_id=existing_order.id,
            tax_rate=0,
            transaction_type_id=transaction_type_id,
            order_credit_card_id=order_credit_card_id,
        )
    )
    update_fees_balance_list: List[OrderFeeBalanceIn] = []
    fees = existing_order.fees
    for fee in fees:
        update_fees_balance_list.append(
            OrderFeeBalanceIn(
                remaining_balance=0,
                order_id=existing_order.id,
                account_id=existing_order.account_id,
                fee_id=fee.id,
                transaction_type_id=transaction_type_id,
                order_credit_card_id=order_credit_card_id,
            )
        )
    await order_fee_balance_controller.handle_initial_fee_balance(update_fees_balance_list)


async def handle_order_balances_paydown_distribution(
    existing_order: Order,
    subtotal_to_be_paid: Decimal,
    tax_to_be_paid: Decimal,
    fees_to_be_paid: Decimal,
    transaction_type_id: str = None,
):
    await subtotal_balance_controller.handle_subtotal_balance_paydown(
        existing_order, subtotal_to_be_paid, False, transaction_type_id, None
    )
    await tax_balance_controller.handle_tax_balance_paydown(
        existing_order, tax_to_be_paid, False, transaction_type_id, None
    )

    await order_fee_balance_controller.handle_pay_order_fee_balance_only_fees(
        existing_order, fees_to_be_paid, transaction_type_id=transaction_type_id, order_credit_card_id=None
    )


async def handle_order_balances_paydown(
    existing_order: Order,
    amount_paid: Decimal,
    transaction_type_id: str = None,
    payment_strategy: str = None,
    payment_option: str = None,
    order_credit_card_id: str = None,
):
    tax_rate = existing_order.calculated_order_tax_rate
    # Check if any strategy was set for payment
    if (
        payment_strategy is not None
        and payment_option is not None
        and payment_strategy in ['pay_sub_total', 'pay_fees']
    ):
        # Current strategy
        if payment_strategy == 'pay_sub_total':
            # calculated_order_subtotal_balance
            subtotal_owed = existing_order.calculated_order_subtotal_balance
            tax_on_subtotal = subtotal_owed / (1 + tax_rate) * tax_rate
            if (subtotal_owed + tax_on_subtotal) >= amount_paid:
                # we can pay off the subtotal
                subtotal_paid = amount_paid / (1 + tax_rate)
                await subtotal_balance_controller.handle_subtotal_balance_paydown(
                    existing_order, subtotal_paid, False, transaction_type_id, order_credit_card_id
                )
                await tax_balance_controller.handle_tax_balance_paydown(
                    existing_order, tax_on_subtotal, False, transaction_type_id, order_credit_card_id
                )
            else:
                raise HTTPException(
                    status_code=422,
                    detail="Payment amount is more than subtotal owed",
                )
                pass

        elif payment_strategy == 'pay_fees':
            # calculated_order_fee
            fee_owed = existing_order.calculated_order_fees_balance
            taxable_fees_owed = existing_order.calculated_order_fees_taxable_balance
            tax_on_fee = taxable_fees_owed / (1 + tax_rate) * tax_rate
            if (fee_owed + tax_on_fee) >= amount_paid:
                # we can pay off the fee owed and related tax
                taxable_amount = await order_fee_balance_controller.handle_pay_order_fee_balance(
                    order=existing_order,
                    payment_amount=amount_paid,
                    transaction_type_id=transaction_type_id,
                    order_credit_card_id=order_credit_card_id,
                )
                await tax_balance_controller.handle_tax_balance_paydown(
                    existing_order, taxable_amount, False, transaction_type_id, order_credit_card_id
                )
                pass
            else:
                raise HTTPException(
                    status_code=422,
                    detail="Payment amount is more than fees owed",
                )
                pass
    else:
        paid_off_balances = 0
        subtotal_owed = existing_order.calculated_order_subtotal_balance
        tax_on_subtotal_owed = subtotal_owed * tax_rate

        if tax_on_subtotal_owed > existing_order.calculated_order_tax_balance:
            tax_on_subtotal_owed = existing_order.calculated_order_tax_balance

        # lets check if the amount paid can pay off the subtotal with tax if any
        if (subtotal_owed + tax_on_subtotal_owed) < amount_paid:
            remaining_tax_balance = existing_order.calculated_order_tax_balance
            #   they can pay subtotal and pay off some fees
            if existing_order.calculated_order_subtotal_balance > Decimal(0):
                # They still owed som subtotal
                await subtotal_balance_controller.handle_subtotal_balance_paydown(
                    existing_order, subtotal_owed, False, transaction_type_id, order_credit_card_id
                )
                paid_off_balances += subtotal_owed

                await tax_balance_controller.handle_tax_balance_paydown(
                    existing_order, tax_on_subtotal_owed, False, transaction_type_id, order_credit_card_id
                )
                remaining_tax_balance -= tax_on_subtotal_owed
                paid_off_balances += tax_on_subtotal_owed

            # pay off fees with remaining amount paid
            amount_after_subtotal_payment = amount_paid - (subtotal_owed + tax_on_subtotal_owed)
            taxable_amount, total_fee_paid = await order_fee_balance_controller.handle_pay_order_fee_balance(
                order=existing_order,
                payment_amount=amount_after_subtotal_payment,
                transaction_type_id=transaction_type_id,
                order_credit_card_id=order_credit_card_id,
                remaining_tax_balance=remaining_tax_balance,
            )
            paid_off_balances += total_fee_paid

            # Update, to get latest tax balance
            existing_order = await order_crud.get_one(existing_order.id)

            if taxable_amount - existing_order.calculated_order_tax_balance > 1:
                # We are in a quick pay scenario, with a flat tax, so the tax from taxable fees we want to paydown further doesn't exist
                await tax_balance_controller.handle_tax_balance_paydown(
                    existing_order,
                    existing_order.calculated_order_tax_balance,
                    False,
                    transaction_type_id,
                    order_credit_card_id,
                )
                paid_off_balances += existing_order.calculated_order_tax_balance
            else:
                await tax_balance_controller.handle_tax_balance_paydown(
                    existing_order, taxable_amount, False, transaction_type_id, order_credit_card_id
                )
                paid_off_balances += taxable_amount

            # Update, to get latest tax balance
            existing_order = await order_crud.get_one(existing_order.id)

            if Decimal(paid_off_balances) < Decimal(amount_paid) + Decimal(0.1):
                # check if can pay tax out of remaining amount
                if amount_paid - paid_off_balances <= existing_order.calculated_order_tax_balance:
                    await tax_balance_controller.handle_tax_balance_paydown(
                        existing_order,
                        Decimal(amount_paid) - Decimal(paid_off_balances),
                        False,
                        transaction_type_id,
                        order_credit_card_id,
                    )
                else:
                    await tax_balance_controller.handle_tax_balance_paydown(
                        existing_order,
                        existing_order.calculated_order_tax_balance,
                        False,
                        transaction_type_id,
                        order_credit_card_id,
                    )

        else:
            # They can at most pay off subtotal
            tax_paid = amount_paid / (1 + tax_rate) * tax_rate
            subtotal_paid = amount_paid / (1 + tax_rate)

            if tax_paid > existing_order.calculated_order_tax_balance:
                subtotal_paid += tax_paid - existing_order.calculated_order_tax_balance
                tax_paid = existing_order.calculated_order_tax_balance

            await subtotal_balance_controller.handle_subtotal_balance_paydown(
                existing_order, subtotal_paid, False, transaction_type_id, order_credit_card_id
            )

            await tax_balance_controller.handle_tax_balance_paydown(
                existing_order, tax_paid, False, transaction_type_id, order_credit_card_id
            )


async def update_order_address(address_id: str, order_address: CreateUpdateAddress, order_id: str, user: Auth0User):
    await save_address(order_address, address_id, user.app_metadata.get("account_id"))
    return await order_crud.get_one(order_id)


@atomic()
async def archive_order(order_id: str, auth_user: Auth0User, background_tasks=None):
    order = await order_crud.get_one(order_id)
    inventory_ids = []
    other_inventory_ids = []
    for item in order.line_items:
        if item.inventory is None and item.other_inventory is None:
            continue
        elif item.inventory is not None:
            inventory_ids.append(item.inventory.id)
            await line_item_crud.db_model.filter(id=item.id).update(inventory_id=None)
        elif item.other_inventory is not None:
            other_inventory_ids.append(item.other_inventory.id)
            await line_item_crud.db_model.filter(id=item.id).update(inventory_id=None)
        await line_item_crud.db_model.filter(id=item.id).update(potential_driver_id=None)

    if len(inventory_ids) > 0:
        await container_inventory_crud.db_model.filter(id__in=inventory_ids).update(status="Available")
    if len(other_inventory_ids) > 0:
        await other_inventory_crud.db_model.filter(id__in=other_inventory_ids).update(status="Available")

    await order_crud.update(
        auth_user.app_metadata['account_id'],
        order_id,
        OrderInUpdate(account_id=auth_user.app_metadata['account_id'], is_archived=True),
    )

    # send event to event controller
    if background_tasks:
        background_tasks.add_task(send_event, order.account_id, str(order.id), {}, "order", "delete")

    user_id = auth_user.id.replace("auth0|", "")
    try:
        assistant = await assistant_crud.get_by_assistant_id(user_id)
    except HTTPException as e:
        if e.status_code == 404:
            assistant = None
        else:
            raise e

    user_ids = [user_id]
    if assistant:
        user_ids.append(assistant.manager.id)

    try:
        clear_cache([order.status], order.type, user_ids, auth_user.app_metadata['account_id'])
    except Exception as e:
        logger.info(str(e))
    return Status(message="success")


async def drop_order(
    order_id: str,
    auth_user: Auth0User,
):
    line_items = await line_item_crud.get_by_order_id(order_id)
    inventory_ids = []
    other_inventory_ids = []
    for item in line_items:
        if item.inventory is None and item.other_inventory is None:
            continue
        elif item.inventory is not None:
            inventory_ids.append(item.inventory.id)
        elif item.other_inventory is not None:
            other_inventory_ids.append(item.other_inventory.id)
    if len(inventory_ids) == 0 and len(other_inventory_ids) == 0:
        # drop file_upload
        await file_upload_crud.db_model.filter(order_id=order_id).delete()
        # drop misc_cost
        await misc_cost_crud.db_model.filter(order_id=order_id).delete()
        # drop notes
        await note_crud.db_model.filter(order_id=order_id).delete()
        # drop order_credit_card
        await order_credit_card_crud.db_model.filter(order_id=order_id).delete()
        # drop total_order_balance
        await total_order_balance_crud.db_model.filter(order_id=order_id).delete()
        # drop customer_application_response
        await customer_app_response_crud.db_model.filter(order_id=order_id).delete()
        # drop fee
        await fee_crud.db_model.filter(order_id=order_id).delete()
        # drop order_tax
        await order_tax_crud.db_model.filter(order_id=order_id).delete()
        # drop coupon_code_order
        await coupon_code_order_crud.db_model.filter(order_id=order_id).delete()
        # drop order_contract
        await order_contract_crud.db_model.filter(order_id=order_id).delete()
        # Check if there any inventory Items and drop them or set to avaialable
        # drop line_item
        # Fetch the related inventory and other inventory list and drop or reset those
        # inventory_id, other_inventory_id,
        # if len(inventory_ids) > 0 :
        #     await container_inventory_crud.db_model.filter(id__in=inventory_ids).update(status="Available")
        # if len(other_inventory_ids) > 0 :
        #     await other_inventory_crud.db_model.filter(id__in=other_inventory_ids).update(status="Available")
        await line_item_crud.db_model.filter(order_id=order_id).delete()
        # drop rent_period
        await rent_period_crud.db_model.filter(order_id=order_id).delete()
        # drop transaction_type
        await transaction_type_crud.db_model.filter(order_id=order_id).delete()
        # drop order_fee_balance
        await order_fee_balance_crud.db_model.filter(order_id=order_id).delete()
        # drop subtotal_balance
        await subtotal_balance_crud.db_model.filter(order_id=order_id).delete()
        # drop tax_balance
        await tax_balance_crud.db_model.filter(order_id=order_id).delete()
        # customer_application_schema_id
        # if (
        #     hasattr(existing_order, 'customer_application_schema_id')
        #     and existing_order.customer_application_schema_id is not None
        # ):
        #     await customer_application_schema_crud.db_model.filter(
        #         id=existing_order.customer_application_schema_id
        #     ).delete()
        # drop order
        await order_crud.db_model.filter(id=order_id).delete()
        # customer_id, address_id, customer_profile_id, purchased_order_job_id, single_customer_id, billing_address_id
        return Status(message="success")
    else:
        raise HTTPException(
            status_code=422,
            detail="You must manage attached items before deleting order",
        )


def check_is_single_customer_order(order: Order) -> dict[str, Any]:
    customer_info: None | OrderCustomer | Customer = None
    is_single_customer: bool = False

    if order.customer is not None:
        customer_info = order.customer
    elif order.single_customer is not None:
        customer_info = order.single_customer
        is_single_customer = True

    customer_info_dict: dict[str, Any] = customer_info.__dict__

    if is_single_customer:
        customer_info_dict["email"] = customer_info.customer_contacts[0].email
        customer_info_dict["phone"] = customer_info.customer_contacts[0].phone

    return_dict: dict[str, Any] = {"customer_info": customer_info_dict, "is_single_customer": is_single_customer}

    return return_dict


async def get_transaction_types_message(order: Dict[str, Any]) -> str:
    transaction_types_message = ""
    for tt in order.get('transaction_type_order', []):
        transaction_types_message += tt.get('payment_type', "") + ", "
    for tt in order.get('credit_card', []):
        transaction_types_message += "Credit Card, "
    return transaction_types_message.rstrip(", ")


async def get_notes(order: Dict[str, Any], order_id: str, cms_attributes: Dict[str, Any]) -> str:
    public_notes = await note_crud.get_public_note(order_id)
    notes = cms_attributes.get("bank_fee_message", '')
    if public_notes:
        notes += '\n\n' + public_notes[0].content
    return notes


def prepare_items(order: Dict[str, Any], down_payment_strategy: str, single_discount: Decimal) -> Dict[str, Any]:
    items = {}
    for line_item in order.get("line_items", []):
        key = line_item.get("abrev_title")
        inventory = line_item.get("inventory", {}) or {}
        container_number = inventory.get("container_number", "")

        if key in items:
            items[key]["quantity"] += line_item.get("quantity", 1)
            items[key]["unit_cost"] += fetch_item_unit_cost(order, line_item, down_payment_strategy) + single_discount
            items[key]["container_numbers"][f'{len(items[key]["container_numbers"])}'] = container_number
        else:
            items[key] = {
                "container_numbers": {"0": container_number},
                "name": key,
                "quantity": line_item.get("quantity", 1),
                "unit_cost": fetch_item_unit_cost(order, line_item, down_payment_strategy) + single_discount,
            }
    return items


def prepare_transactions(order: Dict[str, Any]) -> list:
    transactions = [
        {
            'name': tt.get('payment_type'),
            'date': (
                tt.get("transaction_effective_date") if tt.get("transaction_effective_date") else tt.get('created_at')
            ),
            'notes': tt.get('notes'),
            'amount': tt.get('amount'),
        }
        for tt in order.get('transaction_type_order', [])
    ]
    for tt in order.get('credit_card', []):
        transactions.append(
            {'name': 'Credit Card', 'date': tt.get('created_at'), 'notes': tt.get('notes'), 'amount': tt.get('amount')}
        )
    return sorted(transactions, key=lambda x: x['date'], reverse=True)


def parse_address(addr_str: str) -> Dict[str, str]:
    addr = addr_str.split(", ")
    try:
        return {
            "street": addr[0],
            "city": addr[1],
            "state": addr[2],
            "zip": addr[3],
        }
    except Exception as e:
        logger.error(f"Error parsing address: {e}")
        return {
            "street": "",
            "city": "",
            "state": "",
            "zip": "",
        }


async def generate_order_pdf(order: Order, order_id: str) -> str:
    logger.info("Generating Invoice, FREE")
    account = await account_crud.get_one(order.account_id)
    cms_attributes = account.cms_attributes
    account_name = account.name

    order = order.dict()
    logos = cms_attributes.get("logo_settings", {})

    transaction_types_message = await get_transaction_types_message(order)
    notes = await get_notes(order, order_id, cms_attributes)
    if transaction_types_message:
        if notes is None:
            notes = ""
        notes += '\n' + "Paid by " + transaction_types_message

    days_to_add = cms_attributes.get("grace_period", 5)
    invoice = InvoiceGenerator(
        sender=f'{ "A Mobile Box" if account_name == "Amobilebox" else account_name }\n'
        + cms_attributes.get("company_mailing_address", "")
        + "\n"
        + cms_attributes.get("quote_contact_phone", ""),
        to=order.get("customer", {}).get("full_name", ""),
        company_to=order.get("customer", {}).get("company_name", ""),
        ship_to=order.get("address", {}).get("full_address", ""),
        logo="https://fluffy-jelly-0cb624.netlify.app" + logos.get("logo_path", ""),
        number=order.get("display_order_id", None),
        date=order.get("created_at").strftime("%Y-%m-%d"),
        due_date=(order.get("created_at") + timedelta(days=days_to_add)).strftime("%Y-%m-%d"),
        notes=notes,
        shipping=0 if order.get("type") == "RENT" else str(order.get("calculated_order_tax")),
        amount_paid=str(order.get('total_paid')),
    )

    single_discount = (
        (order.get("calculated_discount") / len(order.get("line_items", []))).quantize(Decimal('0.01'))
        if order.get("calculated_discount") is not None and order.get("calculated_discount") > 0.00
        else Decimal(0.00)
    )
    items = prepare_items(order, cms_attributes.get("rent_options").get("down_payment_strategy", ""), single_discount)

    isFirstItem = True
    for item in items:
        numbers = [(key, value) for key, value in items[item]['container_numbers'].items() if value != '']
        shipping = " with Shipping"
        name_items = ""
        if isFirstItem and order.get("type") == "RENT":
            name_items = " -- First Payment"
            items[item]['unit_cost'] = order.get("calculated_down_payment")
        if not isFirstItem and order.get("type") == "RENT":
            shipping = ""

        container_numbers_str = ", ".join([f"{value}" for key, value in numbers if value != "" and value is not None])
        if container_numbers_str != '':
            container_numbers_str = " [ " + container_numbers_str + " ] "
        if len(numbers) > 0:
            name_items = items[item]['name'] + container_numbers_str + shipping + name_items
        else:
            name_items = items[item]['name'] + shipping + name_items

        invoice.add_item(
            name=name_items,
            quantity=items[item]['quantity'],
            unit_cost=str(items[item]['unit_cost'] / items[item]['quantity']),
        )
        isFirstItem = False

    if order.get("calculated_discount") > 0.00:
        invoice.add_item(
            name='Applied Discount (Not Taxable)', quantity=1, unit_cost=str(order.get("calculated_discount") * -1)
        )

    if order.get("calculated_fees") > 0.00:
        for fee in order.get("fees", []):
            invoice.add_item(
                name=f'{ fee.get("type", {}).get("name") } Fee ({ "Taxable" if fee.get("type", {}).get("is_taxable") else "Not Taxable" })',
                quantity=1,
                unit_cost=str(fee.get("fee_amount")),
            )

    if order.get('purchase_order_number') is not None:
        invoice.add_custom_field(name='P.O Number', value=order.get('purchase_order_number'))
    if order.get('purchased_order_job_id') is not None:
        invoice.add_custom_field(name='P.O. Job Id', value=order.get('purchased_order_job_id'))
    invoice.set_template_text('shipping_title', 'Tax')
    if order.get("type") == "RENT":
        invoice.set_template_text('invoice_number_title', 'RENTAL #')
    if order.get('status') in ['Paid', 'Partially paid', "Completed", "Delivered"]:
        invoice.set_template_text("header", "RECEIPT")
    invoice.set_template_text('ship_to_title', 'Delivery To')
    invoice.toggle_subtotal('', True, True)
    return await invoice.download(account.integrations.get("pdf_invoice_key"))


async def generate_rent_receipt_pdf_docugenerate(order: Order, receipt: Receipt):
    account = await account_crud.get_one(order.account_id)
    cms_attributes = account.cms_attributes
    logos = cms_attributes.get("logo_settings", {})

    invoice = PdfGeneratorRentalReceipt(
        api_key=account.integrations.get("docugenerate_api_key"),
        logo="https://fluffy-jelly-0cb624.netlify.app" + logos.get("logo_path", ""),
        title=f"{'INVOICE' if receipt.payment_date is None else 'RECEIPT'}",
        receipt=receipt,
    )

    return await invoice.download()


async def generate_web_rental_order_table_data(order: Order, rent_period_id: str):
    rental_line_items = []
    crt_rent_period: RentPeriod = None
    for rent_period in order.rent_periods:
        if str(rent_period.id) == rent_period_id:
            crt_rent_period = rent_period
    has_line_item_late_fees = False
    rent_period_fees = crt_rent_period.rent_period_fees
    drop_off_fee = 0
    for fee in rent_period_fees:
        if fee.type.name == 'DROP_OFF' or fee.type.name == 'PICK_UP':
            drop_off_fee += fee.fee_amount

    late_fees = []
    for fee in rent_period_fees:
        if fee.type.name == 'LATE':
            late_fees.append({"date": fee.created_at})

    total_line_items = 0
    for line_item in order.line_items:
        total_line_items += line_item.monthly_owed
    total_line_items += drop_off_fee

    fees_to_display_line_item = {}

    for fee in rent_period_fees:
        if fee.type.line_item_level:
            if fee.type.name not in fees_to_display_line_item:
                fees_to_display_line_item[fee.type.name] = fee.fee_amount
            else:
                fees_to_display_line_item[fee.type.name] += fee.fee_amount
            # Checking this at the line item level to decide if to show the late fee header or not
            if fee.type.name == 'LATE' and fee.fee_amount > 0:
                has_line_item_late_fees = True

    late_fee_header = ""
    if late_fees and has_line_item_late_fees:
        dates = [fee["date"] for fee in late_fees]
        earliest_date = min(dates).strftime("%m/%d/%y")
        latest_date = max(dates).strftime("%m/%d/%y")

        late_fee_header = f"Late fees {earliest_date} - {latest_date}"

    for line_item in order.line_items:
        rental_line_item = {}
        rental_line_item['shipping_container'] = (
            line_item.title + " " + (line_item.inventory.container_number if line_item.inventory else " ")
        )
        rental_line_item['delivery_from'] = line_item.location
        rental_line_item['delivery_to'] = (
            line_item.container_address
            if line_item.container_address != ""
            else f"{order.address.city}, {order.address.state}"
        )
        rental_line_item['drop_off_pickup'] = drop_off_fee / len(order.line_items)
        if order.first_payment_strategy.upper() == "FIRST_MONTH_PLUS_DELIVERY":
            rental_line_item['drop_off'] = drop_off_fee / len(order.line_items)
            rental_line_item['pick_up'] = 0
        else:
            rental_line_item['drop_off'] = drop_off_fee / len(order.line_items) / 2
            rental_line_item['pick_up'] = drop_off_fee / len(order.line_items) / 2

        rental_line_item['monthly_rent'] = line_item.monthly_owed

        rental_line_item['tax'] = (
            Decimal(crt_rent_period.calculated_rent_period_tax)
            * (Decimal(line_item.monthly_owed) + Decimal(drop_off_fee) / Decimal(len(order.line_items)))
            / Decimal(total_line_items)
        )
        rental_line_item['total'] = (
            Decimal(rental_line_item['monthly_rent'])
            + Decimal(rental_line_item['drop_off_pickup'])
            + Decimal(rental_line_item['tax'])
        )
        for fee_name, fee_value in fees_to_display_line_item.items():
            rental_line_item[fee_name] = fee_value / len(order.line_items)
        rental_line_items.append(rental_line_item)

    totals = []
    freight_fees = 0
    for fee in rent_period_fees:
        if fee.type.name == 'DROP_OFF' or fee.type.name == 'PICK_UP':
            freight_fees += fee.fee_amount

    fees_to_display_summary = {}
    for fee in rent_period_fees:
        if fee.type.display_name not in fees_to_display_line_item:
            if fee.type.display_name not in fees_to_display_summary:
                fees_to_display_summary[fee.type.display_name] = fee.fee_amount
            else:
                fees_to_display_summary[fee.type.display_name] += fee.fee_amount

    totals.append({"name": "Freight subtotal", "value": freight_fees})
    for fee_key, fee_value in fees_to_display_summary.items():
        if fee_key != "Delivery" and fee_key != "Pick Up" and fee_key != '':
            totals.append({"name": fee_key, "value": fee_value})
    totals.append({"name": "Rent Subtotal", "value": sum([x['monthly_rent'] for x in rental_line_items])})
    totals.append({"name": "Tax", "value": sum([x['tax'] for x in rental_line_items])})

    account = await account_crud.get_one(order.account_id)
    show_combined = account.cms_attributes['rent_options'].get('show_combined_drop_off_pick_up', False)
    return {
        "rental_line_items": rental_line_items,
        "rental_totals": totals,
        "show_combined": show_combined,
        "late_fee_header": late_fee_header,
        "remaining_balance": crt_rent_period.calculated_rent_period_total_balance,
        "period": crt_rent_period,
        "columns_data": get_visible_columns_and_data(
            {'show_combined': show_combined, 'late_fee_header': late_fee_header, 'visibleColumns': []},
            rental_line_items,
        ),
        'subtotals': filter_subtotals(totals),
    }


async def generate_rental_invoice_pdf_docugenerate(order_id: str, rent_period_id: str) -> str:
    order = await order_crud.get_one(order_id)
    account = await account_crud.get_one(order.account_id)
    cms_attributes = account.cms_attributes
    account_name = cms_attributes.get("account_name", "")

    order_dict = order.dict()
    logos = cms_attributes.get("logo_settings", {})

    notes = await get_notes(order_dict, order_id, cms_attributes)

    days_to_add = cms_attributes.get("grace_period", 5)

    addr_dict = parse_address(cms_attributes.get("company_mailing_address", ""))
    company_city_state_zip = f"{addr_dict.get('city') }, { addr_dict.get('state') }, { addr_dict.get('zip') }"

    table_data = await generate_web_rental_order_table_data(order, rent_period_id)
    current_due = fc(table_data['remaining_balance'])
    order = order.dict()
    customer_name = (
        order.get("customer", {}).get("full_name", "")
        if order.get("customer")
        else order.get("single_customer", {}).get("calculated_name", "")
    )

    if order.get("single_customer"):
        customer_contact = order.get("customer_contacts", [{}])[0]
        customer_address = customer_contact.get("customer_address", {})
        customer_street_address = customer_address.get("street_address", "")
        customer_city_state_zip = f"{customer_address.get('city', '')}, {customer_address.get('state', '')}, {customer_address.get('zip', '')}".strip().replace(
            "'", ""
        )
    else:
        customer_street_address = order.get("address", {}).get("full_address", "")
        customer_city_state_zip = company_city_state_zip

    no = selected_rent_period_number(order, rent_period_id)
    column_titles, line_items, column_titles_fields = table_data['columns_data']
    invoice = PdfGeneratorRentalInvoice(
        api_key=account.integrations.get("docugenerate_api_key"),
        logo="https://fluffy-jelly-0cb624.netlify.app" + logos.get("logo_path", ""),
        title=f"INVOICE {order.get('display_order_id', None)}-{no}",
        order_id=order.get("display_order_id", None) + no,
        created_on=order.get("created_at"),
        due_date=(order.get("created_at") + timedelta(days=days_to_add)),
        po_num=order.get('purchase_order_number', ''),
        po_job_id=order.get('purchased_order_job_id', ''),
        balance_due=order.get('total_due'),
        company_name=account_name,
        company_street=addr_dict.get("street"),
        company_city_state_zip=company_city_state_zip,
        company_phone=cms_attributes.get("quote_contact_phone", ""),
        customer_name=customer_name,
        customer_billing_street=customer_street_address,
        customer_billing_city_state_zip=customer_city_state_zip,
        delivery_address=order.get("address", {}).get("full_address", ""),
        sub_total=order.get("calculated_sub_total_without_fees", 0),
        tax=order.get("calculated_order_tax", 0),
        total=order.get("calculated_total_price", 0),
        total_paid=order.get('total_paid', 0),
        main_notes=notes,
        additional_notes="",
        current_due=current_due,
        line_items=line_items,
        column_title=column_titles,
        visible_columns=len(column_titles[0]),
        subtotals=table_data['subtotals'],
        paid_on_txt=(
            f"Paid on {last_payment_date(table_data['period'])}"
            if table_data['remaining_balance'] == Decimal(0)
            else ""
        ),
        order_dates=rent_period_dates(order, table_data['period']),
    )

    return await invoice.download()


async def generate_order_pdf_docugenerate(order: Order, order_id: str) -> str:
    order = await order_crud.get_one(order_id)
    account = await account_crud.get_one(order.account_id)
    cms_attributes = account.cms_attributes
    account_name = account.name

    if account_name == 'Amobilebox':
        account_name = 'AMobileBox'

    order = order.dict()
    logos = cms_attributes.get("logo_settings", {})

    notes = await get_notes(order, order_id, cms_attributes)

    days_to_add = cms_attributes.get("grace_period", 5)

    addr_dict = parse_address(cms_attributes.get("company_mailing_address", ""))
    company_city_state_zip = f"{addr_dict.get('city') }, { addr_dict.get('state') }, { addr_dict.get('zip') }"
    customer_name = (
        order.get("customer", {}).get("full_name", "")
        if order.get("customer")
        else order.get("single_customer", {}).get("full_name", "")
    )

    invoice = PdfGeneratorPurchaseInvoice(
        api_key=account.integrations.get("docugenerate_api_key"),
        logo="https://fluffy-jelly-0cb624.netlify.app" + logos.get("logo_path", ""),
        title=f"{'INVOICE' if order.get('paid_at') is None else 'RECEIPT'}",
        order_id=order.get("display_order_id", None),
        created_on=order.get("created_at"),
        due_date=(order.get("created_at") + timedelta(days=days_to_add)),
        po_num=order.get('purchase_order_number', ''),
        po_job_id=order.get('purchased_order_job_id', ''),
        balance_due=(
            order.get('calculated_remaining_order_balance')
            if order.get('type') in ["PURCHASE", "PURCHASE_ACCESSORY", "RENT_TO_OWN"]
            else order.get('total_due')
        ),
        company_name=account_name,
        company_street=addr_dict.get("street"),
        company_city_state_zip=company_city_state_zip,
        company_phone=cms_attributes.get("quote_contact_phone", ""),
        customer_name=customer_name,
        customer_billing_street=order.get("address", {}).get("full_address", ""),
        delivery_address=order.get("address", {}).get("full_address", ""),
        sub_total=order.get("calculated_sub_total_without_fees", 0),
        tax=order.get("calculated_order_tax", 0),
        total=order.get("calculated_total_price", 0),
        total_paid=order.get('total_paid', 0),
        transactions_present=len(prepare_transactions(order)) > 0,
        transactions=prepare_transactions(order),
        main_notes=notes,
        additional_notes="",
        items=[
            {
                'name': line_item.get("abrev_title")
                + " "
                + (
                    order.get("address", {}).get("full_address", "")
                    if not line_item.get("inventory_address")
                    else line_item.get("inventory_address")[0].get('full_address_computed')
                ),
                'quantity': 1,
                'unit_cost': fetch_item_unit_cost(
                    order, line_item, cms_attributes.get("rent_options").get("down_payment_strategy", "")
                ),
                # 'description': line_item.get("inventory", {}).get("container_number", "")
            }
            for line_item in order.get("line_items", [])
        ],
    )

    if order.get("calculated_discount") > 0.00:
        invoice.add_item(name='Applied Discount', quantity=1, unit_cost=order.get("calculated_discount") * -1)

    if order.get("calculated_fees") > 0.00:
        for fee in order.get("fees", []):
            invoice.add_item(
                name=f'{ fee.get("type", {}).get("name") } Fee ({ "Taxable" if fee.get("type", {}).get("is_taxable") else "Not Taxable" })',
                quantity=1,
                unit_cost=fee.get("fee_amount"),
            )

    return await invoice.download()


def fetch_item_unit_cost(order, line_item, down_payment_strategy) -> Decimal:
    if order.get('type') != "RENT":
        return line_item.get("calculated_total_revenue")
    # Shipping makes up the down/first payment so there is no need to add it again
    # shipping = line_item.get("shipping_revenue")
    # if down_payment_strategy == "DELIVERY_PLUS_PICKUP_PLUS_FIRST_MONTH" :
    # shipping = shipping * 2 # Delivery and pickup are the same and separated based on payment strategy
    return line_item.get("monthly_owed")  # + shipping


async def get_order_by_rent_period_id(rent_period_id, user):
    rent_period = await rent_period_crud.get_one(rent_period_id)

    order = await order_crud.get_one(rent_period.order_id)
    return order


@atomic()
async def duplicate_order(order_id, user):
    existing_order: Order = await order_crud.get_one(order_id)
    account = await account_crud.get_one(existing_order.account_id)
    selected_order_id = await get_order_id(account)

    clone_order_db = OrderIn(
        status=existing_order.status,
        account_id=existing_order.account_id,
        customer_id=existing_order.customer.id,
        display_order_id=selected_order_id,
        type=existing_order.type,
        attributes=existing_order.attributes,
        address_id=existing_order.address.id,
        billing_address_id=existing_order.billing_address.id,
        user_id=user.id.replace("auth0|", ""),
        payment_type=existing_order.payment_type,
        delivered_at=existing_order.delivered_at,
        paid_at=existing_order.paid_at,
        allow_external_payments=existing_order.allow_external_payments,
        credit_card_fee=existing_order.credit_card_fee,
        rent_due_on_day=existing_order.rent_due_on_day or None,
        is_autopay=existing_order.is_autopay,
        first_payment_strategy=existing_order.first_payment_strategy,
        tax_exempt=existing_order.tax_exempt,
        processing_flat_cost=existing_order.processing_flat_cost,
        processing_percentage_cost=existing_order.processing_percentage_cost,
        charge_per_line_item=existing_order.charge_per_line_item,
        applications_overridden=existing_order.applications_overridden,
    )

    saved_order: Order = await order_crud.create(clone_order_db)

    for line_item in existing_order.line_items:
        new_line_item = LineItemIn(
            scheduled_date=line_item.scheduled_date,
            potential_date=line_item.potential_date,
            delivery_date=line_item.delivery_date,
            minimum_shipping_cost=line_item.minimum_shipping_cost,
            potential_dollar_per_mile=line_item.potential_dollar_per_mile,
            potential_miles=line_item.potential_miles,
            product_cost=line_item.product_cost,
            revenue=line_item.revenue,
            shipping_revenue=line_item.shipping_revenue,
            shipping_cost=line_item.shipping_cost,
            tax=line_item.tax,
            potential_driver_charge=line_item.potential_driver_charge,
            convenience_fee=line_item.convenience_fee,
            good_to_go=line_item.good_to_go,
            welcome_call=line_item.welcome_call,
            pickup_email_sent=line_item.pickup_email_sent,
            missed_delivery=line_item.missed_delivery,
            door_orientation=line_item.door_orientation,
            product_city=line_item.product_city,
            product_state=line_item.product_state,
            container_size=line_item.container_size,
            condition=line_item.condition,
            rent_period=line_item.rent_period,
            interest_owed=line_item.interest_owed,
            total_rental_price=line_item.total_rental_price,
            monthly_owed=line_item.monthly_owed,
            attributes=line_item.attributes,
            inventory_id=line_item.inventory.id if line_item.inventory else None,
            other_inventory_id=line_item.other_inventory.id if line_item.other_inventory else None,
            driver_id=line_item.driver.id if line_item.driver else None,
            product_type=line_item.product_type,
            other_product_name=line_item.other_product_name,
            other_product_shipping_time=line_item.other_product_shipping_time,
            potential_driver_id=line_item.potential_driver.id if line_item.potential_driver else None,
            order_id=saved_order.id,
        )

        if line_item.product_type == "CONTAINER_ACCESSORY":
            other_product = await other_product_crud.get_one(user.app_metadata.get("account_id"), line_item.product_id)
            await line_item_crud.saveWithAccessory(
                new_line_item,
                CreateAccessoryLineItem(
                    id=str(uuid.uuid4()),
                    product_type=line_item.product_type,
                    other_product_name=line_item.other_product_name,
                    other_product_shipping_time=line_item.other_product_shipping_time,
                    filename=(
                        other_product.file_upload[0].filename
                        if other_product.file_upload is not None and len(other_product.file_upload) > 0
                        else None
                    ),
                    content_type=(
                        other_product.file_upload[0].content_type
                        if other_product.file_upload is not None and len(other_product.file_upload) > 0
                        else None
                    ),
                    folder_type=(
                        other_product.file_upload[0].folder_type
                        if other_product.file_upload is not None and len(other_product.file_upload) > 0
                        else None
                    ),
                    other_product_id=other_product.id,
                ),
            )
        else:
            await line_item_crud.create(new_line_item)

    if saved_order.type == "RENT":

        rent_options: dict = account.cms_attributes.get("rent_options", {})
        drop_off = 0
        pick_up = 0
        for fee in existing_order.rent_periods[0].rent_period_fees:
            if fee.type.name == "DROP_OFF":
                drop_off = fee.fee_amount
            elif fee.type.name == "PICK_UP":
                pick_up = fee.fee_amount

        create_initial_rent_period = True
        if create_initial_rent_period:
            await rent_period_controller.handle_initial_rent_period(
                saved_order.id, user, rent_options, quick_rent=False, drop_off=drop_off, pickup=pick_up
            )

        return saved_order
    else:
        # if the front end has said that there is tax, then we will run our calculation
        if saved_order.tax_exempt is False and account.cms_attributes.get("charge_tax", True):
            if existing_order.calculated_order_tax != 0:
                try:
                    await handle_order_tax(
                        saved_order.id,
                        user.app_metadata.get("account_id"),
                        flat_tax=existing_order.calculated_order_tax,
                        quick_sale_override_tax=True,
                    )
                except Exception as e:
                    logger.info(f"Something went wrong with the handle_order_tax: {e}")
                    raise (e)

        order = await order_crud.get_one(saved_order.id)
        try:
            await handle_initial_order_balance(order, account, True)
        except Exception as e:
            logger.error(f"Something went wrong with the handle_initial_order_balance: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")

        await handle_initial_subtotal_balance(order, account, False)


async def calculate_remaining_balance(data: Dict[Any, Any], order_id):
    order = await order_crud.get_one(order_id)
    data_li = list(data.keys())[0]
    moved_out_date = datetime.fromisoformat(data[data_li].replace('Z', '+00:00'))

    s = 0  # Initialize total balance

    # Loop through rent periods to calculate the balance owed
    for rp in order.rent_periods:
        # Add the balance and fee for all past periods
        if rp.start_date < datetime.now(timezone.utc):
            # If the period ends before the move-out date, it is fully owed
            if rp.end_date < moved_out_date:
                s += rp.calculated_rent_period_total_balance
            # If the period overlaps or starts after the move-out date, skip it
            elif rp.start_date >= moved_out_date:
                continue
            # If the move-out date falls within the period, add the full balance and fee
            else:
                s += rp.calculated_rent_period_total_balance

    return s


async def transactions_rent_periods(start_date, end_date, display_order_id, user):
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    order: Order = await order_crud.get_one_by_display_id(user.app_metadata['account_id'], display_order_id)

    s = Decimal(0)
    pickup_substracted = False
    dropoff_substracted = False
    for rp in order.rent_periods:
        logger.info(len(rp.transaction_type_rent_period))
        for tt in rp.transaction_type_rent_period:
            s += Decimal(tt.amount)
            for fee in rp.rent_period_fees:
                if fee.type.name == 'PICK_UP' and not pickup_substracted:
                    s -= Decimal(fee.fee_amount)
                    pickup_substracted = True

                if fee.type.name == 'DROP_OFF' and not dropoff_substracted:
                    s -= Decimal(fee.fee_amount)
                    dropoff_substracted = True

    return s


async def get_orders(ids, auth_user):
    return await order_crud.get_by_ids(auth_user.app_metadata['account_id'], ids)


async def get_exported_orders(order_status, order_type, emulated_user_id, auth_user, pagination, displayOrderIds):
    can_read_all = len([p for p in auth_user.permissions if p == "read:all_orders"])
    user_ids = None
    if not can_read_all:
        user_ids = await get_user_ids(
            auth_user.app_metadata["account_id"],
            auth_user.id.replace("auth0|", ""),
            includeManager=True,
        )
    if emulated_user_id and len([p for p in auth_user.permissions if p == "emulate:users"]):
        user_ids = await get_user_ids(
            auth_user.app_metadata["account_id"],
            emulated_user_id,
            includeManager=True,
        )

    # ensure order status looks like first letter capatilized
    if "_" in order_status:
        order_status_words: list[str] = order_status.split('_')
        for i, word in enumerate(order_status_words):
            order_status_words[i] = word.capitalize()

        order_status = "_".join(order_status_words)
    else:
        order_status = order_status.capitalize()

    if displayOrderIds:
        order_result = await exported_order_crud.get_by_display_order_ids(
            auth_user.app_metadata["account_id"], displayOrderIds, user_ids
        )
    else:
        order_result = await exported_order_crud.get_by_status_type(
            auth_user.app_metadata["account_id"], order_status, order_type, user_ids, pagination
        )

    return order_result
