# Python imports
import logging
import os
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Union

# Pip imports
from fastapi import BackgroundTasks, HTTPException
from loguru import logger
from pydantic import BaseModel
from tortoise.transactions import atomic

# Internal imports
from src.api.rental_history import create_rental_history
from src.auth.auth import Auth0User
from src.config import settings
from src.controllers import balance as balance_controller
from src.controllers import fee_type as fee_type_controller
from src.controllers import notifications_controller
from src.controllers import order_fee_balance as order_fee_balance_controller
from src.controllers import orders as order_controller
from src.controllers import rent_period as rent_period_controller
from src.controllers.event_controller import send_event, order_paid_agent_notification
from src.crud.account_crud import account_crud
from src.crud.fee_crud import fee_crud
from src.crud.order_card_info_crud import order_credit_card_crud
from src.crud.order_crud import OrderCRUD
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.crud.total_order_balance_crud import total_order_balance_crud
from src.crud.transaction_type_crud import TransactionTypeIn, transaction_type_crud
from src.crud.user_crud import UserCRUD
from src.database.models.account import Account
from src.database.models.fee_type import FeeType
from src.database.models.note import Note
from src.database.models.orders.order import Order
from src.database.models.pricing.location_price import LocationPrice
from src.database.models.rent_period import RentPeriod

# from src.redis import limiter
from src.schemas.container_locations import LocationPriceInSchema, LocationPriceOutSchema
from src.schemas.fee import FeeIn
from src.schemas.notes import NoteInSchema, NoteOutSchema, UpdateNote
from src.schemas.order_credit_card import OrderCreditCardInSchema
from src.schemas.order_fee_balance import OrderFeeBalanceIn
from src.schemas.orders import OrderInUpdate
from src.schemas.payment import CreditCardObj, OtherPayment, Payment
from src.schemas.rental_history import RentalHistoryIn
from src.schemas.total_order_balance import TotalOrderBalanceIn
from src.services.notifications import email_service, email_service_mailersend
from src.services.payment.authorize_pay_service import charge_credit_card as authorize_charge_credit_card
from src.services.payment.authorize_pay_service import (
    charge_customer_profile,
    create_customer_profile,
    delete_payment_profile,
    get_customer_profile,
    handle_create_authorize_customer_profile_id,
    handle_create_authorize_payment_profile_id,
    handle_create_authorize_payment_profile_id_credit_card,
)
from src.services.payment.authorize_pay_service import remove_customer_profile as remove_customer_profile_authorize
from src.services.payment.authorize_pay_service import (
    update_customer_payment_profile,
    update_customer_payment_profile_bank_account,
    verify_card,
)
from src.services.payment.card_pointe_service import authorize_and_capture_transaction
from src.services.payment.noomerik_pay_service import charge_credit_card as noomerik_charge_credit_card
from src.services.payment.usa_epay_service import charge_credit_card as usa_epay_charge_credit_card
from src.services.payment.usa_epay_service import get_all_data
from src.services.payment.usa_epay_service import get_customers as usa_epay_get_customers
from src.utils.utility import make_json_serializable

from ..crud.customer_crud import CustomerCRUD
from ..crud.location_distance_crud import LocationDistanceCRUD
from ..crud.rent_period_fee_crud import rent_period_fee_crud


class Status(BaseModel):
    message: str


BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")
FAILING_ZIP_AUTHORIZE = 46282
IS_PROD: bool = settings.STAGE.lower() == "prod"
IS_DEV: bool = settings.STAGE.lower() == "dev"
MOCK_SUCCESSFUL_TRANSACTION_RESPONSE: dict = {
    'transactionResponse': {
        'responseCode': '1',
        'authCode': '51IBFA',
        'avsResultCode': 'Y',
        'cvvResultCode': 'P',
        'cavvResultCode': '2',
        'transId': '120011925489',
        'refTransID': '',
        'transHash': '',
        'testRequest': '0',
        'accountNumber': 'XXXX0126',
        'accountType': 'AmericanExpress',
        'messages': [{'code': '1', 'description': 'This transaction has been approved.'}],
        'transHashSha2': '',
        'SupplementalDataQualificationIndicator': 0,
        'networkTransId': 'H0RG8JBXUILS74RMJD928JT',
    },
    'messages': {'resultCode': 'Ok', 'message': [{'code': 'I00001', 'text': 'Successful.'}]},
}
MOCK_UNSUCCESSFUL_TRANSACTION_RESPONSE: dict = {
    'transactionResponse': {
        'responseCode': '2',
        'authCode': '',
        'avsResultCode': 'Y',
        'cvvResultCode': 'P',
        'cavvResultCode': '2',
        'transId': '120011925264',
        'refTransID': '',
        'transHash': '',
        'testRequest': '0',
        'accountNumber': 'XXXX0126',
        'accountType': 'AmericanExpress',
        'errors': [{'errorCode': '2', 'errorText': 'This transaction has been declined.'}],
        'transHashSha2': '',
        'SupplementalDataQualificationIndicator': 0,
        'networkTransId': '1S64E9XFKUX1RK1B0O0EO74',
    },
    'messages': {'resultCode': 'Ok', 'message': [{'code': 'I00001', 'text': 'Successful.'}]},
    'errorMessage': 'This transaction has been declined.',
}

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


location_crud = TortoiseCRUD(
    schema=LocationPriceOutSchema,
    create_schema=LocationPriceInSchema,
    update_schema=LocationPriceInSchema,
    db_model=LocationPrice,
)


async def handle_authorize_charge_credit_card(payment_info: dict, authorize_int: dict) -> dict:
    credit_card_response = authorize_charge_credit_card(
        payment_info,
        live_name=authorize_int.get("api_login_id"),
        live_trans_key=authorize_int.get("transaction_key"),
        url=authorize_int.get("url"),
    )
    if credit_card_response["messages"]["resultCode"] != 'Ok':
        logger.error(
            f"{payment_info['display_order_id']} charge_rental_downpayment failed "
            + str(credit_card_response["messages"]["message"][0]['text'])
        )
        raise Exception(credit_card_response["messages"]["message"][0]['text'])

    return credit_card_response


async def charge_card_purchase(account: Account, payment_info: dict, new_balance: Decimal):
    usa_epay_int = account.integrations.get("usa_epay", {})
    authorize_int_purchase = account.integrations.get("authorize", {}).get('purchase', {})
    noomerik_int = account.integrations.get("noomerik", {})
    card_pointe_int = account.integrations.get("card_pointe", {})
    credit_card_response = {}

    account_country = account.cms_attributes.get('account_country', "USA")
    # we dont want to charge them 0
    # and IS_PROD Removing this so that we actually ping authorize even in test env
    if new_balance >= 0:
        if authorize_int_purchase.get("in_use"):
            credit_card_response = authorize_charge_credit_card(
                payment_info,
                live_name=authorize_int_purchase.get("api_login_id"),
                live_trans_key=authorize_int_purchase.get("transaction_key"),
                url=authorize_int_purchase.get("url"),
                country=account_country,
            )

        if usa_epay_int.get("in_use"):
            credit_card_response = usa_epay_charge_credit_card(payment_info, usa_epay_int["api_key"])

        if noomerik_int.get("in_use"):
            credit_card_response = noomerik_charge_credit_card(payment_info, noomerik_int.get('transaction_key'))

        if card_pointe_int.get("in_use"):
            credit_card_response = await authorize_and_capture_transaction(
                payment_info,
                card_pointe_int.get('merchid'),
                card_pointe_int.get('authorization'),
                base_url=card_pointe_int.get("url"),
            )
    elif new_balance >= 0 and IS_DEV:
        if authorize_int_purchase.get("in_use"):
            payment_zip_code: int = int(payment_info.get("zip", 0))
            if payment_zip_code == int(FAILING_ZIP_AUTHORIZE):
                credit_card_response = MOCK_UNSUCCESSFUL_TRANSACTION_RESPONSE
            else:
                credit_card_response = MOCK_SUCCESSFUL_TRANSACTION_RESPONSE

    return credit_card_response


