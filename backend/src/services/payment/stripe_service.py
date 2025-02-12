# main.py
# Python imports
import asyncio
import json
import uuid
from datetime import datetime
from decimal import Decimal

# Pip imports
import stripe
from fastapi import BackgroundTasks, HTTPException
from loguru import logger

# Internal imports
from src.controllers import payment as payment_controller
from src.crud.account_crud import account_crud
from src.crud.order_card_info_crud import order_credit_card_crud
from src.crud.order_crud import order_crud
from src.crud.transaction_type_crud import transaction_type_crud
from src.schemas.order_credit_card import OrderCreditCardInSchema
from src.schemas.transaction_type import TransactionTypeIn


async def create_payment_intent(account_id, order_id, amount):
    account = await account_crud.get_one(account_id)
    order = await order_crud.get_one(order_id)
    country = account.cms_attributes.get("account_country", "USA")
    currency = "usd" if country == "USA" else "cad"

    payment_methods = ['card', 'ach_debit']
    if country == "USA":
        payment_methods.append('us_bank_account')

    if account.cms_attributes.get("stripe", {}).get("enabled", False):
        integration = account.integrations.get("stripe", {})
        stripe.api_key = integration.get("secret_key", "")
        try:
            order_token = str(uuid.uuid4())
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_types=payment_methods,
                metadata={
                    'display_order_id': order.display_order_id,
                    'phone': order.customer.phone,
                    'email': order.customer.email,
                    'city': order.customer.city,
                    'state': order.customer.state,
                    'county': order.customer.county,
                    'street_address': order.customer.street_address,
                    'order_id': order_id,
                    'account_id': account_id,
                    'amount': amount / 100,
                    'order_token': order_token,
                },
            )
            return {
                "client_secret": payment_intent.client_secret,
                "public_key": integration.get("public_key", ""),
                "order_token": order_token,
                "payment_intent_id": payment_intent.id,
            }
        except Exception as e:
            logger.info(str(e))
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=422, detail="Stripe not enabled on this account")


async def webhook_received(account_id, request_data, backround_tasks: BackgroundTasks):
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.

    # need to authenticate the webhook
    # Need to use credit card transaction crud instead of transaction crud
    # Need to ensure that payment intent succeeded is the correct event for ach payments
    body_str = request_data.decode('utf-8')
    # logger.info(body_str)
    request_data = json.loads(body_str)
    # sig_header = request_data.META['HTTP_STRIPE_SIGNATURE']
    logger.info(request_data)
    account = await account_crud.get_one(account_id)
    integration = account.integrations.get("stripe", {})
    stripe.api_key = integration.get("secret_key", "")
    try:
        stripe.Event.construct_from(request_data, stripe.api_key)
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload stripe webhook: {e}")

    # integration = account.integrations.get("stripe", {})
    # webhook_secret = integration.get("secret_key", "")
    data = request_data['data']
    event_type = request_data['type']
    data_object = data['object']
    # check for duplicates
    meta_data = data_object.get("metadata", {})
    if "order_token" in meta_data:
        order_id = meta_data['order_id']
        transaction_id = meta_data['order_token']
        amount = meta_data['amount']
        transaction = await transaction_type_crud.get_by_id(transaction_id)
        order_credit = await order_credit_card_crud.get_by_id(transaction_id)
        order = await order_crud.get_one(order_id)
        if transaction is None and order_credit is None and order is not None:
            if event_type == 'payment_intent.succeeded':
                logger.info('Payment received!')
                payment_method = stripe.PaymentMethod.retrieve(data_object.get("payment_method", ""))
                if order is not None:
                    # save transaction
                    await process_transaction(
                        order=order,
                        transaction_id=transaction_id,
                        payment_method=payment_method,
                        amount_paid=amount,
                        intent_data=data_object,
                        account=account,
                        backround_tasks=backround_tasks,
                    )
                    # If it is a rental
            elif event_type == 'payment_intent.payment_failed':
                logger.info('Payment failed.')
        else:
            logger.info('Duplicate transaction id.')
            logger.info(data)
    return {'status': 'success'}


