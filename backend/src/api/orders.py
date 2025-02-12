# Python imports
import re
from datetime import datetime, timedelta
from io import BytesIO
from pydantic import BaseModel
from typing import Any, Dict, List

# Pip imports
# Pip imports HTTPException, status
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from loguru import logger
from tortoise.transactions import atomic
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import orders
from src.controllers import rent_period as rent_period_controller
from src.controllers.customer_statement import customer_statement_controller
from src.crud._types import PAGINATION
from src.crud.account_crud import account_crud
from src.crud.assistant_crud import assistant_crud
from src.crud.container_attribute_crud import container_attribute_crud
from src.crud.container_product_crud import container_product_crud
from src.crud.line_item_crud import line_item_crud
from src.crud.order_crud import order_crud
from src.crud.tax_crud import tax_crud
from src.dependencies import auth
from src.lambdas.post_processor.get_receipt_items_report_post_processor import get_receipt_items_report_post_processor
from src.lambdas.sql_functions.orders_summary_rentals import get_orders_summary_rentals
from src.schemas.line_items import LineItemInUpdate
from src.schemas.orders import (
    CreateUpdateAddress,
    OrderInUpdate,
    OrderOut,
    OrderSearchFilters,
    PaymentOrder,
    Receipt,
    UpdateOrder,
    UpdateRentPeriodDates,
    RentalStatementDataRequest

)

# from src.services.orders.utils import request_key_builder
from src.schemas.reports import FilterObject
from src.services.invoice.pdf_generation import PdfGeneratorRentalStatement, PdfGeneratorRentalStatementMultipleOrders
from src.services.notifications import email_service_mailersend
from src.utils.order_update_in_cache import clear_cache


router = APIRouter(tags=["orders"], dependencies=[Depends(auth.implicit_scheme)])


@router.get("/order_by_display_id/{order_id}", response_model=Dict[str, Any])
async def get_order_by_display_id(order_id: str, user: Auth0User = Depends(auth.get_user)):
    return await orders.get_order_by_display_id(order_id, user)


@router.get("/order_line_items_history/{order_id}")
async def get_order_line_items_history(order_id: str, user: Auth0User = Depends(auth.get_user)):
    return await orders.get_order_line_items_history(order_id, user)


@router.get("/order/{order_id}", response_model=Dict[str, Any])
async def get_order_by_id(order_id: str, user: Auth0User = Depends(auth.get_user)):
    return await orders.get_order_by_id(order_id, user)


@router.post("/order/{order_id}/preview", response_model=Dict[str, Any])
async def preview_payment(order_id: str, payment_obj: PaymentOrder, user: Auth0User = Depends(auth.get_user)):
    return await orders.preview_payment(order_id, payment_obj.payment_amount)


@router.get("/resend_order/{order_id}")
async def resend_order(order_id: str, backround_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)):
    order = await order_crud.get_one(order_id)
    at_least_one_accessory = False
    at_least_one_shipping_container = False
    for line_item in order.line_items:
        if line_item.product_type == 'CONTAINER_ACCESSORY':
            at_least_one_accessory = True
        elif line_item.product_type == 'CONTAINER':
            at_least_one_shipping_container = True

    return await orders.send_invoice_email(
        order_id, None, user, at_least_one_accessory, at_least_one_shipping_container, backround_tasks, None
    )