async def get_customer_profile_by_id(customer_profile_id: str, user: Auth0User):
    account: Account = await account_crud.get_one(user.app_metadata.get('account_id'))

    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})
    if authorize_int_rentals.get("in_use"):
        return get_customer_profile(
            customer_profile_id=customer_profile_id,
            live_key=authorize_int_rentals["api_login_id"],
            trans_key=authorize_int_rentals["transaction_key"],
            url=authorize_int_rentals["url"],
        )
    return {}


async def credit_card_charge_rental_downpayment(account: Account, payment_info: dict, existing_order: Order):
    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})
    credit_card_response = {}
    customer_profile_id: int
    if authorize_int_rentals.get("in_use"):
        logger.info(f"{payment_info['display_order_id']} charge_rental_downpayment")
        # we check to see if they have autopay selected
        is_autopay_selected: bool = existing_order.is_autopay

        if is_autopay_selected:
            # if they do, then we need to create a customer_profile_id for their order
            if existing_order.customer_profile_id is None:
                customer_profile_id = await handle_create_authorize_customer_profile_id(
                    existing_order=existing_order,
                    payment_info=payment_info,
                    authorize_int=authorize_int_rentals,
                    account_id=account.id,
                    is_autopay=is_autopay_selected,
                )
            else:
                customer_profile_id = existing_order.customer_profile_id
                payment_info['type'] = 'CREDIT'

            customer_profile_response: Any | dict[str, str] = get_customer_profile(
                customer_profile_id=customer_profile_id,
                live_key=authorize_int_rentals["api_login_id"],
                trans_key=authorize_int_rentals["transaction_key"],
                url=authorize_int_rentals["url"],
            )

            customer_payment_profile_id = None
            for pp in customer_profile_response['profile']['paymentProfiles']:
                if pp['payment'].get('creditCard'):
                    customer_payment_profile_id = pp['customerPaymentProfileId']
                    payment_info['merchant_name'] = pp['payment']['creditCard']['cardType']

            if not customer_payment_profile_id:
                raise Exception("Credit card customer payment profile not found.")

            credit_card_response = charge_customer_profile(
                order_details=payment_info,
                customer_profile_id=customer_profile_id,
                payment_profile_id=customer_payment_profile_id,
                live_name=authorize_int_rentals.get("api_login_id"),
                live_trans_key=authorize_int_rentals.get("transaction_key"),
                url=authorize_int_rentals["url"],
            )

        else:
            if payment_info.get('pay_with_customer_profile'):
                customer_profile_id = existing_order.customer_profile_id
                payment_info['type'] = 'CREDIT'

                customer_profile_response: Any | dict[str, str] = get_customer_profile(
                    customer_profile_id=customer_profile_id,
                    live_key=authorize_int_rentals["api_login_id"],
                    trans_key=authorize_int_rentals["transaction_key"],
                    url=authorize_int_rentals["url"],
                )

                customer_payment_profile_id = None
                for pp in customer_profile_response['profile']['paymentProfiles']:
                    if pp['payment'].get('creditCard'):
                        customer_payment_profile_id = pp['customerPaymentProfileId']
                        payment_info['merchant_name'] = pp['payment']['creditCard']['cardType']

                credit_card_response = charge_customer_profile(
                    order_details=payment_info,
                    customer_profile_id=customer_profile_id,
                    payment_profile_id=customer_payment_profile_id,
                    live_name=authorize_int_rentals.get("api_login_id"),
                    live_trans_key=authorize_int_rentals.get("transaction_key"),
                    url=authorize_int_rentals["url"],
                )
            else:
                # then we just go ahead and charge downpayment if they are not on autopay
                credit_card_response = await handle_authorize_charge_credit_card(payment_info, authorize_int_rentals)

    return credit_card_response


async def credit_card_charge_rental(account: Account, payment_info: dict):
    usa_epay_int: dict = account.integrations.get("usa_epay", {})
    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})
    credit_card_response = {}
    if authorize_int_rentals.get("in_use"):
        existing_order: Order = await order_crud.get_one(payment_info['order_id'])

        # pay rent period
        logger.info(f"{existing_order.display_order_id} authorize_charge_credit_card pay period")
        if not payment_info['pay_with_customer_profile']:
            credit_card_response = await handle_authorize_charge_credit_card(
                payment_info=payment_info, authorize_int=authorize_int_rentals
            )
        else:
            customer_profile_response: Any | dict[str, str] = get_customer_profile(
                customer_profile_id=existing_order.customer_profile_id,
                live_key=authorize_int_rentals["api_login_id"],
                trans_key=authorize_int_rentals["transaction_key"],
                url=authorize_int_rentals["url"],
            )

            payment_info['type'] = 'CREDIT'

            customer_payment_profile_id = None
            for pp in customer_profile_response['profile']['paymentProfiles']:
                if pp['payment'].get('creditCard'):
                    customer_payment_profile_id = pp['customerPaymentProfileId']
                    payment_info['merchant_name'] = pp['payment']['creditCard']['cardType']

            if not customer_payment_profile_id:
                raise Exception("Credit card customer payment profile not found.")

            credit_card_response = charge_customer_profile(
                order_details=payment_info,
                customer_profile_id=existing_order.customer_profile_id,
                payment_profile_id=customer_payment_profile_id,
                live_name=authorize_int_rentals.get("api_login_id"),
                live_trans_key=authorize_int_rentals.get("transaction_key"),
                url=authorize_int_rentals["url"],
            )

    if usa_epay_int.get("in_use"):
        payment_info["total_paid"] = payment_info["rental_first_month_price"]
        api_key = usa_epay_int["api_key"]
        all_customers = get_all_data(usa_epay_get_customers, api_key)
        found_customer = [customer for customer in all_customers if customer["email"] == payment_info["email"]]
        found_customer = found_customer[0] if len(found_customer) > 0 else None
        credit_card_response = usa_epay_charge_credit_card(payment_info, api_key, found_customer)
    return credit_card_response


async def charge_ach_on_file(account: Account, payment_info: dict):
    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})

    if authorize_int_rentals.get("in_use"):
        existing_order: Order = await order_crud.get_one(payment_info['order_id'])

        # pay rent period
        logger.info(f"{existing_order.display_order_id} authorize_charge_ach pay period")
        customer_profile_response = get_customer_profile(
            customer_profile_id=existing_order.customer_profile_id,
            live_key=authorize_int_rentals["api_login_id"],
            trans_key=authorize_int_rentals["transaction_key"],
            url=authorize_int_rentals["url"],
        )

        payment_info['type'] = 'CREDIT'

        customer_payment_profile_id = None
        for pp in customer_profile_response['profile']['paymentProfiles']:
            if pp['payment'].get("bankAccount"):
                customer_payment_profile_id = pp['customerPaymentProfileId']

        if not customer_payment_profile_id:
            raise Exception("Didn't find an ACH payment profile on customer profile.")

        payment_response = charge_customer_profile(
            order_details=payment_info,
            customer_profile_id=existing_order.customer_profile_id,
            payment_profile_id=customer_payment_profile_id,
            live_name=authorize_int_rentals.get("api_login_id"),
            live_trans_key=authorize_int_rentals.get("transaction_key"),
            url=authorize_int_rentals["url"],
        )
    return payment_response


