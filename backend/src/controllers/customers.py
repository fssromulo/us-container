# Python imports
import base64
import json
import logging
import os
import random
import uuid
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Union

# Pip imports
import requests
from dateutil.relativedelta import relativedelta
from fastapi import BackgroundTasks, HTTPException, status
from tortoise import Model
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import account as account_controller
from src.controllers import fee_controller
from src.controllers import inventory as inventory_controller
from src.controllers import misc_costs as misc_costs_controller
from src.controllers import orders as order_controller
from src.controllers import rent_period as rent_period_controller
from src.controllers import transaction_type as transaction_type_controller
from src.controllers.event_controller import as_is_event, send_event
from src.controllers.payment import (
    credit_card_payment_purchase_public,
    handle_other_payment,
    handle_quick_rent_period_generation,
)
from src.crud.account_crud import account_crud
from src.crud.address_crud import address_crud
from src.crud.customer_contact_crud import customer_contact_crud
from src.crud.customer_crud import CustomerCRUD
from src.crud.line_item_crud import line_item_crud
from src.crud.location_price_crud import location_price_crud
from src.crud.note_crud import note_crud
from src.crud.order_crud import OrderCRUD
from src.crud.order_id_counter_crud import order_id_counter_crud
from src.crud.order_tax_crud import order_tax_crud
from src.crud.other_product_crud import other_product_crud
from src.crud.partial_order_crud import partial_order_crud
from src.crud.single_customer_crud import single_customer_crud
from src.crud.subtotal_balance_crud import subtotal_balance_crud
from src.crud.tax_balance_crud import tax_balance_crud
from src.crud.tax_crud import tax_crud
from src.crud.total_order_balance_crud import total_order_balance_crud
from src.crud.transaction_type_crud import transaction_type_crud
from src.database.models.account import Account
from src.database.models.orders.line_item import LineItem
from src.database.models.orders.order import Order
from src.schemas.acccessory_line_items import AccessoryLineItemOut, CreateAccessoryLineItem
from src.schemas.address import AddressIn, CreateAddress
from src.schemas.customer import CreateCustomerOrder, CustomerIn, UpdateCustomerOrder
from src.schemas.customer_contact import (
    CreateCustomerContact,
    CustomerContactIn,
    EditCustomerContact,
    NewCustomerContact,
)
from src.schemas.customer_simple import CreateCustomer, CustomerProfileIn
from src.schemas.fee import FeeIn
from src.schemas.line_items import CreateLineItem, LineItemIn, LineItemInUpdate
from src.schemas.misc_cost import MiscCostIn
from src.schemas.notes import NoteInSchema
from src.schemas.order_id_counter import OrderIdCounterUpdate
from src.schemas.order_tax import OrderTaxIn, OrderTaxOut
from src.schemas.orders import CreateOrder, CreateUpdateAddress, OrderIn, OrderInUpdate
from src.schemas.payment import OtherPayment, QuickRent, QuickSalePayObj, QuickSalePayment
from src.schemas.subtotal_balance import SubtotalBalanceIn
from src.schemas.tax_balance import TaxBalanceIn
from src.schemas.total_order_balance import TotalOrderBalanceIn, TotalOrderBalanceOut
from src.schemas.transaction_type import TransactionTypeIn
from src.services.orders.address import save_address
from src.utils.generate_processing_cost import generate_processing_cost_options
from src.utils.update_cache import prepare_order_cache_swap
from src.utils.utility import make_json_serializable


logger = logging.getLogger(__name__)

customer_crud = CustomerCRUD()
order_crud = OrderCRUD()
BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")

NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND)


def get_random_number(start: int, end: int) -> int:
    return random.randint(start, end)