@router.get("/resend_order/{contact_id}/{order_id}")
async def resend_order_to_contact(
    contact_id: str, order_id: str, backround_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    order = await order_crud.get_one(order_id)
    at_least_one_accessory = False
    at_least_one_shipping_container = False
    for line_item in order.line_items:
        if line_item.product_type == 'CONTAINER_ACCESSORY':
            at_least_one_accessory = True
        elif line_item.product_type == 'CONTAINER':
            at_least_one_shipping_container = True

    return await orders.send_invoice_email(
        order_id, contact_id, user, at_least_one_accessory, at_least_one_shipping_container, backround_tasks, None
    )


@router.get("/resend_order/{order_id}/period/{period_id}")
async def resend_period_invoice(
    order_id: str, period_id: str, backround_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    order = await order_crud.get_one(order_id)
    at_least_one_accessory = False
    at_least_one_shipping_container = False
    for line_item in order.line_items:
        if line_item.product_type == 'CONTAINER_ACCESSORY':
            at_least_one_accessory = True
        elif line_item.product_type == 'CONTAINER':
            at_least_one_shipping_container = True

    return await orders.send_invoice_email(
        order_id, None, user, at_least_one_accessory, at_least_one_shipping_container, backround_tasks, period_id
    )


@router.get("/send_agent_status_email/{order_id}")
async def send_agent_status_email(
    order_id: str, backround_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    return await orders.send_agent_status_email(order_id, user, backround_tasks)


@router.get("/convert_order_to_purchase/{order_id}")
async def convert_order_to_purchase(order_id: str, user: Auth0User = Depends(auth.get_user)):
    order = await order_crud.get_one(order_id)

    for line_item in order.line_items:
        line_item_dict = {}
        line_item_dict['rent_period'] = None
        line_item_dict['total_rental_price'] = None
        line_item_dict['monthly_owed'] = None
        await line_item_crud.update(user.app_metadata['account_id'], line_item.id, LineItemInUpdate(**line_item_dict))

    await order_crud.update(
        user.app_metadata['account_id'],
        order_id,
        OrderInUpdate(
            **{
                "type": "PURCHASE",
                "account_id": user.app_metadata['account_id'],
            }
        ),
    )


@router.get("/get_orders_inventory/{status}/{order_type}")
async def get_orders_with_inventory(
    status: str,
    order_type: str,
    pagination: PAGINATION = order_crud.pagination_depends,
    user: Auth0User = Depends(auth.get_user),
):
    return await orders.get_orders_with_inventory(status, order_type, user, pagination)


@router.get("/orders/refreshCache")
async def refresh_cache(user: Auth0User = Depends(auth.get_user)):
    user_id = user.id.replace("auth0|", "")
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

    statuses = [
        "Partially Paid",
        "Signed",
        "Pod",
        "First_Payment_Received",
        "Expired",
        "Delinquent",
        "Paid",
        "Delivered",
        "Invoiced",
        "Delayed",
        "Approved",
        "Purchase_Order",
        "Estimate",
        "Current",
        "Completed",
        "Cancelled",
        "Returned",
        "Quote",
        "To_Deliver",
        "On_Rent",
    ]

    try:
        clear_cache(statuses, "PURCHASE", user_ids, user.app_metadata['account_id'])
        clear_cache(statuses, "PURCHASE_ACCESSORY", user_ids, user.app_metadata['account_id'])
        clear_cache(statuses, "RENT", user_ids, user.app_metadata['account_id'])
        clear_cache(statuses, "RENT_TO_OWN", user_ids, user.app_metadata['account_id'])
    except Exception as e:
        logger.info(str(e))


@router.get(
    "/orders",
    response_model=Dict[str, Any],
)
async def get_orders_by_status_type(
    status: str,
    order_type: str,
    emulated_user_id: str = None,
    product_type: str = None,
    pagination: PAGINATION = order_crud.pagination_depends,
    get_all: bool = False,
    pull_all: bool = False,
    auth_user: Auth0User = Depends(auth.get_user),
):
    return await orders.get_orders_by_status_type(
        status, order_type, auth_user, pagination, get_all, emulated_user_id, product_type, pull_all
    )


@router.delete("/rent_period/{rent_period_id}")
async def delete_rent_period(rent_period_id, user: Auth0User = Depends(auth.get_user)):
    await rent_period_controller.delete_rent_period(rent_period_id, user)


@router.get("/rankings")
@cache(namespace="rankings", expire=60 * 10)
async def generate_rankings(
    searched_user_ids: str = None,
    emulated_user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    pod_mode: bool = False,
    user: Auth0User = Depends(auth.get_user),
):
    return await orders.generate_rankings(
        user,
        searched_user_ids,
        emulated_user_id,
        start_date,
        end_date,
        pod_mode=pod_mode,
    )


@router.get("/search_orders")
async def search_orders_by_query_param(
    statuses: str = None,
    order_types: str = None,
    searched_user_ids: str = None,
    regions: str = None,
    pickup_regions: str = None,
    container_sizes: str = None,
    container_types: str = None,
    display_order_id: str = None,
    container_number: str = None,
    container_release_number: str = None,
    customer_name: str = None,
    customer_email: str = None,
    customer_phone: str = None,
    driver_id: str = None,
    not_driver_id: str = None,
    is_rush: bool = False,
    not_rush: bool = False,
    good_to_go: str = None,
    not_good_to_go: str = None,
    welcome_call: str = None,
    not_welcome_call: str = None,
    created_at: str = None,
    paid_at: str = None,
    signed_at: str = None,
    delivered_at: str = None,
    completed_at: str = None,
    container_id: str = None,
    not_container_id: str = None,
    pickup: str = None,
    not_pickup: str = None,
    start_date: str = None,
    end_date: str = None,
    emulated_user_id: str = None,
    scheduled_date: str = None,
    not_schedule_date: str = None,
    potential_date: str = None,
    not_potential_date: str = None,
    potential_driver: str = None,
    not_potential_driver: str = None,
    location: str = None,
    tracking_number: str = None,
    container_condition: str = None,
    product_type: str = None,
    customer_company_name: str = None,
    user: Auth0User = Depends(auth.get_user),
    pagination: PAGINATION = order_crud.pagination_depends,
):
    pagination = None
    if searched_user_ids and isinstance(searched_user_ids, str):
        searched_user_ids = searched_user_ids.split(',')
    filters = OrderSearchFilters(
        statuses=statuses,
        order_types=order_types,
        searched_user_ids=searched_user_ids if searched_user_ids else [],
        regions=regions,
        pickup_regions=pickup_regions,
        container_sizes=container_sizes,
        container_types=container_types,
        display_order_id=display_order_id,
        container_number=container_number,
        container_release_number=container_release_number,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        driver_id=driver_id,
        not_driver_id=not_driver_id,
        good_to_go=good_to_go,
        not_good_to_go=not_good_to_go,
        welcome_call=welcome_call,
        not_welcome_call=not_welcome_call,
        created_at=created_at,
        paid_at=paid_at,
        signed_at=signed_at,
        delivered_at=delivered_at,
        completed_at=completed_at,
        container_id=container_id,
        not_container_id=not_container_id,
        pickup=pickup,
        not_pickup=not_pickup,
        start_date=start_date,
        end_date=end_date,
        emulated_user_id=emulated_user_id,
        scheduled_date=scheduled_date,
        not_schedule_date=not_schedule_date,
        potential_date=potential_date,
        not_potential_date=not_potential_date,
        potential_driver=potential_driver,
        not_potential_driver=not_potential_driver,
        location=location,
        tracking_number=tracking_number,
        container_condition=container_condition,
        product_type=product_type,
        customer_company_name=customer_company_name,
        is_rush=is_rush,
        not_rush=not_rush,
    )

    return await orders.search_orders_by_query_param(user, pagination, filters)


@router.get("/all_orders", response_model=List[OrderOut])
async def get_all_orders(
    pagination: PAGINATION = order_crud.pagination_depends,
    user: Auth0User = Depends(auth.get_user),
):
    return await orders.get_all_orders(user, pagination)


@router.patch("/order/{order_id}", response_model=OrderOut)
async def update_order(
    order_id: str, order: UpdateOrder, backround_tasks: BackgroundTasks, Auth0User: Auth0User = Depends(auth.get_user)
):
    await FastAPICache.clear(namespace="commissions")
    await FastAPICache.clear(namespace="rankings")

    return await orders.update_order(order_id, order, Auth0User, backround_tasks)


@router.patch("/order_discount/{order_id}", response_model=OrderOut)
async def order_discount(order_id: str, backround_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)):
    return await orders.update_order_discount(order_id, backround_tasks, user)


@router.patch("/order_address/{address_id}/order/{order_id}", response_model=OrderOut)
async def update_order_address(
    address_id: str,
    order_address: CreateUpdateAddress,
    order_id: str,
    user: Auth0User = Depends(auth.get_user),
):
    return await orders.update_order_address(address_id, order_address, order_id, user)


@router.get("/orders_by_inventory_id")
async def orders_by_inventory_id(
    inventory_id: str = None,
    user: Auth0User = Depends(auth.get_user),
):
    return await orders.get_by_inventory_ids([inventory_id], user)


@router.post("/get_receipt_items_report")
async def get_receipt_items_report(filters: FilterObject, user: Auth0User = Depends(auth.get_user)):
    data = await get_orders_summary_rentals(filters)
    return get_receipt_items_report_post_processor(data)

class RequestDates(BaseModel):
    dates: List[datetime]

@router.post("/print_rental_statement_multiple_orders/{single_customer_id}")
async def print_rental_statement_multiple_orders(single_customer_id: str, request: RequestDates, user: Auth0User = Depends(auth.get_user)):
    rental_statement = await customer_statement_controller.print_rental_statement_multiple_orders(
        single_customer_id, user.app_metadata.get("account_id"), request
    )
    account = await account_crud.get_one(account_id=user.app_metadata.get("account_id"))

    api_key = account.integrations.get('docugenerate_api_key')
    pdf_generator = PdfGeneratorRentalStatementMultipleOrders(api_key=api_key, statement=rental_statement)
    pdf_url = await pdf_generator.download()
    
    return {"pdf_url": pdf_url}

@router.get("/generate_rental_statement_pdf")
async def generate_rental_statement_pdf(
    order_id: str,
    user: Auth0User = Depends(auth.get_user),
):
    rental_statement = await customer_statement_controller.generate_rental_statement_pdf(
        order_id, user.app_metadata.get("account_id")
    )
    account = await account_crud.get_one(account_id=user.app_metadata.get("account_id"))

    api_key = account.integrations.get('docugenerate_api_key')
    pdf_generator = PdfGeneratorRentalStatement(api_key=api_key, statement=rental_statement)
    pdf_url = await pdf_generator.download()
    result = await customer_statement_controller.generate_rental_statement_web(
        order_id, user.app_metadata.get("account_id")
    )
    result['pdf_url'] = pdf_url
    return result


@router.post("/generate_client_rental_statement_web/{order_id}")
async def generate_client_rental_statement_web(
    order_id: str,
    data: RentalStatementDataRequest,
    user: Auth0User = Depends(auth.get_user),
):
    result = await customer_statement_controller.generate_rental_statement_web(
        order_id, user.app_metadata.get("account_id"), data
    )
    return result


@router.post("/abrev_title")
async def abrev_title(
    data: Dict[Any, Any],
):
    pairs = await container_attribute_crud.get_all(1)
    container_products = await container_product_crud.get_all_all_accounts()
    for con in container_products:
        attrs = {}
        for cpa in con.container_product_attributes:
            attr = cpa.container_attribute.name
            for pair in pairs:
                if pair.name == attr:
                    attr = pair.value
                    break
            attrs[attr] = True

        found = False
        for attr in attrs:
            if not data['attributes'].get(attr, False):
                found = True
                break

        if not found and data['container_size'] == con.container_size and data['condition'] == con.condition:
            return con.title

    return 'Title not found'


@router.get("/generate_web_rental_order_table_data/{order_id}/{rent_period_id}")
async def generate_web_rental_order_table_data(order_id: str, rent_period_id: str):
    order = await order_crud.get_one(order_id)

    return await orders.generate_web_rental_order_table_data(order, rent_period_id)


@router.post("/generate_rent_receipt_pdf/{order_id}")
async def generate_rent_receipt_pdf(receipt: Receipt, order_id: str):
    order = await order_crud.get_one(order_id)
    pdf_url = await orders.generate_rent_receipt_pdf_docugenerate(order, receipt)
    return {"pdf_url": pdf_url}


@router.get("/generate_order_pdf")
async def generate_order_pdf(
    order_id: str,
    background_task: BackgroundTasks,
):
    headers = {'Content-Disposition': 'attachment; filename="invoice.pdf"'}
    order = await order_crud.get_one(order_id)
    account = await account_crud.get_one(order.account_id)

    if account.cms_attributes.get("use_paid_pdf_generator", False):
        pdf_url = await orders.generate_order_pdf_docugenerate(order, order_id)
        logger.info(pdf_url)
        return {"pdf_url": pdf_url}
    else:
        result = await orders.generate_order_pdf(order, order_id)
        buffer = BytesIO(result)
        background_task.add_task(buffer.close)
        return Response(buffer.getvalue(), headers=headers, media_type='application/pdf')


@router.get("/generate_rental_invoice_pdf")
async def generate_rental_invoice_pdf(order_id: str, rent_period_id: str):
    pdf_url = await orders.generate_rental_invoice_pdf_docugenerate(order_id, rent_period_id)
    logger.info(f"pdf_url: {pdf_url}")
    return {"pdf_url": pdf_url}


@atomic()
@router.delete("/order/{order_id}", response_model=Dict[str, Any])
async def delete_order(order_id: str, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)):
    if len([p for p in user.permissions if p == "delete:delete_orders"]) == 1:
        return await orders.archive_order(order_id, user, background_tasks=background_tasks)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete an order",
        )