async def send_payment_emails(updated_order, account, background_tasks):
    updated_order_d = updated_order.dict()

    email_provider = account.cms_attributes.get("emails", {}).get("provider", {})

    if not updated_order.is_pickup:
        if email_provider == "mailersend":
            email_info = {
                "text": account.cms_attributes.get("emails", {}).get("payment", ""),
                "order_title": updated_order_d.get("status", "Invoice"),
                "account_name": account.company_name,
                "display_order_id": updated_order_d.get("display_order_id"),
                **updated_order_d,
            }
            email_service_mailersend.send_paid_email(email_info)
        else:
            await notifications_controller.send_paid_email(updated_order_d["id"], background_tasks)
            email_service.send_customer_general_receipt_email(updated_order_d)

    email_text = "You just had a customer just pay via Credit Card. Order #{}".format(
        updated_order_d["display_order_id"]
    )
    order_user = await user_crud.get_one_without_account(updated_order_d["user"]['id'])
    emails = [order_user.assistant.manager.email, order_user.email] if order_user.assistant else [order_user.email]
    if account.cms_attributes.get("sendInternalAgentEmails", True):
        external_integrations = account.external_integrations
        if external_integrations is not None and external_integrations.get("resources") is not None and len(external_integrations.get("resources")) > 0 and len([res for res in external_integrations.get("resources") if "update:user:paid_at" in res.get("event_types")]) > 0:
            await order_paid_agent_notification(updated_order.display_order_id, False if updated_order.signed_at is None else True, account.id, await order_controller.get_agent(updated_order), updated_order, emails, background_tasks)
        else:
            email_service.send_agent_email(email_text, emails)


async def get_order_and_account(order_id: str) -> Dict[str, Any]:
    existing_order: Order = await order_crud.get_one(order_id)

    if existing_order.status == "Paid" or existing_order.calculated_remaining_order_balance <= 0:
        raise HTTPException(status_code=400, detail="This order has already been paid. Please refresh the browser.")

    account: Account = await account_crud.get_one(existing_order.account_id)
    return {"order": existing_order, "account": account}


def create_payment_info(existing_order: Order, payment_requst: Payment) -> Dict[str, Any]:

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=existing_order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    payment_info = payment_requst.dict()
    payment_info["order_id"] = existing_order.id
    payment_info["email"] = customer_info.get("email", "")
    payment_info["shipping_details"] = {
        "first_name": customer_info.get("first_name", ""),
        "last_name": customer_info.get("last_name", ""),
        "street_address": existing_order.address.street_address,
        "city": existing_order.address.city,
        "state": existing_order.address.state,
        "zip": existing_order.address.zip,
    }

    payment_info["line_items"] = [
        {
            "name": item.title,
            "id": item.id,
            "price": item.calculated_total_revenue,
        }
        for item in existing_order.line_items
    ]
    # "2020-08-30"

    shipping_revenue = sum([Decimal(item.shipping_revenue) for item in existing_order.line_items])

    payment_info["tax"] = existing_order.calculated_order_tax
    payment_info["shipping_revenue"] = str(shipping_revenue)

    # RENTAL FIELDS
    payment_info["amount"] = payment_info['total_paid']  # str(existing_order.calculated_monthly_owed_total)
    payment_info['trial_amount'] = str(existing_order.calculated_remaining_order_balance)
    payment_info["total_period"] = '1'
    payment_info['total_occurrences'] = '9999'
    payment_info["order_type"] = existing_order.type

    return payment_info


def calculate_total_bank_fees(payment_request: Payment, convenience_percentage: float) -> Decimal:
    total_bank_fees = round(((payment_request.total_paid) * Decimal(convenience_percentage)), 2)

    return total_bank_fees


def validate_convenience_fee(total_fees: Decimal, convenience_fee_total: Decimal):
    if total_fees < convenience_fee_total - 1 or total_fees > convenience_fee_total + 1:
        logger.info("convenience fee is not correct")
        raise HTTPException(status_code=400, detail="Bank fee is not correct")


def calculate_new_balance(
    existing_order: Order,
    sub_total_price: Decimal,
    total_bank_fees: Decimal,
    total_paid_with_bank_fees: Decimal,
    payment_request: Payment,
) -> Decimal:
    if existing_order.type == "RENT":
        return existing_order.calculated_remaining_order_balance - Decimal(payment_request.total_paid)
    if not existing_order.calculated_remaining_order_balance:
        logger.info("no remaining balance")
        new_balance = (sub_total_price + total_bank_fees) - total_paid_with_bank_fees
        if new_balance < 1 and new_balance > -1:
            new_balance = 0
    else:
        remaining_balance = round(existing_order.calculated_remaining_order_balance, 4)
        # Grabbing the remaining balance and adding on the total bank fees to increase the total rb
        new_balance = remaining_balance + total_bank_fees
        # Then we subtract from the new balance, the total paid with the bank fees added on
        # ex: total paid from front end is 1500, then the bank fee is 52.5. so the 52.5 gets added to the
        # remaining balance in the logic before and then here we add the 1500 + 52.5 = 1552.50 to get the total
        # paid with bank fee and then subtract that from the new balance. This way the bank fees cancel out and
        # it is really just the amount they are paying that gets subtracted from the remaining balance.
        new_balance = Decimal(new_balance) - (total_paid_with_bank_fees)
        logger.info("CALCULATED NEW REMAINING BALANCE ", new_balance)
    return new_balance


async def update_order_balance(existing_order: Order, new_balance: Decimal) -> None:
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Browser needs to be refreshed.")

    create_order_balance = TotalOrderBalanceIn(remaining_balance=new_balance, order_id=existing_order.id)
    await total_order_balance_crud.create(create_order_balance)


async def handle_credit_card_response(
    existing_order: Order,
    account: Account,
    payment_info: Dict[str, Any],
    new_balance: Decimal,
    total_paid_with_bank_fees: Decimal,
    is_downpayment: bool,
    background_tasks: BackgroundTasks,
) -> dict:
    # THIS IS CRUCIAL. WE HAVE TO SET THE TOTAL_PAID AMOUNT TO THE TOTAL PAID WITH BANK FEES
    # check these logs often to ensure that we are sending the proper amount to authorize
    payment_info["total_paid"] = str(total_paid_with_bank_fees)
    logger.info(f"Total amount to be charged: ${payment_info.get('total_paid')}")

    if existing_order.type == "RENT":
        if is_downpayment:
            credit_card_response = await credit_card_charge_rental_downpayment(account, payment_info, existing_order)
            if not credit_card_response.get("errorMessage"):
                # TODO can these go into a background task
                await order_crud.update(
                    account.id,
                    existing_order.id,
                    OrderInUpdate(
                        **{
                            "status": "first_payment_received",
                            "user_id": existing_order.user.id,
                            "account_id": account.id,
                        }
                    ),
                )
                await notifications_controller.send_paid_email(existing_order.id, background_tasks)
        else:
            credit_card_response = await credit_card_charge_rental(account, payment_info)

    if existing_order.type == "RENT_TO_OWN":
        pass

    if existing_order.type == "PURCHASE" or existing_order.type == 'PURCHASE_ACCESSORY':
        credit_card_response = await charge_card_purchase(account, payment_info, new_balance)

    credit_card_response['payment_amount'] = str(total_paid_with_bank_fees)

    error = credit_card_response.get("errorMessage")

    order_credit_card_obj = await order_credit_card_crud.create(
        OrderCreditCardInSchema(
            order_id=existing_order.id,
            merchant_name=payment_info["merchant_name"].upper(),
            card_type=payment_info.get("type"),
            response_from_gateway=credit_card_response,
        )
    )

    if error:
        logger.info("There was an error of some kind, however the customer may have still successfully paid.")
        logger.info(error)
        raise HTTPException(status_code=400, detail=error)

    return credit_card_response, order_credit_card_obj