async def process_transaction(
    order, transaction_id, payment_method, amount_paid, intent_data, account, backround_tasks: BackgroundTasks
):
    payment_type = "ACH"
    order_id = order.id
    amount = amount_paid
    convenience_percentage = account.cms_attributes.get("convenience_fee_rate", 0)
    if not order.credit_card_fee:
        convenience_percentage = 0
    amount = round(Decimal(amount_paid) / (1 + Decimal(convenience_percentage)), 2)

    total_bank_fees = round(((Decimal(amount)) * Decimal(convenience_percentage)), 2)

    if 'card' in payment_method:
        payment_type = "CC"
        payment_info = payment_method.get('card')
        await order_credit_card_crud.create(
            OrderCreditCardInSchema(
                **{
                    "order_id": order_id,
                    "merchant_name": payment_info.get("brand", "VISA").upper(),
                    "card_type": payment_info.get("funding", 'CREDIT').upper(),
                    "response_from_gateway": intent_data,
                    "id": transaction_id,
                }
            )
        )
    else:
        transaction_type = TransactionTypeIn(
            **{
                "payment_type": payment_type,
                "order_id": order_id,
                "id": transaction_id,
                "notes": "Stripe Payment",
                "account_id": order.account_id,
                "amount": amount,
                "group_id": str(uuid.uuid4()),
                "transaction_effective_date": datetime.now(),
            }
        )
        await transaction_type_crud.create(transaction_type)

    if order.type == "RENT":
        # TODO putting code for purchascalculated_remaining_order_balancee here for now
        new_balance = order.calculated_remaining_order_balance - Decimal(amount_paid)
        order_account_dict = await payment_controller.get_order_and_account(order.id)
        existing_order = order_account_dict["order"]
        await payment_controller.update_order_balance(existing_order, new_balance)
        updated_order = await payment_controller.handle_order_status(existing_order, new_balance)
        if updated_order.status == "Paid":
            await payment_controller.send_payment_emails(updated_order, account)
    else:
        order_account_dict = await payment_controller.get_order_and_account(order.id)
        existing_order = order_account_dict["order"]
        new_balance = Decimal(0)
        if not existing_order.calculated_remaining_order_balance:
            sub_total_price = (
                sum(
                    [
                        payment_controller.calculateTotal(line_item, convenience_percentage)
                        for line_item in existing_order.line_items
                    ]
                )
                + existing_order.calculated_order_tax
            )
            new_balance = (sub_total_price + total_bank_fees) - Decimal(amount_paid)
            if new_balance < 1 and new_balance > -1:
                new_balance = 0
        else:
            new_balance = (existing_order.calculated_remaining_order_balance + total_bank_fees) - Decimal(amount_paid)
        await payment_controller.update_order_balance(existing_order, new_balance)
        updated_order = await payment_controller.handle_order_status(existing_order, new_balance)
        if updated_order.status == "Paid":
            await payment_controller.send_payment_emails(updated_order, account)


async def transaction_status(order_token: str, payment_intent: str, account_id, backround_tasks: BackgroundTasks):
    transaction = await transaction_type_crud.get_by_id(order_token)
    order_credit = await order_credit_card_crud.get_by_id(order_token)
    if transaction is not None:
        order = await order_crud.get_one(transaction.order_id)
        return {"status": "success", "balance": order.calculated_remaining_order_balance}
    elif order_credit is not None:
        order = await order_crud.get_one(order_credit.order_id)
        return {"status": "success", "balance": order.calculated_remaining_order_balance}
    asyncio.create_task(
        poll_payment_intent(account_id=account_id, intent_id=payment_intent, backround_tasks=backround_tasks)
    )
    raise HTTPException(status_code=404, detail="Transaction not found")


async def poll_payment_intent(account_id: int, intent_id: str, backround_tasks: BackgroundTasks):
    account = await account_crud.get_one(account_id)
    if account.cms_attributes.get("stripe", {}).get("enabled", False):
        integration = account.integrations.get("stripe", {})
        stripe.api_key = integration.get("secret_key", "")
        intent = stripe.PaymentIntent.retrieve(intent_id)
        # logger.info(intent)
        if intent and intent.status == 'succeeded':
            # payment successful
            meta_data = intent.metadata
            order_id = meta_data.order_id
            transaction_id = meta_data.order_token
            amount = meta_data.amount
            transaction = await transaction_type_crud.get_by_id(transaction_id)
            order = await order_crud.get_one(order_id)
            if transaction is None and order is not None:
                payment_method = stripe.PaymentMethod.retrieve(intent.payment_method)
                await process_transaction(
                    order=order,
                    transaction_id=transaction_id,
                    payment_method=payment_method,
                    amount_paid=amount,
                    intent_data=intent,
                    account=account,
                    backround_tasks=backround_tasks,
                )


# In src/services/stripe_service.py
async def create_payment_link(amount, account_id):
    stripe.api_key = ""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Order Payment',
                    },
                    'unit_amount': amount * 100,  # amount in cents
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url='https://example.com/success',
        cancel_url='https://example.com/cancel',
    )
    return session.url