@router.post("/get_rent_on_due_date")
async def get_rent_on_due_date(post: Dict[Any, Any], user: Auth0User = Depends(auth.get_user)):
    post['current_date'] = datetime.strptime(post['current_date'], '%Y-%m-%dT%H:%M:%S.%fZ')

    result = rent_period_controller.generate_single_rent_period_dates(1, post['current_date'], post['rent_due_on_day'])
    return result


@router.post("/notify_payment")
async def driver_payment_notification(post: Dict[Any, Any], user: Auth0User = Depends(auth.get_user)):
    return await orders.notify_driver_on_payment(post['order_id'], post['containers_paid_for'], user)


@router.get("/get_order_by_rent_period_id/{rent_period_id}")
async def get_order_by_rent_period_id(rent_period_id, user: Auth0User = Depends(auth.get_user)):
    return await orders.get_order_by_rent_period_id(rent_period_id, user)


@router.get("/duplicate_order/{order_id}")
async def duplicate_order(order_id: str, user: Auth0User = Depends(auth.get_user)):
    return await orders.duplicate_order(order_id, user)


@router.get("/chat_log/{phone}")
async def get_chat_log(phone: str, user: Auth0User = Depends(auth.get_user)):
    account = await account_crud.get_one(user.app_metadata['account_id'])
    account_sid = account.integrations.get("twilio", {}).get("account_sid", "")
    auth_token = account.integrations.get("twilio", {}).get("auth_token", "")
    from_phone = account.integrations.get("twilio", {}).get("from_phone", "")
    client = Client(account_sid, auth_token)
    days_ago = 5
    processed_messages = []

    date_filter = datetime.utcnow() - timedelta(days=days_ago)

    messages = client.messages.list(
        to=from_phone,
        date_sent_after=date_filter,
        from_=phone,
    )

    for message in messages:
        processed_messages.append(
            {'from': message.from_, 'body': message.body, 'date_sent': message.date_sent, 'status': message.status}
        )

    messages = client.messages.list(
        to=phone,
        date_sent_after=date_filter,
        from_=from_phone,
    )

    for message in messages:
        processed_messages.append(
            {'from': message.from_, 'body': message.body, 'date_sent': message.date_sent, 'status': message.status}
        )

    processed_messages = sorted(processed_messages, key=lambda x: x["date_sent"])
    return processed_messages