async def handle_fees(existing_order: Order, total_bank_fees: Decimal, order_credit_card_obj: None):

    bank_fee_type: FeeType = await fee_type_controller.fetch_fee_type_by_name(existing_order.account_id, "CREDIT_CARD")

    # Add the total fees to the fee table for every credit card transaction
    if total_bank_fees != 0:
        create_fee = FeeIn(fee_amount=total_bank_fees, type_id=bank_fee_type.id, order_id=existing_order.id)
        created_fee = await fee_crud.create(create_fee)

        fee_balance_obj = OrderFeeBalanceIn(
            remaining_balance=total_bank_fees,
            order_id=existing_order.id,
            account_id=existing_order.account_id,
            fee_id=created_fee.id,
        )
        # TODO these can go into a background task
        await order_fee_balance_controller.handle_initial_fee_balance([fee_balance_obj])
        await order_fee_balance_controller.create_order_fee_balance(
            OrderFeeBalanceIn(
                remaining_balance=0,
                order_id=existing_order.id,
                account_id=existing_order.account_id,
                fee_id=created_fee.id,
                order_credit_card_id=order_credit_card_obj.id,
            )
        )


async def handle_order_status(existing_order: Order, new_balance: Decimal, rent_due_on_day: Union[int, None] = None):
    updated_status = existing_order.status
    if existing_order.type == "RENT":
        if existing_order.rent_periods[0].calculated_rent_period_total_balance == 0 and (
            len(existing_order.rent_periods) > 1
            and existing_order.rent_periods[1].calculated_total_paid == 0
            or len(existing_order.rent_periods) == 1
        ):
            updated_status = "first_payment_received"

        rent_due_on_day = rent_due_on_day

    if existing_order.type == "PURCHASE" or existing_order.type == 'PURCHASE_ACCESSORY':
        if new_balance == Decimal(0):
            updated_status = "Paid"
        elif existing_order.status != "Pod":
            updated_status = "Partially Paid"

    order_dict = {
        "status": updated_status,
        "user_id": existing_order.user.id,
        "account_id": existing_order.account_id,
    }

    # only if it is a rental, and that rental payment has the payment_request.rent_due_on_day populated
    # then we will update the order with it
    if existing_order.rent_due_on_day is None and rent_due_on_day is not None:
        order_dict["rent_due_on_day"] = rent_due_on_day

    if updated_status == "Paid":
        order_dict["paid_at"] = datetime.now()
        if not existing_order.payment_type:
            order_dict["payment_type"] = "CC"

    if updated_status == "Delivered":
        if not existing_order.payment_type:
            order_dict["payment_type"] = "CC"

    updated_order = await order_crud.update(
        existing_order.account_id,
        existing_order.id,
        OrderInUpdate(**order_dict),
    )

    return updated_order


def subTotalNoFee(item):
    return Decimal(item.revenue or 0) + Decimal(item.shipping_revenue or 0)


def calculateTotal(i, fee_percentage):
    return subTotalNoFee(i) * (Decimal(fee_percentage) + 1)


@atomic()
async def credit_card_payment_purchase_public(payment_request: Payment, background_tasks: BackgroundTasks):
    order_account_dict = await get_order_and_account(payment_request.order_id)
    existing_order: Order = order_account_dict["order"]
    account: Account = order_account_dict["account"]
    convenience_percentage = account.cms_attributes.get("convenience_fee_rate", 0)

    payment_info: Dict[str, Any] = create_payment_info(existing_order=existing_order, payment_requst=payment_request)

    if not existing_order.credit_card_fee:
        convenience_percentage = 0

    # we have to make sure that this is included any time we are paying with creditcard. the bank fees are added to the total paid, so that
    # we give the backend the control on the amount of the bank fees
    total_bank_fees = calculate_total_bank_fees(payment_request, convenience_percentage)
    total_paid_with_bank_fees = payment_request.total_paid + total_bank_fees

    validate_convenience_fee(total_bank_fees, payment_request.convenience_fee_total)
    sub_total_price = (
        sum([calculateTotal(line_item, convenience_percentage) for line_item in existing_order.line_items])
        + existing_order.calculated_order_tax
    )

    new_balance = calculate_new_balance(
        existing_order=existing_order,
        sub_total_price=sub_total_price,
        total_bank_fees=total_bank_fees,
        total_paid_with_bank_fees=total_paid_with_bank_fees,
        payment_request=payment_request,
    )

    new_balance: Decimal = round(new_balance, 2)

    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Browser needs to be refreshed.")

    _, order_credit_card_object = await handle_credit_card_response(
        existing_order=existing_order,
        account=account,
        payment_info=payment_info,
        new_balance=new_balance,
        total_paid_with_bank_fees=total_paid_with_bank_fees,
        is_downpayment=False,
        background_tasks=background_tasks,
    )

    # send event to event controller
    if background_tasks:
        background_tasks.add_task(
            send_event,
            existing_order.account_id,
            str(existing_order.id),
            make_json_serializable(
                {
                    "payment_method": "CREDIT_CARD",
                    "transaction_date": datetime.now(),
                    "success": True
                    if order_credit_card_object.response_from_gateway.get("messages", {}).get("resultCode", "Not ok")
                    == "Ok"
                    else False,
                }
            ),
            "payment",
            "make_payment",
        )

    transaction_type = await transaction_type_crud.create(
        TransactionTypeIn(
            order_id=existing_order.id,
            payment_type="CC",
            amount=payment_info['total_paid'],
            account_id=existing_order.account_id,
            credit_card_object_id=order_credit_card_object.id,
            transaction_effective_date=datetime.now(),
        )
    )

    # Both of these need to be after the credit card comes through successful if it does
    # background_tasks.add_task(handle_fees, existing_order, total_bank_fees, order_credit_card_object)
    # background_tasks.add_task(update_order_balance, existing_order, new_balance)
    await handle_fees(existing_order, total_bank_fees, order_credit_card_object)
    await update_order_balance(existing_order, new_balance)

    updated_order = await handle_order_status(existing_order, new_balance)
    at_least_one_accessory = False
    for line_item in existing_order.line_items:
        if line_item.product_type == 'CONTAINER_ACCESSORY':
            at_least_one_accessory = True

    if updated_order.status == "Paid":
        if existing_order.status != "Pod":
            await send_payment_emails(updated_order, account, background_tasks)
        if account.name.startswith("USA Containers") and at_least_one_accessory:
            await email_service.send_accessory_paid_email(updated_order.display_order_id)
        if not account.name.startswith("USA Containers") and at_least_one_accessory:
            # need to implement accessory emails for non-usa containers accounts
            pass

        # background_tasks.add_task(order_controller.handle_pay_all_balances, existing_order, order_credit_card_object.id)
        await order_controller.handle_pay_all_balances(
            existing_order, order_credit_card_id=order_credit_card_object.id, transaction_type_id=transaction_type.id
        )
    else:
        # background_tasks.add_task( order_controller.handle_order_balances_paydown, existing_order, payment_info['amount'], order_credit_card_object.id)
        await order_controller.handle_order_balances_paydown(
            existing_order,
            payment_info['amount'],
            order_credit_card_id=order_credit_card_object.id,
            transaction_type_id=transaction_type.id,
        )

    return updated_order