async def get_single_customer(customer_id: str, user: Auth0User) -> Model:
    try:
        return await single_customer_crud.get_one(user.app_metadata['account_id'], customer_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")


async def get_customer(customer_id: str, user: Auth0User) -> Model:
    try:
        return await customer_crud.get_latest(user.app_metadata["account_id"], customer_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")


async def save_line_item(
    line_item: CreateLineItem, account_id: int, order_id: int, user_id: str = None, line_item_id: str = None
) -> Model:
    note = None
    if hasattr(line_item, 'note'):
        note = line_item.note
        del line_item.note
    saved_line_item = None
    line_item_dict = line_item.dict(exclude_unset=True)
    line_item_dict["order_id"] = order_id
    line_item_dict["good_to_go"] = "NO"
    line_item_dict["welcome_call"] = "NO"
    if (
        line_item_dict["product_type"] is None
        or line_item_dict["product_type"] == ""
        or line_item_dict["product_type"] == "SHIPPING_CONTAINER"
    ):
        line_item_dict.pop("product_id")
        line_item_dict["product_type"] = "CONTAINER"
        if line_item_id:
            saved_line_item = await line_item_crud.update(account_id, line_item_id, LineItemInUpdate(**line_item_dict))
        else:
            saved_line_item = await line_item_crud.create(LineItemIn(**line_item_dict))
    elif line_item_dict["product_type"] == "CONTAINER_ACCESSORY":
        other_product = await other_product_crud.get_one(account_id, line_item_dict["product_id"])
        line_item_dict['other_product_name'] = other_product.name
        line_item_dict['other_product_shipping_time'] = other_product.shipping_time
        line_item_dict['product_cost'] = other_product.price
        line_item_dict.pop("product_id")
        line_item_dict.pop("door_orientation")
        if line_item_id:
            saved_line_item = await line_item_crud.update(account_id, line_item_id, LineItemInUpdate(**line_item_dict))
        else:
            print(other_product)
            saved_line_item = await line_item_crud.saveWithAccessory(
                LineItemIn(**line_item_dict),
                CreateAccessoryLineItem(
                    id=str(uuid.uuid4()),
                    product_type=line_item_dict["product_type"],
                    other_product_name=line_item_dict["other_product_name"],
                    other_product_shipping_time=line_item_dict["other_product_shipping_time"],
                    filename=other_product.file_upload[0].filename
                    if other_product.file_upload is not None and len(other_product.file_upload) > 0
                    else None,
                    content_type=other_product.file_upload[0].content_type
                    if other_product.file_upload is not None and len(other_product.file_upload) > 0
                    else None,
                    folder_type=other_product.file_upload[0].folder_type
                    if other_product.file_upload is not None and len(other_product.file_upload) > 0
                    else None,
                    other_product_id=str(other_product.id),
                ),
            )
    if note:
        await note_crud.create(
            NoteInSchema(
                title=note.title,
                content=note.content,
                author_id=user_id,
                line_item_id=saved_line_item.id,
            )
        )

    return saved_line_item


async def save_customer(
    customer: CreateCustomerOrder, account_id: int, customer_id: str = None, user_id: str = None
) -> Model:
    note = None
    if hasattr(customer, 'note'):
        note = customer.note
        del customer.note

    if hasattr(customer, 'order'):
        del customer.order

    customer_dict = customer.dict(exclude_unset=True)

    customer_dict["account_id"] = account_id

    if customer_id:
        saved_customer = await customer_crud.update(account_id, customer_id, CustomerIn(**customer_dict))
    else:
        if not customer_dict.get('email'):
            customer_dict[
                'email'
            ] = f"{customer_dict.get('first_name')}.{customer_dict.get('last_name')}.{customer_dict.get('phone')[1:4]}@fake_email.com"
        saved_customer = await customer_crud.create(CustomerIn(**customer_dict))

    if note and note.title and note.content:
        await note_crud.create(
            NoteInSchema(
                title=note.title,
                content=note.content,
                author_id=user_id,
                customer_id=saved_customer.id,
            )
        )

    return saved_customer


async def save_customer_profile(customer: CreateCustomer, account_id: int, customer_id: str = None) -> Model:
    customer_dict = customer.dict(exclude_unset=True)

    customer_dict["account_id"] = account_id

    if customer_id:
        saved_customer = await single_customer_crud.update(account_id, customer_id, CustomerProfileIn(**customer_dict))
    else:
        saved_customer = await single_customer_crud.create(CustomerProfileIn(**customer_dict))

    return saved_customer


async def get_order_id(account):
    if account.id == 5:
        order_id_counter_list = await order_id_counter_crud.get_all(1)
    else:
        order_id_counter_list = await order_id_counter_crud.get_all(account.id)
    order_id_item = order_id_counter_list[0]
    order_id_count = order_id_item.order_id

    found_id = False

    while not found_id:
        try:
            if account.id == 5:
                await order_crud.get_one_by_display_id(1, order_id_count)
            else:
                await order_crud.get_one_by_display_id(account.id, order_id_count)
        except Exception as e:
            logger.debug(f"id doesn't exist, proceed: {e}")
            break
        else:
            logger.debug("id exists, increment")
            order_id_count += 1

    logger.debug(f"final order id {order_id_count}")
    year_prefixed = (
        account.cms_attributes.get("feature_flags", {}).get("order_id_configuration", {}).get("has_year_prefix")
    )
    selected_order_id = None
    if year_prefixed:
        current_year = datetime.now().strftime("%y")
        selected_order_id = f"{current_year}-{order_id_count}"
    if account.cms_attributes.get("feature_flags", {}).get("order_id_configuration", {}).get("other_prefix", '') != "":
        other_prefix = (
            account.cms_attributes.get("feature_flags", {}).get("order_id_configuration", {}).get("other_prefix", '')
        )
        selected_order_id = f"{other_prefix}-{selected_order_id if selected_order_id is not None else order_id_count}"

    if account.id == 5:
        await order_id_counter_crud.update(
            1, order_id_item.id, OrderIdCounterUpdate(order_id=order_id_count + 1, account_id=1)
        )
    else:
        await order_id_counter_crud.update(
            account.id, order_id_item.id, OrderIdCounterUpdate(order_id=order_id_count + 1, account_id=account.id)
        )

    return selected_order_id or order_id_count


async def handle_initial_tax_balance(
    order: Order, account: Account, remaining_balance_is_zero: bool = False, tax_rate=0
) -> None:
    order_remaining_balance: Decimal = 0
    order_remaining_balance = order.calculated_order_tax if not remaining_balance_is_zero else 0

    create_tax_balance: TaxBalanceIn = TaxBalanceIn(
        balance=order_remaining_balance, order_id=order.id, tax_rate=tax_rate
    )
    await tax_balance_crud.create(create_tax_balance)
    return


async def handle_initial_subtotal_balance(
    order: Order, account: Account, remaining_balance_is_zero: bool = False
) -> None:
    order_remaining_balance: Decimal = 0
    order_remaining_balance = order.calculated_sub_total_without_fees if not remaining_balance_is_zero else 0

    create_tax_balance: SubtotalBalanceIn = SubtotalBalanceIn(balance=order_remaining_balance, order_id=order.id)
    await subtotal_balance_crud.create(create_tax_balance)
    return


async def handle_initial_order_balance(order: Order, account: Account, remaining_balance_is_zero: bool = False) -> None:
    """
    Create the order balance based on the provided order and line items.

    This function calculates the remaining balance for an order based on the provided
    order object and line items. If any of the line items have the 'monthly_owed' property
    populated, it is considered a rent-to-own (RTO) item, and the remaining balance is
    calculated as the sum of the 'monthly_owed' values from those items. If none of the
    line items have 'monthly_owed' values, the remaining balance is set to the total
    price of the order.

    Args:
        order (Order): The order object.
        line_items (list[LineItem]): List of line items associated with the order.

    Returns:
        None: The function updates the order balance and creates an order balance record.

    """
    # rent_enabled = account.cms_attributes.get("feature_flags", {}).get("rent", {}).get("enabled")
    # downpayment_strategy = account.cms_attributes.get("rent_options", {}).get("down_payment_strategy", {})
    order_remaining_balance: Decimal = 0
    if order.type == "PURCHASE" or order.type == 'PURCHASE_ACCESSORY':
        order_remaining_balance = order.calculated_total_price if not remaining_balance_is_zero else 0
    # if order.type == "RENT":
    #     if downpayment_strategy == "DELIVERY_PLUS_PICKUP_PLUS_FIRST_MONTH":
    #         order_remaining_balance: Decimal = order.calculated_monthly_owed_total + (
    #             order.calculated_shipping_revenue_total * 2
    #         )
    if order.type == "RENT_TO_OWN":
        # change this to be the total of the monthly owed items
        order_remaining_balance = order.calculated_total_price if not remaining_balance_is_zero else 0

    create_order_balance: TotalOrderBalanceIn = TotalOrderBalanceIn(
        remaining_balance=order_remaining_balance, order_id=order.id
    )
    create_order_balance: TotalOrderBalanceOut = await total_order_balance_crud.create(create_order_balance)


async def handle_order_tax(
    order_id: str,
    account_id: int,
    flat_tax: Decimal = None,
    quick_sale_override_tax: bool = False,
) -> OrderTaxOut:
    existing_order: Order = await order_crud.get_one(order_id)
    account: Account = await account_controller.get_account_by_id(account_id)
    avalara_int = account.integrations.get("avalara", {})

    if avalara_int:
        avalara_api_url = avalara_int.get("url")
        username = avalara_int.get("account")
        password = avalara_int.get("license_key")
        now = datetime.now()

        formatted_date = now.strftime("%Y-%m-%d")

        fromCity, fromState = "", ""
        if existing_order.line_item_length > 0:
            fromCity = existing_order.line_items[0].product_city
            fromState = existing_order.line_items[0].product_state

        loc = await location_price_crud.get_by_city(fromCity, account_id)

        transaction = {
            "type": "SalesOrder",
            "companyCode": "DEFAULT",
            "date": formatted_date,
            "customerCode": "ABC",
            "addresses": {
                "shipFrom": {
                    "line1": "",
                    "city": fromCity,
                    "region": fromState,
                    "country": "US",
                    "postalCode": loc.zip,
                },
                "shipTo": {
                    "line1": existing_order.address.street_address,
                    "city": existing_order.address.city,
                    "region": existing_order.address.state,
                    "country": "US",
                    "postalCode": existing_order.address.zip,
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
            timeout=10,
        )

        if response.status_code == 201:
            transaction_data = response.json()
            total_tax = transaction_data['totalTax']
            total_amount = transaction_data['totalAmount']
            tax_rate = (total_tax / total_amount) if total_amount != 0 else 0
        else:
            raise Exception(f"Can't calculate order tax rate from avalara: {response.text}")
    else:
        tax_states = [
            li.inventory.container_inventory_address.state
            for li in existing_order.line_items
            if li.inventory and li.inventory.container_inventory_address
        ]
        if not tax_states:
            tax_states = [existing_order.address.state]

        if tax_states:
            tax_rate = await tax_crud.get_tax_rate(account_id, tax_states[0])
        else:
            tax_rate = 0.0

    tax_amt: Decimal = Decimal(existing_order.calculated_sub_total_price) * Decimal(tax_rate)
    order_tax: Decimal = Decimal(tax_amt.quantize(Decimal(".01"), rounding=ROUND_HALF_UP))

    if quick_sale_override_tax:
        order_tax = flat_tax

        if existing_order.calculated_sub_total_price != 0:
            tax_rate = Decimal(flat_tax) / Decimal(existing_order.calculated_sub_total_price)

    create_order_tax = OrderTaxIn(tax_amount=order_tax, order_id=existing_order.id)
    created_order_tax: OrderTaxOut = await order_tax_crud.create(create_order_tax)

    existing_order = await order_crud.get_one(existing_order.id)

    await handle_initial_tax_balance(existing_order, account, False, tax_rate)
    return created_order_tax


async def handle_order_creation_logic(
    order_db: OrderIn,
    line_items: List[LineItem],
    user: Auth0User,
    order_configuration: dict,
    remaining_balance_is_zero: bool,
    order: CreateOrder,
    account: Account,
    quick_sale_override_tax: bool = False,
    note=None,
    quick_rent=False,
    drop_off=0,
    pickup=0,
    background_tasks=None,
) -> Order:
    saved_order: Order = await order_crud.create(order_db)

    if note:
        if order.note and len(order.note.content) != 0:
            order_note_db = NoteInSchema(
                title=note.title,
                content=note.content,
                author_id=user.id.replace("auth0|", ""),
                order_id=saved_order.id,
            )
            await note_crud.create(order_note_db)

    if order.note:
        if len(order.note.content) != 0:
            order_note_db = NoteInSchema(
                title=order.note.title,
                content=order.note.content,
                author_id=user.id.replace("auth0|", ""),
                order_id=saved_order.id,
            )
            await note_crud.create(order_note_db)

    if line_items:
        [await save_line_item(line_item, account.id, saved_order.id, user) for line_item in line_items]

    if saved_order.type == "RENT":

        account: Account = await account_controller.get_account(user)
        rent_options: dict = account.cms_attributes.get("rent_options", {})
        create_initial_rent_period = order_configuration.get("create_initial_rent_period", True)
        if create_initial_rent_period:
            await rent_period_controller.handle_initial_rent_period(
                saved_order.id, user, rent_options, quick_rent=quick_rent, drop_off=drop_off, pickup=pickup
            )

        return saved_order
    else:
        # if the front end has said that there is tax, then we will run our calculation
        if saved_order.tax_exempt is False and account.cms_attributes.get("charge_tax", True):
            if order.tax != 0:
                try:
                    await handle_order_tax(
                        saved_order.id,
                        user.app_metadata.get("account_id"),
                        flat_tax=order.tax,
                        quick_sale_override_tax=quick_sale_override_tax,
                    )
                except Exception as e:
                    logger.info(f"Something went wrong with the handle_order_tax: {e}")
                    raise (e)

        order = await order_crud.get_one(saved_order.id)
        try:
            await handle_initial_order_balance(order, account, remaining_balance_is_zero)
        except Exception as e:
            logger.error(f"Something went wrong with the handle_initial_order_balance: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")

        await handle_initial_subtotal_balance(order, account, False)

        # send event to event controller
        background_tasks.add_task(
            send_event, order.account_id, str(order.id), make_json_serializable(order.dict()), "order", "create"
        )
    return order


async def create_generic_customer(
    customer: CreateCustomerOrder,
    account: Account,
    user: Auth0User,
    order_configuration: Dict[str, str] = {},
    background_tasks: BackgroundTasks = None,
) -> Model:
    remaining_balance_is_zero = order_configuration.get("remaining_balance_is_zero", False)
    order: CreateOrder = customer.order
    line_items: List[LineItem] = getattr(order, 'line_items', None)
    order_status = order.status
    order_address = getattr(order, 'address', None)
    billing_address = getattr(order, 'billing_address', None)

    saved_customer = await save_customer(customer, account.id)
    saved_address = await save_address(order_address)
    if billing_address:
        billing_address = await save_address(billing_address)

    if getattr(saved_customer, 'note', None):
        if len(order.note.content.strip()) != 0:
            customer_note_db = NoteInSchema(
                title=order.note.title,
                content=order.note.content,
                author_id=user.id.replace("auth0|", ""),
                customer_id=saved_customer.id,
            )
            await note_crud.create(customer_note_db)

    if getattr(order, 'note', None):
        if len(order.note.content.strip()) != 0:
            order_note_db = NoteInSchema(
                title=order.note.title,
                content=order.note.content,
                author_id=user.id.replace("auth0|", ""),
            )
            await note_crud.create(order_note_db)

    selected_order_id = await get_order_id(account)

    default_external_payment = account.cms_attributes.get("default_external_payments", True)

    credit_card_fee = account.cms_attributes.get('credit_card_fees', {}).get('is_rent_credit_card_fee_enabled', True)
    if order.type == 'PURCHASE' or order.type == 'PURCHASE_ACCESSORY':
        credit_card_fee = account.cms_attributes.get('credit_card_fees', {}).get(
            'is_purchase_credit_card_fee_enabled', True
        )
    elif order.type == 'RENT_TO_OWN':
        credit_card_fee = account.cms_attributes.get('credit_card_fees', {}).get(
            'is_rent_to_own_credit_card_fee_enabled', True
        )

    is_only_auto_pay_allowed = account.cms_attributes.get('is_only_auto_pay_allowed', False)

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
        status=order_status if order_status is not None else "Invoiced",
        account_id=account.id,
        customer_id=saved_customer.id,
        display_order_id=selected_order_id,
        type=order.type,
        attributes=order.attributes,
        address_id=saved_address.id,
        billing_address_id=billing_address.id if billing_address else None,
        user_id=user.id.replace("auth0|", ""),
        payment_type=order.payment_type,
        delivered_at=order.delivered_at,
        paid_at=order.paid_at,
        allow_external_payments=default_external_payment,
        credit_card_fee=credit_card_fee,
        rent_due_on_day=order.rent_due_on_day or None,
        is_autopay=True if is_only_auto_pay_allowed else False,
        first_payment_strategy=order.first_payment_strategy,
        tax_exempt=order.tax_exempt,
        processing_flat_cost=processing_flat_cost,
        processing_percentage_cost=processing_percentage_cost,
        charge_per_line_item=charge_per_line_item,
        applications_overridden=applications_override,
        message_type=order.message_type,
    )

    if order.overridden_user_id:
        order_db.user_id = order.overridden_user_id

    if order:
        order = await handle_order_creation_logic(
            order_db,
            line_items,
            user,
            order_configuration,
            remaining_balance_is_zero,
            order,
            account,
            background_tasks=background_tasks,
        )

    created_customer = await customer_crud.get_latest(account.id, saved_customer.id)
    return created_customer


@atomic()
async def merge_customers(customer: UpdateCustomerOrder, account_id: int):
    customer_profile_exists = True
    customer_contact = None
    try:
        customer_contact = await customer_contact_crud.get_by_email(account_id, customer.email)
    except Exception:
        customer_profile_exists = False

    if customer_profile_exists:
        if customer_contact.customer:
            customer_ids_to_delete = []
            order_items = await order_crud.get_all_by_email_non_queryset(customer.email, account_id=account_id)
            for row in order_items:
                customer_ids_to_delete.append(row.customer.id)

            orders_to_be_modified = []
            for row in order_items:
                orders_to_be_modified.append(Order(account_id=account_id, id=row.id, single_customer_id=customer_contact.customer.id))

            await order_crud.bulk_update(orders_to_be_modified, ["single_customer_id"], len(order_items))

            for order in order_items:
                await prepare_order_cache_swap(order, order, order.user.id, account_id)

            return customer_contact.customer.id

    createAddressDict = {
        "street_address": customer.street_address,
        "zip": customer.zip,
        "state": customer.state,
        "city": customer.city,
        "county": customer.county,
    }
    resAddress = await address_crud.create(AddressIn(**createAddressDict))

    createCustomerProfileDict = {
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "company_name": customer.street_address,
        "account_id": account_id,
    }
    resCustomerProfile = await single_customer_crud.create(CustomerProfileIn(**createCustomerProfileDict))

    createCustomerContactDict = {
        "email": customer.email,
        "phone": customer.phone,
        "customer_id": str(resCustomerProfile.id),
        "customer_address_id": str(resAddress.id),
        "account_id": account_id,
    }
    await customer_contact_crud.create(CustomerContactIn(**createCustomerContactDict))

    customer_ids_to_delete = []
    order_items = await order_crud.get_all_by_email_non_queryset(customer.email, account_id=account_id)
    
    #There may be a foreign key that deletes the order if we delete the customer id
    #for row in order_items:
    #    customer_ids_to_delete.append(row.customer.id)

    orders_to_be_modified = []
    for row in order_items:
        orders_to_be_modified.append(Order(account_id=account_id, id=row.id, 
                                           single_customer_id=resCustomerProfile.id,
                                           ))

    await order_crud.bulk_update(orders_to_be_modified, ["single_customer_id"], len(order_items))

    #await customer_crud.delete_all_in_list(account_id, customer_ids_to_delete)

    for order in order_items:
        await prepare_order_cache_swap(order, order, order.user.id, account_id)

    return resCustomerProfile.id


async def create_customer(customer: CreateCustomerOrder, user: Auth0User, background_tasks: BackgroundTasks) -> Model:
    account = await account_crud.get_one(user.app_metadata["account_id"])
    created_customer = await create_generic_customer(customer, account, user, background_tasks=background_tasks)
    customer_dict = created_customer.dict()
    order = customer_dict["order"][0]
    at_least_one_shipping_container = False
    at_least_one_accessory = False

    order_obj = await order_crud.get_one(order['id'])
    for line_item in order_obj.line_items:
        if line_item.product_type == 'CONTAINER_ACCESSORY':
            at_least_one_accessory = True
        elif line_item.product_type == 'CONTAINER':
            at_least_one_shipping_container = True

    await order_controller.send_invoice_email(
        order['id'], None, user, at_least_one_accessory, at_least_one_shipping_container, background_tasks, None
    )
    return created_customer


async def update_customer_profile(customer_id: str, customer: CreateCustomer, user: Auth0User) -> Model:
    account_id = user.app_metadata["account_id"]
    saved_customer = await save_customer_profile(customer, account_id, customer_id)
    return await order_crud.get_one(saved_customer.order[0].id)


async def update_customer_contacts(
    customer_contacts_id: str, customer_contacts: CreateCustomerContact, user: Auth0User
) -> Model:
    account_id = user.app_metadata["account_id"]
    customer_contacts_dict = customer_contacts.dict()
    customer_contacts_dict['account_id'] = account_id
    await customer_contact_crud.update(account_id, customer_contacts_id, CustomerContactIn(**customer_contacts_dict))
    return


async def update_customer_address(customer_address_id: str, customer_address: CreateAddress, user: Auth0User) -> Model:
    account_id = user.app_metadata["account_id"]
    customer_address_dict = customer_address.dict()
    await address_crud.update(account_id, customer_address_id, AddressIn(**customer_address_dict))
    return


async def update_customer(customer_id: str, customer: UpdateCustomerOrder, user: Auth0User) -> Model:
    account_id = user.app_metadata["account_id"]
    saved_customer = await save_customer(customer, account_id, customer_id)
    result = await order_crud.get_one(saved_customer.order[0].id)

    # Update order cache
    await prepare_order_cache_swap(result, result, result.user.id, account_id)

    return result


async def unlink_single_customer(order_id, account_id):
    update_order_dict = {"single_customer_id": None, "account_id": account_id}
    result = await order_crud.update(account_id, order_id, OrderInUpdate(**update_order_dict))

    order = await order_crud.get_one(order_id)
    await prepare_order_cache_swap(order, order, order.user.id, account_id)
    return result


async def fetch_single_customer_contacts(single_customer_id, account_id):
    return await customer_contact_crud.get_by_customer_id(account_id=account_id, customer_id=single_customer_id)


async def remove_single_customer_contacts(contact_id, address_id):
    await customer_contact_crud.db_model.filter(id=contact_id).delete()
    return await address_crud.db_model.filter(id=address_id).delete()


async def add_single_customer_contacts(data: NewCustomerContact, account_id):
    createAddressDict = {
        "street_address": data.street_address,
        "zip": data.zip,
        "state": data.state,
        "city": data.city,
        "county": data.county,
    }
    resAddress = await address_crud.create(AddressIn(**createAddressDict))
    createCustomerContactDict = {
        "email": data.email,
        "phone": data.phone,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "customer_id": data.customer_id,
        "customer_address_id": str(resAddress.id),
        "account_id": account_id,
    }
    return await customer_contact_crud.create(CustomerContactIn(**createCustomerContactDict))


async def edit_single_customer_contacts(data: EditCustomerContact, account_id):
    createAddressDict = {
        "street_address": data.street_address,
        "zip": data.zip,
        "state": data.state,
        "city": data.city,
        "county": data.county,
    }
    await address_crud.update(account_id, data.customer_address_id, AddressIn(**createAddressDict))
    createCustomerContactDict = {
        "email": data.email,
        "phone": data.phone,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "customer_id": data.customer_id,
        "customer_address_id": data.customer_address_id,
        "account_id": account_id,
    }
    return await customer_contact_crud.update(account_id, data.id, CustomerContactIn(**createCustomerContactDict))


async def search_single_customer_id(single_customer_id, account_id):
    return await order_crud.get_all_by_single_customer_id(single_customer_id, account_id)


async def search_single_customers_by_query_parameters(
    name: str = None, phone: str = None, email: str = None, account_id: str = None
):
    customer_contact = await customer_contact_crud.get_by_filters_all(account_id, email=email, name=name, phone=phone)
    return customer_contact


async def search_customers_by_query_parameters(
    name: str = None, phone: str = None, email: str = None, company_name: str = None, account_id: str = None
):
    return await customer_crud.search_customers_by_params(account_id, email, phone, company_name, name)


def create_line_items_and_customer_order_dict(quick_obj: Any, is_quick_rent: bool = False):
    order: CreateOrder = quick_obj.order
    total: Decimal = Decimal(0)
    total_monthly_owed: Decimal = Decimal(0)
    total_shipping: Decimal = Decimal(0)
    total_pickup: Decimal = Decimal(0)

    tax_per_line_item = 0
    if is_quick_rent:
        total_tax: Decimal = quick_obj.order.tax
        tax_per_line_item = total_tax / len(quick_obj.line_items) if total_tax > 0 else Decimal(0)
    line_items: List[CreateLineItem] = []
    inventory_ids: List[str] = []
    for line_item in quick_obj.line_items:
        total += line_item.price + line_item.shipping

        if is_quick_rent:
            total_monthly_owed += line_item.monthly_owed
            # if line_item.tax is not None:
            #     total_tax += line_item.tax
            total_shipping += line_item.shipping
            total_pickup += line_item.pickup

        current_item: CreateLineItem = CreateLineItem(
            revenue=line_item.price,
            shipping_revenue=line_item.shipping,
            monthly_owed=line_item.monthly_owed if is_quick_rent else 0,
            shipping_cost=line_item.shipping_cost,
            tax=line_item.tax if not is_quick_rent else tax_per_line_item,
            attributes=line_item.attributes,
            condition=line_item.condition,
            container_size=line_item.container_size,
            product_city=line_item.product_city,
            product_state=line_item.product_state,
            product_type="SHIPPING_CONTAINER",
            product_id=line_item.product_id,
            door_orientation=line_item.door_orientation,
        )

        if line_item.inventory_id:
            current_item.inventory_id = line_item.inventory_id
            inventory_ids.append(line_item.inventory_id)
        line_items.append(current_item)

    create_customer_order_dict: dict = {
        "order": {
            "line_items": line_items,
            "type": order.type,
            "sub_total_price": total,
            "total_price": total,
            "status": "Invoiced",
            "address": {
                "street_address": quick_obj.street_address,
                "city": quick_obj.city,
                "state": quick_obj.state,
                "zip": quick_obj.zip,
                "email": quick_obj.email,
                "county": quick_obj.county,
            },
            "billing_address": {
                "street_address": quick_obj.billing_street_address,
                "city": quick_obj.billing_city,
                "state": quick_obj.billing_state,
                "zip": quick_obj.billing_zip,
                "email": quick_obj.email,
                "county": quick_obj.billing_county,
            },
        },
        "last_name": quick_obj.last_name,
        "first_name": quick_obj.first_name,
        "phone": quick_obj.phone,
        "email": quick_obj.email,
        "company_name": quick_obj.company_name,
    }

    return (
        line_items,
        create_customer_order_dict,
        inventory_ids,
        total,
        total_monthly_owed,
        total_shipping,
        total_pickup,
    )


async def add_fees_quick_sale_rent(quick_pay_obj, created_order, user, account, is_quick_sale=False):
    try:
        fee_in_list: List[FeeIn] = []
        for fee in quick_pay_obj.fees:
            if fee.fee == 0 or fee.fee_type is None:
                continue
            fee_in_dict: dict = {
                "order_id": created_order.id,
                "type_id": fee.fee_type,
                "fee_amount": round(fee.fee, 2),
            }
            fee_in_obj: FeeIn = FeeIn(**fee_in_dict)
            fee_in_list.append(fee_in_obj)
        if len(fee_in_list) > 0:
            if is_quick_sale:
                await fee_controller.create_fee(fee_in_list, user, account, quick_sale_override_tax=True)
            else:
                await fee_controller.create_fee(fee_in_list, user, account)
    except Exception as e:
        raise Exception(f"Error adding fees to order in create_quick_sale: {e}")


@atomic()
async def create_quick_sale(
    quick_sale: QuickSalePayment, user: Auth0User, account: Account, order_configuration: dict, background_tasks=None
) -> Model:
    # Question do we use the price parsed or we use the the container price?

    remaining_balance_is_zero = order_configuration.get("remaining_balance_is_zero", False)
    total: Decimal = 0
    customer_id: Union[None, str] = None
    order: CreateOrder = quick_sale.order
    order_address: CreateUpdateAddress = None
    is_credit_card_fee_enabled: bool = True
    payment_request: QuickSalePayObj = quick_sale.payment

    # if payment_request.credit_card:
    #     # want to pass by reference not by value
    #     payment_request_copy: Payment = payment_request.credit_card.copy()
    #     is_card_valid = await verify_credit_card(payment_request_copy, user.app_metadata.get("account_id"))

    #     if not is_card_valid:
    #         raise HTTPException(
    #             status_code=status.HTTP_402_PAYMENT_REQUIRED,
    #             detail="Invalid credit card information provided in the request.",
    #         )

    # checks for the line items attached to the order
    line_items, create_customer_order_dict, inventory_ids, total, _, _, _ = create_line_items_and_customer_order_dict(
        quick_sale
    )

    create_customer_order: CreateCustomerOrder = CreateCustomerOrder(**create_customer_order_dict)
    create_customer_order.order.line_items = line_items
    if quick_sale.single_customer_id is None:

        create_customer_order.order.address = CreateUpdateAddress(**create_customer_order_dict["order"]["address"])
        create_customer_order.order.billing_address = CreateUpdateAddress(
            **create_customer_order_dict["order"]["billing_address"]
        )

        order_address = create_customer_order.order.address
        billing_address = create_customer_order.order.billing_address
        if quick_sale.customer_id:
            customer_id = quick_sale.customer_id

        saved_customer = await save_customer(create_customer_order, account.id, customer_id)
        saved_address = await save_address(order_address)
        billing_address = await save_address(billing_address)

    selected_order_id = await get_order_id(account)

    default_external_payment = account.cms_attributes.get("default_external_payments", True)

    if order.type == 'PURCHASE' or order.type == 'PURCHASE_ACCESSORY':
        is_credit_card_fee_enabled = account.cms_attributes.get('credit_card_fees', {}).get(
            'is_purchase_credit_card_fee_enabled', True
        )

    (
        flat_rates_enabled,
        percentage_rates_enabled,
        processing_flat_cost,
        processing_percentage_cost,
        charge_per_line_item,
    ) = generate_processing_cost_options(account, order)

    if flat_rates_enabled or percentage_rates_enabled:
        is_credit_card_fee_enabled = False

    # we are going to save the order as invoiced first, then go through teh payment process
    # if they had selected a paid at date or a delivered at date, then after the successful payment
    # we will then update the order
    account_requires_cc_application = account.cms_attributes.get("applications", {}).get("credit_card", False)
    applications_override = None
    if account_requires_cc_application:
        applications_override = [{"name": "credit_card", "overridden": False}]
    else:
        applications_override = [{"name": "credit_card", "overridden": True}]

    order_db = OrderIn(
        status="Invoiced",
        account_id=account.id,
        customer_id=saved_customer.id if quick_sale.single_customer_id is None else None,
        display_order_id=selected_order_id,
        type=order.type,
        attributes=order.attributes,
        address_id=saved_address.id if quick_sale.single_customer_id is None else None,
        billing_address_id=billing_address.id if quick_sale.single_customer_id is None else None,
        user_id=user.id.replace("auth0|", ""),
        payment_type=order.payment_type if quick_sale.create_unpaid_order is not True else None,
        allow_external_payments=default_external_payment,
        credit_card_fee=is_credit_card_fee_enabled,
        rent_due_on_day=order.rent_due_on_day or None,
        tax_exempt=quick_sale.tax_exempt,
        processing_flat_cost=processing_flat_cost,
        processing_percentage_cost=processing_percentage_cost,
        charge_per_line_item=charge_per_line_item,
        single_customer_id=quick_sale.single_customer_id,
        applications_overridden=applications_override,
    )
    created_order: Union[None, Order] = None
    if order:
        created_order = await handle_order_creation_logic(
            order_db,
            line_items,
            user,
            order_configuration,
            remaining_balance_is_zero,
            order,
            account,
            quick_sale_override_tax=True,
            background_tasks=background_tasks,
        )

    transaction_type = None
    if order.payment_type:
        if quick_sale.create_unpaid_order is not True:
            group_id = str(uuid.uuid4())
            transaction_type_in = TransactionTypeIn(
                rent_period_id=None,
                order_id=created_order.id,
                notes=order.payment_notes,
                payment_type=order.payment_type,
                amount=payment_request.other_amt,
                group_id=group_id,
                transaction_effective_date=datetime.now(),
            )
            if quick_sale.order.paid_at:
                transaction_type_in = TransactionTypeIn(
                    rent_period_id=None,
                    order_id=created_order.id,
                    notes=order.payment_notes,
                    payment_type=order.payment_type,
                    amount=payment_request.other_amt,
                    group_id=group_id,
                    transaction_effective_date=quick_sale.order.paid_at,
                )

            transaction_type = await transaction_type_controller.create_transaction_type(
                transaction_type_in,
                user,
            )

    for inventory_id in inventory_ids:
        await inventory_controller.update_container_inventory_dict(account.id, inventory_id, {"status": "Attached"})
    # Add fees and increase total balance
    await add_fees_quick_sale_rent(quick_sale, created_order, user, account, is_quick_sale=True)

    # Add misc costs
    try:
        misc_cost_in_list: List[MiscCostIn] = []
        for m in quick_sale.misc_costs:
            if m.misc == 0:
                continue
            misc_cost_in_dict: dict = {
                "order_id": created_order.id,
                "cost_type_id": m.misc_type,
                "amount": round(m.misc, 2),
            }
            misc_in_obj: MiscCostIn = MiscCostIn(**misc_cost_in_dict)
            misc_cost_in_list.append(misc_in_obj)
        if len(misc_cost_in_list) > 0:
            await misc_costs_controller.create_misc_cost(misc_cost_in_list, user)
    except Exception as e:
        raise Exception(f"Error adding misc costs to order in create_quick_sale: {e}")

    if quick_sale.create_unpaid_order is not True:
        if payment_request.credit_card:
            payment_request.credit_card.order_id = created_order.id
            payment_request.credit_card.display_order_id = created_order.display_order_id
            await credit_card_payment_purchase_public(payment_request.credit_card, BackgroundTasks())
        elif payment_request.other_amt:
            other_payment_obj: OtherPayment = OtherPayment(order_id=str(created_order.id))
            other_payment_obj.purchase_pay_amt = payment_request.other_amt
            await handle_other_payment(other_payment_obj, transaction_type=transaction_type)
        else:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="No payment information provided in the request."
            )

        update_order_dict: dict = {}

        # if they are provided, then we will update these fields
        if quick_sale.order.paid_at:
            update_order_dict["paid_at"] = quick_sale.order.paid_at
            update_order_dict["account_id"] = account.id
            # do not need to update status, bc if the payments were successful
            # then it will already have been marked as paid

        if quick_sale.order.delivered_at:
            update_order_dict["delivered_at"] = quick_sale.order.delivered_at
            update_order_dict["status"] = "Delivered"
            update_order_dict["account_id"] = account.id

        if update_order_dict:
            # this means the dictioanry is not empty
            await order_crud.update(created_order.account_id, created_order.id, OrderInUpdate(**update_order_dict))

    if quick_sale.single_customer_id is None:
        created_customer = await customer_crud.get_latest(account.id, saved_customer.id)
    else:
        created_customer = await single_customer_crud.get_one(account.id, quick_sale.single_customer_id)

    return created_customer


@atomic()
async def create_quick_rent(
    quick_rent: QuickRent,
    user: Auth0User,
    account: Account,
    order_configuration: dict,
    background_tasks: BackgroundTasks = None,
) -> Model:
    # Question do we use the price parsed or we use the the container price?

    remaining_balance_is_zero = order_configuration.get("remaining_balance_is_zero", False)
    total: Decimal = 0
    total_monthly_owed: Decimal = 0
    total_tax: Decimal = quick_rent.order.tax
    total_shipping: Decimal = 0
    total_pickup: Decimal = 0

    customer_id: Union[None, str] = None
    order: CreateOrder = quick_rent.order
    order_address: CreateUpdateAddress = None

    (
        line_items,
        create_customer_order_dict,
        inventory_ids,
        total,
        total_monthly_owed,
        total_shipping,
        total_pickup,
    ) = create_line_items_and_customer_order_dict(quick_rent, True)

    create_customer_order: CreateCustomerOrder = CreateCustomerOrder(**create_customer_order_dict)
    create_customer_order.order.line_items = line_items

    if quick_rent.single_customer_id is None:
        create_customer_order.order.address = CreateUpdateAddress(**create_customer_order_dict["order"]["address"])
        create_customer_order.order.billing_address = CreateUpdateAddress(
            **create_customer_order_dict["order"]["billing_address"]
        )

        order_address = create_customer_order.order.address
        billing_address = create_customer_order.order.billing_address
        if quick_rent.customer_id:
            customer_id = quick_rent.customer_id

        saved_customer = await save_customer(create_customer_order, account.id, customer_id)
        saved_address = await save_address(order_address)
        billing_address = await save_address(billing_address)

    selected_order_id = await get_order_id(account)

    default_external_payment = account.cms_attributes.get("default_external_payments", True)

    (
        flat_rates_enabled,
        percentage_rates_enabled,
        processing_flat_cost,
        processing_percentage_cost,
        charge_per_line_item,
    ) = generate_processing_cost_options(account, order)

    # we are going to save the order as invoiced first, then go through teh payment process
    # if they had selected a paid at date or a delivered at date, then after the successful payment
    # we will then update the order
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

    logger.info(f"applications_override on customers: {applications_override}")

    order_db = OrderIn(
        status="Invoiced",
        account_id=account.id,
        customer_id=saved_customer.id if quick_rent.single_customer_id is None else None,
        display_order_id=selected_order_id,
        type="RENT",
        attributes=order.attributes,
        address_id=saved_address.id if quick_rent.single_customer_id is None else None,
        billing_address_id=billing_address.id if quick_rent.single_customer_id is None else None,
        user_id=user.id.replace("auth0|", ""),
        payment_type=order.payment_type,
        allow_external_payments=default_external_payment,
        credit_card_fee=False,
        rent_due_on_day=order.rent_due_on_day or None,
        override_application_process=True,
        tax_exempt=quick_rent.tax_exempt,
        processing_flat_cost=processing_flat_cost,
        processing_percentage_cost=processing_percentage_cost,
        charge_per_line_item=charge_per_line_item,
        single_customer_id=quick_rent.single_customer_id,
        applications_overridden=applications_override,
    )

    created_order: Union[None, Order] = None
    if order:
        created_order = await handle_order_creation_logic(
            order_db,
            line_items,
            user,
            order_configuration,
            remaining_balance_is_zero,
            order,
            account,
            note=quick_rent.note,
            quick_rent=True,
            drop_off=total_shipping,
            pickup=total_pickup,
            background_tasks=background_tasks,
        )
    if not order.pick_up_paid:
        await note_crud.create(
            NoteInSchema(
                title="downpayment_note",
                content=f"Pickup was not paid for this rental - Amount ${total_pickup}",
                author_id=user.id.replace("auth0|", ""),
                order_id=created_order.id,
            )
        )

    for inventory_id in inventory_ids:
        await inventory_controller.update_container_inventory_dict(account.id, inventory_id, {"status": "Attached"})
    # Add fees and increase total balance
    await add_fees_quick_sale_rent(quick_rent, created_order, user, account, is_quick_sale=False)

    # Add misc costs
    try:
        misc_cost_in_list: List[MiscCostIn] = []
        for m in quick_rent.misc_costs:
            if m.misc == 0:
                continue
            misc_cost_in_dict: dict = {
                "order_id": created_order.id,
                "cost_type_id": m.misc_type,
                "amount": round(m.misc, 2),
            }
            misc_in_obj: MiscCostIn = MiscCostIn(**misc_cost_in_dict)
            misc_cost_in_list.append(misc_in_obj)
        if len(misc_cost_in_list) > 0:
            await misc_costs_controller.create_misc_cost(misc_cost_in_list, user)
    except Exception as e:
        raise Exception(f"Error adding misc costs to order in create_quick_rent: {e}")

    update_order_dict: dict = {}

    # if they are provided, then we will update these fields
    if quick_rent.order.paid_at:
        update_order_dict["paid_at"] = quick_rent.order.paid_at
        update_order_dict["account_id"] = account.id
        # do not need to update status, bc if the payments were successful
        # then it will already have been marked as paid

    if quick_rent.order.delivered_at:
        update_order_dict["delivered_at"] = quick_rent.order.delivered_at

        started_one_before_month_difference = relativedelta(
            datetime.now(), datetime.strptime(quick_rent.started_on, "%Y-%m-%dT%H:%M:%S.%fZ")
        )
        status = "Delivered"
        if started_one_before_month_difference.months >= 1:
            status = "Delinquent"
        update_order_dict["status"] = status
        update_order_dict["account_id"] = account.id

    if update_order_dict:
        # this means the dictioanry is not empty
        await order_crud.update(created_order.account_id, created_order.id, OrderInUpdate(**update_order_dict))

    if quick_rent.single_customer_id is None:
        created_customer = await customer_crud.get_latest(account.id, saved_customer.id)
    else:
        created_customer = await single_customer_crud.get_one(account.id, quick_rent.single_customer_id)

    quick_rent.started_on = datetime.strptime(quick_rent.started_on, "%Y-%m-%dT%H:%M:%S.%fZ")
    other_payment: OtherPayment
    other_payment = OtherPayment(
        order_id=str(created_order.id),
        lump_sum_amount=total_monthly_owed + total_tax + total_shipping + total_pickup,
        rent_period_paid_amt=0,
        rent_period_ids=[],
        has_ach=False,
        use_ach_on_file=False,
        start_date=quick_rent.started_on,
    )
    # Handle rental schedule generation and payment here
    has_date_ended = False if quick_rent.ended_on is None else True
    current_date_time = datetime.today()
    number_months = 0
    month_to_pay_together = 0
    if has_date_ended:
        quick_rent.ended_on = datetime.strptime(quick_rent.ended_on, "%Y-%m-%dT%H:%M:%S.%fZ")
        number_months = months_between_dates(quick_rent.started_on, quick_rent.ended_on) + 1
    else:
        number_months = months_between_dates(quick_rent.started_on, current_date_time)
    month_to_pay_together = number_months - 1
    other_payment.past_periods_amt = (
        (month_to_pay_together * (total_monthly_owed + total_tax)) + total_shipping + total_pickup
    )

    # Post rolling period transaction amount
    if has_date_ended:
        await transaction_type_crud.create(
            TransactionTypeIn(
                notes="Default",
                amount=other_payment.past_periods_amt,
                order_id=created_order.id,
                payment_type="Check",
                group_id=str(uuid.uuid4()),
                account_id=created_order.account_id,
                transaction_effective_date=datetime.now(),
            )
        )
    else:
        other_payment.past_periods_amt = 0
    background_tasks.add_task(
        handle_quick_rent_period_generation,
        other_payment,
        min_periods_to_generate=number_months,
        has_ended_date=has_date_ended,
        date_ended=quick_rent.ended_on,
        pick_up_paid=order.pick_up_paid,
        pickup=total_pickup,
        shipping=total_shipping,
    )
    # await handle_quick_rent_period_generation(other_payment,min_periods_to_generate=number_months,
    #     has_ended_date=has_date_ended,
    #     date_ended=quick_rent.ended_on,
    #     pick_up_paid=order.pick_up_paid,
    #     pickup=total_pickup,)
    return created_customer


def months_between_dates(date1, date2):
    # Ensure date1 is the earlier date
    if date1 > date2:
        date1, date2 = date2, date1

    # Calculate the differences in years and months
    years_diff = date2.year - date1.year
    months_diff = date2.month - date1.month
    # Combine the differences
    total_months = years_diff * 12 + months_diff
    return total_months
