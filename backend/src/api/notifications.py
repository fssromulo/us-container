# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
import re

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import notifications, notifications_controller
from src.controllers.orders import generate_rent_receipt_pdf_docugenerate
from src.crud.order_crud import order_crud
from src.crud.account_crud import account_crud
from src.dependencies import auth
from src.schemas.notifications import ConfirmationDeliveryDateModel, PotentialDeliveryDateModel, TimeFrameModel
from src.schemas.orders import Receipt
from src.schemas.token import Status
from src.services.notifications.email_service import send_tracking_number_attached

router = APIRouter(
    tags=["notifications"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.post("/send/paid_email/{order_id}")
async def send_paid_email(order_id: str, background_tasks: BackgroundTasks):
    return await notifications_controller.send_paid_email(order_id, background_tasks)


@router.post("/send/time_frame_email/{line_item_id}/{order_id}", response_model=Status)
async def send_time_frame_email(
    line_item_id: str, order_id: str, time_frame: TimeFrameModel, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    return await notifications_controller.send_time_frame_mail(
        line_item_id, order_id, time_frame.start_date, time_frame.end_date, user, background_tasks
    )


def find_emails(text):
    # Regular expression pattern for matching email addresses
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Find all matches in the text
    emails = re.findall(pattern, text)

    return emails

@router.post("/email_rental_receipt/{order_id}/{email_to_address}", response_model=Status)
async def send_rental_receipt(order_id: str, email_to_address: str, receipt: Receipt):
    order = await order_crud.get_one(order_id)

    rental_pdf_link = await generate_rent_receipt_pdf_docugenerate(order, receipt)
    emails = find_emails(email_to_address)

    for email in emails:
        await notifications_controller.send_rental_receipt(order_id, email, rental_pdf_link)
    return Status(message="Notification has been sent")

@router.post("/send/potential_delivery_email/{line_item_id}/{order_id}", response_model=Status)
async def send_potentiel_delivery_email(
    line_item_id: str,
    order_id: str,
    potential_date: PotentialDeliveryDateModel,
    background_tasks: BackgroundTasks,
    user: Auth0User = Depends(auth.get_user),
):
    delete_line_item = [p for p in user.permissions if p == "update:order_column-potential_date"]
    if not delete_line_item:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to send this email",
        )
    return await notifications_controller.send_potential_mail(
        line_item_id, order_id, potential_date.potential_date, user, background_tasks
    )


@router.post("/send/confirmation_date_email/{line_item_id}/{order_id}", response_model=Status)
async def send_confirmation_date_email(
    line_item_id: str,
    order_id: str,
    confirmation_date: ConfirmationDeliveryDateModel,
    background_tasks: BackgroundTasks,
    user: Auth0User = Depends(auth.get_user),
):
    delete_line_item = [p for p in user.permissions if p == "update:order_column-potential_date"]
    if not delete_line_item:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to send this email",
        )
    return await notifications_controller.send_confirmation_date_mail(
        line_item_id, order_id, confirmation_date.scheduled_date, user, background_tasks
    )


@router.post("/send/tracking_numbers_email/{order_id}")
async def send_tracking_number_attached_api(
    order_id: str,
    user: Auth0User = Depends(auth.get_user),
):
    order = await order_crud.get_one(order_id)
    return send_tracking_number_attached(order)


@router.get('/send/rental_statement_email/{order_id}', response_model=Status)
async def send_rental_statement_email(order_id, user: Auth0User = Depends(auth.get_user)):
    return await notifications.handle_customer_rental_statement(order_id, user)