async def verify_credit_card(payment_request: Payment, account_id: int):
    account: Account = await account_crud.get_one(account_id)

    usa_epay_int = account.integrations.get("usa_epay", {})
    authorize_int = account.integrations.get("authorize.net", {})
    convenience_percentage = account.cms_attributes.get("convenience_fee_rate", 0)

    # we have to make sure that this is included any time we are paying with creditcard. the bank fees are added to the total paid, so that
    # we give the backend the control on the amount of the bank fees
    total_bank_fees = calculate_total_bank_fees(payment_request, convenience_percentage)
    total_paid_with_bank_fees = payment_request.total_paid + total_bank_fees
    payment_request.total_paid = total_paid_with_bank_fees
    payment_info: dict = payment_request.dict(exclude_unset=True)
    # we dont want to charge them 0
    if authorize_int:
        if authorize_int.get("in_use"):
            card_verified_response = verify_card(
                payment_info,
                live_name=authorize_int.get("api_login_id"),
                live_trans_key=authorize_int.get("transaction_key"),
                url=authorize_int.get("url"),
            )
            # No error, its valid
            return not card_verified_response.get('errorMessage', False)
    if usa_epay_int:
        pass


def check_is_down_payment(exisiting_order: Order) -> bool:
    """
    Check if an existing order has already received the down payment charge by looking at the
    length of rent periods. If there is only one, that means the down payment has not yet been
    received

    Args:
        existing_order (Order): The existing order to check.

    Returns:
        bool: True if the order has already received the down payment.
    """
    rent_periods: List[RentPeriod] = exisiting_order.rent_periods
    # if there is only one initial rent period loaded, that means that the order still hasn't received its
    # down payment and will need to be charged that first
    is_only_down_payment: bool = len(rent_periods) == 1
    return is_only_down_payment


async def remove_customer_payment_profile(order_id: str, payment_profile_type: str):
    order: Order = await order_crud.get_one(order_id)
    account: Account = await account_crud.get_one(order.account_id)
    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})

    if authorize_int_rentals.get("in_use"):
        response = get_customer_profile(
            order.customer_profile_id,
            authorize_int_rentals["api_login_id"],
            authorize_int_rentals["transaction_key"],
            url=authorize_int_rentals["url"],
        )

        if response['messages']['resultCode'] == 'Ok':
            payment_profiles = response['profile']['paymentProfiles']
            customerProfileId = response['profile']['customerProfileId']

            for pp in payment_profiles:
                customerPaymentProfileId = pp['customerPaymentProfileId']
                if (
                    payment_profile_type == 'CREDIT_CARD'
                    and pp['payment'].get('creditCard')
                    or payment_profile_type == 'ACH'
                    and pp['payment'].get('bankAccount')
                ):
                    response = delete_payment_profile(
                        customerProfileId,
                        customerPaymentProfileId,
                        authorize_int_rentals["api_login_id"],
                        authorize_int_rentals["transaction_key"],
                        url=authorize_int_rentals["url"],
                    )
                    logger.info(response)

    return Status(message="Success")


async def remove_customer_profile(order_id: str):
    order: Order = await order_crud.get_one(order_id)
    account: Account = await account_crud.get_one(order.account_id)
    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})

    if authorize_int_rentals.get("in_use"):
        response = remove_customer_profile_authorize(
            order.customer_profile_id,
            authorize_int_rentals["api_login_id"],
            authorize_int_rentals["transaction_key"],
            url=authorize_int_rentals["url"],
        )
        return Status(message=str(response))

    return Status(message="Success")


async def add_ach(credit_card_request: CreditCardObj):
    order_account_dict = await get_order_and_account(credit_card_request.order_id)
    account: Account = order_account_dict["account"]
    existing_order = order_account_dict['order']
    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})

    if authorize_int_rentals.get("in_use"):
        if existing_order.customer_profile_id:
            await handle_create_authorize_payment_profile_id(
                existing_order, credit_card_request.dict(), authorize_int_rentals, account.id
            )
        else:
            customer_profile_id = await handle_create_authorize_customer_profile_id(
                existing_order, credit_card_request.dict(), authorize_int_rentals, account.id
            )

            await order_crud.update(account.id, existing_order.id, Order(customer_profile_id=customer_profile_id))

    return Status(message="Success")


async def add_card_on_file(credit_card_request: CreditCardObj, background_tasks: BackgroundTasks):
    order_account_dict = await get_order_and_account(credit_card_request.order_id)
    account: Account = order_account_dict["account"]
    existing_order = order_account_dict['order']
    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})

    if authorize_int_rentals.get("in_use"):
        if existing_order.customer_profile_id:
            customer_profile_id = await handle_create_authorize_payment_profile_id_credit_card(
                existing_order, credit_card_request.dict(), authorize_int_rentals, account.id
            )

            await order_crud.update(
                account.id,
                existing_order.id,
                OrderInUpdate(account_id=account.id, customer_profile_id=customer_profile_id),
            )
        else:
            customer_profile_id = await handle_create_authorize_customer_profile_id(
                existing_order, credit_card_request.dict(), authorize_int_rentals, account.id
            )

            await order_crud.update(
                account.id,
                existing_order.id,
                OrderInUpdate(account_id=account.id, customer_profile_id=customer_profile_id),
            )

    return Status(message="Success")


async def update_ach(change_credit_card_request: CreditCardObj):
    order_account_dict = await get_order_and_account(change_credit_card_request.order_id)
    account: Account = order_account_dict["account"]
    existing_order: Order = order_account_dict['order']
    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=existing_order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    if authorize_int_rentals.get("in_use"):
        customer_payment_profile_id = None
        customer_profile_response = {}

        # create customer profile id
        customer_details = {
            "id": customer_info.get("id", ""),
            "email": customer_info.get("email", ""),
            "card_number": change_credit_card_request.cardNumber,
            "expiration_date": change_credit_card_request.expirationDate,
            "card_code": change_credit_card_request.cardCode,
            "first_name": change_credit_card_request.first_name,
            "last_name": change_credit_card_request.last_name,
            "street_address": change_credit_card_request.avs_street,
            "city": change_credit_card_request.city,
            "state": change_credit_card_request.state,
            "zip": change_credit_card_request.zip,
            "shipping_details": {
                "first_name": customer_info.get("first_name", ""),
                "last_name": customer_info.get("last_name", ""),
                "street_address": existing_order.address.street_address,
                "city": existing_order.address.city,
                "state": existing_order.address.state,
                "zip": existing_order.address.zip,
            },
            'bankName': change_credit_card_request.bank_name,
            'routingNumber': change_credit_card_request.routing_number,
            'accountNumber': change_credit_card_request.account_number,
        }

        if existing_order.customer_profile_id:
            customer_profile_response = get_customer_profile(
                existing_order.customer_profile_id,
                authorize_int_rentals["api_login_id"],
                authorize_int_rentals["transaction_key"],
                url=authorize_int_rentals["url"],
            )

            customer_payment_profile_id = None
            for pp in customer_profile_response['profile']['paymentProfiles']:
                if pp['payment'].get("bankAccount"):
                    customer_payment_profile_id = pp['customerPaymentProfileId']

            if not customer_payment_profile_id:
                raise Exception("Didn't find an ACH payment profile on customer profile.")

            update_customer_profile_response = update_customer_payment_profile_bank_account(
                str(existing_order.customer_profile_id),
                customer_payment_profile_id,
                customer_details,
                authorize_int_rentals["api_login_id"],
                authorize_int_rentals["transaction_key"],
                authorize_int_rentals["url"],
            )
            if update_customer_profile_response["messages"]["resultCode"] == 'Ok':
                pass
            else:
                raise Exception(update_customer_profile_response["messages"]["message"][0]['text'])