@router.post("/sms_received")
async def handle_sms(request: Request):
    form_data = await request.form()
    logger.info(form_data)
    days_ago = 30
    try:
        account = await account_crud.get_one(1)
        account_sid = account.integrations.get("twilio", {}).get("account_sid", "")
        auth_token = account.integrations.get("twilio", {}).get("auth_token", "")

        client = Client(account_sid, auth_token)

        # Calculate the date for filtering
        date_filter = datetime.utcnow() - timedelta(days=days_ago)

        # Retrieve messages
        messages = client.messages.list(
            to=form_data.get("From"),
            date_sent_after=date_filter,
            from_=form_data.get("To"),
        )

        # Process and return relevant information
        processed_messages = []
        for message in messages:
            processed_messages.append(
                {'from': message.from_, 'body': message.body, 'date_sent': message.date_sent, 'status': message.status}
            )

        logger.info(processed_messages)
        email_pattern = r'\b[a-zA-Z]\.deliveries@usacontainers\.net\b'
        order_pattern = r'#\d{6}\b'
        for message in processed_messages:
            matches = re.findall(email_pattern, message['body'])

            if matches:
                email = matches[0]

                matches_order_number = re.findall(order_pattern, message['body'])

                order_number = ""
                if matches_order_number:
                    order_number = matches_order_number[0]
                email_service_mailersend.send_message_from_customer_twilio(
                    order_number[1:], form_data.get("Body"), email, account
                )

    except TwilioRestException as e:
        logger.info(f"An error occurred: {e}")
        return []


