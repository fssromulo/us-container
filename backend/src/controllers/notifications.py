# Internal imports
from src.controllers.orders import check_is_single_customer_order
from src.auth.auth import Auth0User
from src.controllers.customer_statement import customer_statement_controller
from src.crud.account_crud import account_crud  # noqa: E402
from src.schemas.token import Status
from src.services.notifications import email_service, email_service_mailersend
from src.services.invoice.pdf_generation import PdfGeneratorRentalStatement
from src.crud.order_crud import order_crud

async def handle_customer_rental_statement(order_id: str, user: Auth0User):
    # calculated_line_items_title
    statement = await customer_statement_controller.generate_rental_statement_pdf(
        order_id, user.app_metadata.get("account_id"), 0
    )

    account = await account_crud.get_one(account_id=user.app_metadata.get("account_id"))

    
    api_key = account.integrations.get('docugenerate_api_key')
    pdf_generator = PdfGeneratorRentalStatement(api_key=api_key,
                                                statement=statement)
    pdf_url = await pdf_generator.download()

    order = await order_crud.get_one(order_id)

    customer_info_dict = check_is_single_customer_order(order)

    email_service_mailersend.send_customer_rental_statement( 
        pdf_url,
        customer_info_dict.get("email"),
        order.display_order_id,
        account=account
    )

    return Status(message="Rental statement has been sent")