async def change_credit_card(change_credit_card_request: CreditCardObj, background_tasks: BackgroundTasks):
    order_account_dict = await get_order_and_account(change_credit_card_request.order_id)
    account: Account = order_account_dict["account"]
    existing_order: Order = order_account_dict['order']
    authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=existing_order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    if authorize_int_rentals.get("in_use"):
        customer_payment_profile_id = None
        customer_profile_response = {}

        # create customer profile id
        customer_details = {
            "id": customer_info.get("id", ""),
            "email": customer_info.get("email", ""),
            "card_number": change_credit_card_request.cardNumber,
            "expiration_date": change_credit_card_request.expirationDate,
            "card_code": change_credit_card_request.cardCode,
            "first_name": change_credit_card_request.first_name,
            "last_name": change_credit_card_request.last_name,
            "street_address": change_credit_card_request.avs_street,
            "city": change_credit_card_request.city,
            "state": change_credit_card_request.state,
            "zip": change_credit_card_request.zip,
            "shipping_details": {
                "first_name": customer_info.get("first_name", ""),
                "last_name": customer_info.get("last_name", ""),
                "street_address": existing_order.address.street_address,
                "city": existing_order.address.city,
                "state": existing_order.address.state,
                "zip": existing_order.address.zip,
            },
        }

        if existing_order.customer_profile_id:
            customer_profile_response = get_customer_profile(
                existing_order.customer_profile_id,
                authorize_int_rentals["api_login_id"],
                authorize_int_rentals["transaction_key"],
                url=authorize_int_rentals["url"],
            )

            customer_payment_profile_id = None
            for pp in customer_profile_response['profile']['paymentProfiles']:
                if pp['payment'].get("creditCard"):
                    customer_payment_profile_id = pp['customerPaymentProfileId']

            if not customer_payment_profile_id:
                raise Exception("Didn't find an credit card payment profile on customer profile.")

            update_customer_profile_response = update_customer_payment_profile(
                str(existing_order.customer_profile_id),
                customer_payment_profile_id,
                customer_details,
                authorize_int_rentals["api_login_id"],
                authorize_int_rentals["transaction_key"],
                authorize_int_rentals["url"],
            )
            if update_customer_profile_response["messages"]["resultCode"] == 'Ok':
                pass
            else:
                raise Exception(update_customer_profile_response["messages"]["message"][0]['text'])
        else:
            customer_profile_response = create_customer_profile(
                customer_details,
                authorize_int_rentals["api_login_id"],
                authorize_int_rentals["transaction_key"],
                url=authorize_int_rentals["url"],
            )
            if customer_profile_response["messages"]["resultCode"] == 'Ok':
                customer_profile_id = int(customer_profile_response["customerProfileId"])
                order_update_dict: dict = {
                    "account_id": existing_order.account_id,
                    "user_id": existing_order.user.id,
                    "customer_profile_id": customer_profile_id,
                }
                await order_crud.update(
                    existing_order.account_id,
                    existing_order.id,
                    OrderInUpdate(**order_update_dict),
                )


def fetch_rental_convenience_fee_rate(cms_attributes):
    credit_card_fee = cms_attributes.get("credit_card_fees")
    if credit_card_fee.get("is_rent_credit_card_fee_enabled", False):
        return cms_attributes.get("convenience_fee_rate", 0)
    return 0


async def credit_card_rentals(payment_request: Payment, background_tasks: BackgroundTasks, user: Auth0User):
    order_accout_dict = await get_order_and_account(payment_request.order_id)
    existing_order: Order = order_accout_dict["order"]
    account: Account = order_accout_dict["account"]
    rent_options: dict = account.cms_attributes.get("rent_options")
    payment_info = create_payment_info(existing_order, payment_request)
    convenience_percentage = fetch_rental_convenience_fee_rate(
        account.cms_attributes
    )  # .get("convenience_fee_rate", 0)

    # this will tell us whether or not we need to generate the future rent periods or not and if we need to
    # update the start and end date of the current rent period
    is_down_payment_charge: bool = check_is_down_payment(existing_order)

    total_bank_fees = calculate_total_bank_fees(payment_request, convenience_percentage)

    if not existing_order.credit_card_fee:
        convenience_percentage = 0
        total_bank_fees = 0

    total_paid_with_bank_fees = payment_request.total_paid + total_bank_fees

    _, order_credit_card_obj = await handle_credit_card_response(
        existing_order=existing_order,
        account=account,
        payment_info=payment_info,
        new_balance=0,
        total_paid_with_bank_fees=total_paid_with_bank_fees,
        is_downpayment=is_down_payment_charge,
        background_tasks=background_tasks,
    )

    start_date = rent_period_controller.get_contract_start_date(account)
    if not start_date:
        rent_due_on_day = payment_request.rent_due_on_day
    else:
        rent_due_on_day = start_date.day

    if start_date:
        rent_options['start_date'] = start_date

    updated_order = await handle_order_status(existing_order, 0, rent_due_on_day)

    if is_down_payment_charge:
        initial_rent_period: RentPeriod = existing_order.rent_periods[0]
        await rent_period_controller.handle_rent_period_dates_update(
            initial_rent_period, updated_order, rent_due_on_day, start_date
        )

    # await handle_rental_history_creation(existing_order)
    # this payment_request stores the rent_period_id so we will know what is being paid off
    await rent_period_controller.handle_rent_period_credit_card_pay(
        payment_request,
        updated_order,
        rent_options,
        is_down_payment_charge,
        payment_request.autopay_day,
        order_credit_card_obj.id,
        user,
    )

    if (updated_order.status == "Paid" or updated_order.status == "Delivered") and updated_order.type != 'RENT':
        await send_payment_emails(updated_order, account, background_tasks)

    return updated_order


@atomic()
async def waive_all_fees(rent_period_ids: List[str], user: Auth0User):
    late_fee = await fee_type_controller.fetch_fee_type_by_name(user.app_metadata['account_id'], 'LATE')
    if late_fee is not None:
        late_fee_id = str(late_fee.id)
        for rent_period_id in rent_period_ids:
            rent_period = await rent_period_controller.get_rent_period(rent_period_id)
            rent_period_fees = await rent_period_fee_crud.get_all_by_rent_period_id_fee_type(rent_period_id, late_fee_id)

            sum_of_fees = sum([x.fee_amount for x in rent_period_fees])
            try:
                await balance_controller.rent_period_fee_balance_adjustment(rent_period, sum_of_fees, sum_of_fees, False)
            except Exception as e:
                raise e

        await rent_period_fee_crud.delete_all_by_rent_period_ids_fee_type(rent_period_ids, late_fee_id)