@router.post("/calculate_remaining_balance/{order_id}")
async def calculate_remaining_balance(data: Dict[Any, Any], order_id):
    logger.info(order_id)
    logger.info(data)
    return await orders.calculate_remaining_balance(data['move_out_dates'], order_id)


@router.post("/transactions_rent_periods")
async def transactions_rent_periods(data: Dict[Any, Any], user: Auth0User = Depends(auth.get_user)):
    return await orders.transactions_rent_periods(data['start_date'], data['end_date'], data['display_order_id'], user)


@router.get("/get_tax_rate/{order_id}")
async def get_tax_rate(order_id):
    order = await order_crud.get_one(order_id)

    states = [line_item.product_state for line_item in order.line_items]

    state = ""
    if all(state == states[0] for state in states):
        state = states[0]
    tax_rate = await tax_crud.get_tax_rate(order.account_id, state)
    return tax_rate


@router.get(
    "/exported_orders",
    response_model=Dict[str, Any],
)
async def get_orders_by_status_type_for_export(
    status: str,
    order_type: str,
    emulated_user_id: str = None,
    displayOrderIds: List[str] = Query(default=[]),
    auth_user: Auth0User = Depends(auth.get_user),
    pagination: PAGINATION = order_crud.pagination_depends,
):
    if displayOrderIds:
        displayOrderIds = displayOrderIds[0].split(',')
    if emulated_user_id == 'null':
        emulated_user_id = None
    return await orders.get_exported_orders(
        status, order_type, emulated_user_id, auth_user, pagination, displayOrderIds
    )


@router.post('/update_rent_period_dates/{rent_period_id}')
async def update_rent_period_dates(
    rent_period_id: str, request: UpdateRentPeriodDates, auth_user: Auth0User = Depends(auth.get_user)
):
    await rent_period_controller.update_rent_period_dates(rent_period_id, request, auth_user)


@router.get("/orders_by_ids")
async def get_orders(ids: List[str] = Query(default=[]), auth_user: Auth0User = Depends(auth.get_user)):
    ids = ids[0].split(',')
    return await orders.get_orders(ids, auth_user)
