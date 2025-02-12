# Python imports
from datetime import datetime
from fastapi import BackgroundTasks

# Internal imports
from src.auth.auth import Auth0User
from src.crud.account_crud import account_crud  # noqa: E402
from src.crud.line_item_crud import LineItemCrud
from src.crud.note_crud import note_crud
from src.crud.order_crud import OrderCRUD
from src.database.models.orders.line_item import LineItem
from src.schemas.notes import NoteInSchema
from src.schemas.orders import Order
from src.schemas.token import Status
from src.services.notifications import email_service, email_service_mailersend
from src.utils.convert_time import convert_time_date, date_strftime
from src.controllers.event_controller import send_event, timeframe_event, confirmation_event, potential_date_event
from src.utils.utility import make_json_serializable
from src.utils.order_zone import fetch_region, fetch_region_signature
from src.controllers.event_controller import paid_at_event

order_crud = OrderCRUD()
linetitem_crud = LineItemCrud()

    # existing_order = await order_crud.get_one(order_id, True)
    # account = await account_crud.get_one(existing_order.account_id)
    # if account.name.startswith("USA Containers"):
    #
    # else :

async def send_paid_email(order_id: str, background_tasks: BackgroundTasks = None) -> Status:
    order: Order = await order_crud.get_one(order_id, True)
    order_d = order.dict()
    product_city = None
    for line_item in order.line_items:
        if line_item.product_city:
            product_city = line_item.product_city
    signature = await fetch_region_signature(product_city, order.account_id)
    account = await account_crud.get_one(order.account_id)
    uses_external_notifications = account.cms_attributes.get("external_notifications", {}).get("paid_at", False)
    if uses_external_notifications:
        return  await paid_at_event(order, order.paid_at, background_tasks)
    else:
        email_info = {
            "text": account.cms_attributes.get("emails", {}).get("payment", ""),
            "order_title": order_d.get("status", "Invoice"),
            "account_name": account.name,
            "display_order_id": order_d.get("display_order_id"),
            **order_d,
        }
        await email_service_mailersend.send_paid_email(email_info)
        return Status(message="Notification has been sent")


async def send_rental_receipt(
    order_id: str,
    email_to_address: str,
    rental_pdf_link: str,
) -> Status:
    order: Order = await order_crud.get_one(order_id, True)
    account = await account_crud.get_one(order.account_id)

    if account.name.startswith("USA Containers"):
        pass
    else:
        await email_service_mailersend.send_rental_receipt(email_to_address, rental_pdf_link, order_id, account)
    return Status(message="Notification has been sent")


async def send_time_frame_mail(
    line_item_id: str, order_id: str, start_date: str, end_date: str, user: Auth0User, background_tasks
) -> Status:
    order: Order = await order_crud.get_one(order_id, True)
    line_item: LineItem = await linetitem_crud.get_one(user.app_metadata.get("id"), line_item_id)
    order_d = order.dict()
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    await note_crud.create(
        NoteInSchema(
            title="Time Frame Date Sent",
            content=f"Time frame email sent for dates {date_strftime(start_dt, '%a, %B {S} %Y')} & {date_strftime(end_dt, '%a, %B {S} %Y')}",
            author_id=user.app_metadata.get("id"),
            line_item_id=line_item_id,
            order_id=order_id,
        )
    )
    await timeframe_event(line_item, order, start_dt, end_dt, background_tasks)
    # background_tasks.add_task(send_event, user.app_metadata['account_id'], str(line_item.id), make_json_serializable(event_payload), "line_item", "update", 'update:line_item:time_frame')
    # email_service.send_time_frame_email(
    #     order_d,
    #     date_strftime(start_dt, '%a, %B {S} %Y'),
    #     date_strftime(end_dt, '%a, %B {S} %Y'),
    #     await fetch_region_signature(line_item.product_city, order.account_id),
    # )
    return Status(message="Time frame has been sent")


async def send_potential_mail(line_item_id: str, order_id: str, potential_date: str, user: Auth0User, background_tasks) -> Status:
    order: Order = await order_crud.get_one(order_id, True)
    line_item: LineItem = await linetitem_crud.get_one(user.app_metadata.get("id"), line_item_id)
    potential_dt = datetime.strptime(potential_date, '%Y-%m-%d')
    order_d = order.dict()

    formatted_date: datetime = convert_time_date(date_component=potential_dt.date())

    # Update the LineItem with the datetime_with_time
    await LineItem.filter(id=line_item_id).update(potential_date=formatted_date)
    await potential_date_event(line_item,  date_strftime(potential_dt, '%a, %B {S} %Y'), background_tasks)
    # email_service.send_potential_email(
    #     order_d,
    #     date_strftime(potential_dt, '%a, %B {S} %Y'),
    #     await fetch_region_signature(line_item.product_city, order.account_id),
    # )
    await note_crud.create(
        NoteInSchema(
            title="Potential Date Sent",
            content=f"Customer has been emailed asking if {date_strftime(potential_dt, '%a, %B {S} %Y')} works for a delivery date",
            author_id=user.app_metadata.get("id"),
            line_item_id=line_item_id,
            order_id=order_id,
        )
    )
    return Status(message="Potential date has been sent")


async def send_confirmation_date_mail(line_item_id: str, order_id: str, scheduled_date: str, user: Auth0User, background_tasks) -> Status:
    order: Order = await order_crud.get_one(order_id, True)
    line_item: LineItem = await linetitem_crud.get_one(user.app_metadata.get("id"), line_item_id)
    scheduled_dt: datetime = datetime.strptime(scheduled_date, '%Y-%m-%d')
    order_d = order.dict()

    formatted_date: datetime = convert_time_date(date_component=scheduled_dt.date())

    await LineItem.filter(id=line_item_id).update(scheduled_date=formatted_date)
    await confirmation_event(line_item, order, date_strftime(scheduled_dt, '%a, %B {S} %Y'), background_tasks)

    # email_service.send_confirmation_date_email(
    #     order_d,
    #     date_strftime(scheduled_dt, '%a, %B {S} %Y'),
    #     await fetch_region_signature(line_item.product_city, order.account_id),
    # )
    return Status(message="Confirmation date has been sent")