async def handle_other_payment_helper(
    other_payment: OtherPayment,
    order_credit_card_object=None,
    transaction_type=None,
    transaction_type_group_id=None,
    user=None,
):
    # Pay using customer info if the client has ach  paying with Echeck using ach on file
    if other_payment.has_ach and other_payment.use_ach_on_file:
        order_accout_dict = await get_order_and_account(other_payment.order_id)
        existing_order: Order = order_accout_dict["order"]
        account: Account = order_accout_dict["account"]
        amount = 0
        payment_info: list
        if other_payment.lump_sum_amount and other_payment.lump_sum_amount > 0:
            amount = other_payment.lump_sum_amount
        else :
            if other_payment.rent_period_paid_amt:
                amount += other_payment.rent_period_paid_amt
            if other_payment.rent_period_fee_paid_amt:
                amount += other_payment.rent_period_fee_paid_amt
            if other_payment.rent_period_tax_paid_amt:
                amount += other_payment.rent_period_tax_paid_amt
        payment_info = {
            'amount': amount,
            'display_order_id': existing_order.display_order_id,
            'order_id': other_payment.order_id,
        }
        logger.info(f"AMOUNT TO SEND {amount}")

        ach_response = await charge_ach_on_file(account, payment_info)
        if ach_response.get('errorMessage'):
            logger.info(ach_response)
            raise Exception("Transaction could not be processed")

    updated_order: Order
    order_accout_dict = await get_order_and_account(other_payment.order_id)
    existing_order: Order = order_accout_dict["order"]
    account: Account = order_accout_dict["account"]
    rent_options: dict = account.cms_attributes.get("rent_options")

    if existing_order.type == "RENT":
        is_down_payment_charge: bool = check_is_down_payment(existing_order)
        if other_payment.payment_option is not None and other_payment.payment_option == 'Fees':
            await rent_period_controller.handle_rent_period_fees_payment(
                other_payment, existing_order, order_credit_card_object, user=user
            )
        elif other_payment.payment_option is not None and other_payment.payment_option == 'Total Balance':
            await rent_period_controller.pay_multiple_rent_period_balances_only(
                other_payment, existing_order, order_credit_card_object, user=user
            )
        else:
            await rent_period_controller.handle_rent_period_other_pay(
                other_payment,
                existing_order,
                order_credit_card_object,
                transaction_type_group_id=transaction_type_group_id,
                user=user,
            )

        updated_order = await order_crud.get_one(other_payment.order_id)

        start_date = rent_period_controller.get_contract_start_date(account)
        if not start_date:
            rent_due_on_day = other_payment.rent_due_on_day
        else:
            rent_due_on_day = start_date.day

        if not rent_due_on_day:
           rent_due_on_day = date.today().day

        if start_date:
            rent_options['start_date'] = start_date
        # TODO this can go into background task
        updated_order = await handle_order_status(
            updated_order, updated_order.calculated_remaining_order_balance, rent_due_on_day
        )

        if is_down_payment_charge:
            initial_rent_period: RentPeriod = updated_order.rent_periods[0]
            # TODO all awaits here can go into background tasks
            await rent_period_controller.handle_rent_period_dates_update(
                initial_rent_period, updated_order, rent_due_on_day, start_date
            )
            #await rent_period_controller.generate_rolling_rent_periods(rent_options, initial_rent_period, updated_order)
            await notifications_controller.send_paid_email(existing_order.id)

        # await handle_rental_history_creation(existing_order)

    elif existing_order.type == "PURCHASE" or existing_order.type == 'PURCHASE_ACCESSORY':
        is_adding: bool = False
        # TODO this can go into a background task
        await balance_controller.order_balance_adjustment(existing_order, other_payment.purchase_pay_amt, is_adding)

        pay_amount = None
        if not other_payment.lump_sum_amount:
            pay_amount = other_payment.purchase_pay_amt
        else:
            pay_amount = other_payment.lump_sum_amount
        if order_credit_card_object:
            # TODO this can go into a background task
            await order_controller.handle_order_balances_paydown(
                existing_order=existing_order, amount_paid=pay_amount, order_credit_card_id=order_credit_card_object.id
            )
        else:
            # TODO this can go into a background task
            await order_controller.handle_order_balances_paydown(
                existing_order=existing_order, amount_paid=pay_amount, transaction_type_id=transaction_type.id
            )

    updated_order = await order_crud.get_one(other_payment.order_id)
    updated_order = await handle_order_status(
        updated_order, updated_order.calculated_remaining_order_balance, other_payment.rent_due_on_day
    )
    return updated_order


@atomic()
async def handle_other_payment(
    other_payment: OtherPayment, order_credit_card_object=None, transaction_type=None, user=None
):
    transaction_type_group_id = str(uuid.uuid4())
    return await handle_other_payment_helper(
        other_payment,
        order_credit_card_object,
        transaction_type,
        transaction_type_group_id=transaction_type_group_id,
        user=user,
    )


@atomic()
async def handle_other_orders_payment_credit_card(
    other_payment: Dict[Any, Any], payment_request: Payment, background_tasks: BackgroundTasks, user
):
    account = await account_crud.get_one(user.app_metadata['account_id'])
    convenience_percentage = account.cms_attributes.get("convenience_fee_rate", 0)

    orders_ids = other_payment['mergedOrders']
    paymentAmount = other_payment['lump_sum_amount']
    paymentType = other_payment['payment_type']

    bulk_payment = other_payment['bulk_payment']
    individual_payments = other_payment['individual_payments']
    transaction_paid_at = other_payment['transaction_paid_at']

    other_payments = []
    payment_list = []
    if bulk_payment == 'bulk_payment':

        orders = []
        for order_id in orders_ids:
            order = await order_crud.get_one(order_id)
            orders.append(order)

        leftOver = Decimal(paymentAmount)

        for order in orders:
            if order.calculated_rent_balance == 0:
                continue
            elif order.calculated_rent_balance < leftOver:
                other_payments.append(
                    OtherPayment(
                        order_id=str(order.id),
                        lump_sum_amount=order.calculated_rent_balance,
                        payment_type=paymentType,
                        payment_option="Pay All",
                    )
                )

                new_payment = payment_request.copy()
                new_payment.total_paid = Decimal(order.calculated_rent_balance)
                new_payment.convenience_fee_total = new_payment.total_paid * Decimal(convenience_percentage)
                new_payment.order_id = str(order.id)

                payment_list.append(new_payment)

                leftOver -= Decimal(order.calculated_rent_balance)
            elif leftOver != 0 and order.calculated_rent_balance >= leftOver:
                other_payments.append(
                    OtherPayment(
                        order_id=str(order.id), lump_sum_amount=leftOver, payment_type=paymentType, payment_option="Pay All"
                    )
                )
                new_payment = payment_request.copy()
                new_payment.total_paid = Decimal(leftOver)
                new_payment.order_id = str(order.id)
                new_payment.convenience_fee_total = new_payment.total_paid * Decimal(convenience_percentage)

                payment_list.append(new_payment)

                leftOver = 0
            elif leftOver == 0:
                continue

    else:
        for ip in individual_payments:
            other_payments.append(
                OtherPayment(
                    order_id=str(ip['order_id']), lump_sum_amount=ip['payment_amount'], payment_type=paymentType,
                        payment_option="Pay All", transaction_created_at=transaction_paid_at
                )
            )
            new_payment = payment_request.copy()
            new_payment.total_paid = Decimal(ip['payment_amount'])
            new_payment.order_id = str(ip['order_id'])
            new_payment.convenience_fee_total = new_payment.total_paid * Decimal(convenience_percentage)

            payment_list.append(new_payment)

    transaction_type_group_id = str(uuid.uuid4())
    for i in range(len(payment_list)):
        await handle_other_payment_credit_card(
            other_payments[i], payment_list[i], background_tasks, transaction_type_group_id=transaction_type_group_id, user=user
        )

    order = await order_crud.get_one(payment_request.order_id)
    return order


@atomic()
async def handle_other_payment_credit_card(
    other_payment: OtherPayment,
    payment_request: Payment,
    background_tasks: BackgroundTasks,
    transaction_type_group_id=None,
    user=None,
):
    order_accout_dict = await get_order_and_account(payment_request.order_id)
    existing_order: Order = order_accout_dict["order"]
    account: Account = order_accout_dict["account"]
    payment_info = create_payment_info(existing_order, payment_request)
    convenience_percentage = account.cms_attributes.get("convenience_fee_rate", 0)

    total_bank_fees = calculate_total_bank_fees(payment_request, convenience_percentage)
    if not existing_order.credit_card_fee:
        convenience_percentage = 0
        total_bank_fees = 0
    total_paid_with_bank_fees = payment_request.total_paid + total_bank_fees

    payment_info["total_paid"] += total_bank_fees

    credit_card_response, order_credit_card_object = await handle_credit_card_response(
        existing_order=existing_order,
        account=account,
        payment_info=payment_info,
        new_balance=0,
        total_paid_with_bank_fees=total_paid_with_bank_fees,
        is_downpayment=False,
        background_tasks=background_tasks,
    )

    if credit_card_response.get("errorMessage"):
        raise Exception("Transaction could not be processed")
    # TODO handle_order_status can go into a background task
    updated_order = await handle_order_status(existing_order, 0, payment_request.rent_due_on_day)
    updated_order = await handle_other_payment_helper(
        other_payment, order_credit_card_object, transaction_type_group_id=transaction_type_group_id, user=user
    )
    return updated_order


@atomic()
async def handle_other_orders_payment(bulk_orders, user=None):
    orders_ids = bulk_orders['mergedOrders']
    paymentAmount = bulk_orders['paymentAmount']
    paymentType = bulk_orders['paymentType']
    bulk_payment = bulk_orders['bulk_payment']
    individual_payments = bulk_orders['individual_payments']
    transaction_paid_at = bulk_orders['transaction_paid_at']

    other_payments = []

    if bulk_payment == 'bulk_payment':
        orders = []
        for order_id in orders_ids:
            order = await order_crud.get_one(order_id)
            orders.append(order)

        leftOver = Decimal(paymentAmount)
        for order in orders:
            if order.calculated_rent_balance == 0:
                continue
            elif order.calculated_rent_balance < leftOver:
                other_payments.append(
                    OtherPayment(
                        order_id=str(order.id),
                        lump_sum_amount=order.calculated_rent_balance,
                        payment_type=paymentType,
                        payment_option="Pay All",
                    )
                )
                leftOver -= Decimal(order.calculated_rent_balance)
            elif leftOver != 0 and order.calculated_rent_balance >= leftOver:
                other_payments.append(
                    OtherPayment(
                        order_id=str(order.id), lump_sum_amount=leftOver, payment_type=paymentType, payment_option="Pay All"
                    )
                )
                leftOver = 0
            elif leftOver == 0:
                continue

    else:
        for ip in individual_payments:
            other_payments.append(
                OtherPayment(
                    order_id=str(ip['order_id']), lump_sum_amount=ip['payment_amount'], payment_type=paymentType, payment_option="Pay All", transaction_created_at=transaction_paid_at
                )
            )

    transaction_group_id = str(uuid.uuid4())
    for op in other_payments:
        await handle_other_payment_helper(op, transaction_type_group_id=transaction_group_id, user=user )

async def handle_quick_rent_period_generation(
    other_payment: OtherPayment,
    min_periods_to_generate=0,
    has_ended_date=False,
    date_ended=None,
    pick_up_paid=True,
    pickup=Decimal(0),
    shipping=Decimal(0),
):
    updated_order: Order
    order_accout_dict = await get_order_and_account(other_payment.order_id)
    existing_order: Order = order_accout_dict["order"]
    account: Account = order_accout_dict["account"]
    rent_options: dict = account.cms_attributes.get("rent_options")
    if min_periods_to_generate > 0:
        if has_ended_date:
            rent_options['rolling_rent_periods'] = min_periods_to_generate
            rent_options['date_ended'] = date_ended
        else:
            rent_options['rolling_rent_periods'] = min_periods_to_generate + rent_options['rolling_rent_periods']
    if has_ended_date:
        await rent_period_controller.handle_rent_period_other_pay(other_payment, existing_order)
    updated_order = await order_crud.get_one(other_payment.order_id)
    # start_date = rent_period_controller.get_contract_start_date(account)
    is_down_payment_charge = True

    start_date = other_payment.start_date
    rent_due_on_day = start_date.day
    if start_date:
        rent_options['start_date'] = start_date

    updated_order = await handle_order_status(
        updated_order, updated_order.calculated_remaining_order_balance, rent_due_on_day
    )
    initial_rent_period: RentPeriod
    initial_rent_period = updated_order.rent_periods[0]
    if is_down_payment_charge:
        initial_rent_period = updated_order.rent_periods[0]
        await rent_period_controller.handle_rent_period_dates_update(
            initial_rent_period, updated_order, rent_due_on_day, start_date
        )
        await rent_period_controller.generate_rolling_rent_periods(
            rent_options, initial_rent_period, updated_order, quick_rent=True, pickup=pickup, drop_off=shipping
        )
    updated_order = await order_crud.get_one(other_payment.order_id)
    other_payment.lump_sum_amount = other_payment.past_periods_amt
    if has_ended_date:
        await rent_period_controller.handle_rent_period_other_pay(other_payment, updated_order)
    updated_order = await order_crud.get_one(other_payment.order_id)
    updated_order = await handle_order_status(
        updated_order, updated_order.calculated_remaining_order_balance, other_payment.rent_due_on_day
    )
    # if not pick_up_paid:
    #     pickup_fee: RentPeriodFeeIn = RentPeriodFeeIn(
    #         fee_type = "FIRST_PAYMENT",
    #         type_id=fee_type.id,
    #         fee_amount=pickup,
    #         rent_period_id = initial_rent_period.id
    #     )
    #     await rent_period_fee_controller.create_rent_period_fees([pickup_fee])

    return updated_order


async def handle_rental_history_creation(existing_order: Order):
    for line_item in existing_order.line_items:
        if not line_item.rental_history:
            # Don't create a rental history if no container it's attached
            if not line_item.inventory:
                continue
            inventory_id = line_item.inventory.id

            if inventory_id:
                rental_history_dict = {
                    "rent_started_at": datetime.now(),
                    "rent_ended_at": None,
                    "line_item_id": line_item.id,
                    "inventory_id": inventory_id,
                }
                await create_rental_history(RentalHistoryIn(**rental_history_dict))
    return True
