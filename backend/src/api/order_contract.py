# Python imports
import json
from datetime import datetime, timezone
from typing import Any, Literal

# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from tortoise.transactions import atomic

# Internal imports
from src.controllers import contracts, notifications_controller, order_contract
from src.controllers import orders as order_controller
from src.controllers.payment import create_payment_info
from src.crud.account_crud import account_crud
from src.crud.order_crud import order_crud
from src.database.models.account import Account
from src.database.models.orders.order import Order
from src.schemas.orders import OrderInUpdate
from src.schemas.payment import Payment
from src.services.notifications import email_service, email_service_mailersend
from src.services.payment.authorize_pay_service import handle_create_authorize_customer_profile_id
from src.controllers.event_controller import order_pod_signed_agent_notification

router = APIRouter(
    tags=["order_contract"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

security: HTTPBasic = HTTPBasic()

A_MOBILE_BOX_ACCOUNT_NAME: str = "a mobile box"


@atomic
@router.post(path="/order_contract")
async def create_order_contract(
    webhook_json: dict, background_tasks: BackgroundTasks, credentials: HTTPBasicCredentials = Depends(security)
) -> Literal[200]:

    contract_info: dict = webhook_json.get("data", {})["contract"]
    api_key: str = credentials.username  # this will be the api key
    contract_order_id: str = contract_info.get("metadata", "")
    contract_title: str = contract_info.get("title", "")
    contract_status: str = webhook_json.get("status", "")
    all_signers: list = contract_info.get("signers", None)
    is_auto_pay_selected: bool = False
    contract_pdf_url: str | None = contract_info.get("contract_pdf_url", None)

    if all_signers is not None:
        first_signer_signed_info: dict[str, str] = all_signers[0]["signer_field_values"]

    try:
        existing_order: Order = await order_crud.get_one(item_id=contract_order_id)
    except HTTPException:
        raise
    account_id: int = existing_order.account_id
    try:
        account: Account = await account_crud.get_one(account_id=account_id)
    except HTTPException:
        raise
    account_name: str = account.cms_attributes.get('account_name')

    expected_api_key: str = account.integrations["esignatures.io"]["api_key"]

    if api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Basic"},
        )

    order_contract_dict: dict[str, Any] = {
        "status": contract_status,
        "contract_id": contract_info.get("id", ""),
        "meta_data": json.dumps(webhook_json),
        "order_id": contract_order_id,
        "contract_pdf_link": contract_pdf_url,
    }

    await order_contract.save_order_contract(order_contract_dict=order_contract_dict)

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=existing_order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    email_info: dict = {
        "customer_email": customer_info.get("email", ""),
        "display_order_id": existing_order.display_order_id,
        "url": contract_pdf_url,
        "company_name": account.cms_attributes.get("company_name"),
        "title": "",
        "text": "",
    }

    # if this is a signed rental contract notification, and the account does authorization forms
    if (
        contract_status.lower() == "contract-signed"
        and account_name.lower() == A_MOBILE_BOX_ACCOUNT_NAME
        and contract_title.lower().startswith("rent")
    ):
        is_auto_pay_selected = await order_contract.is_autopay_from_signed_contract(
            order_id=existing_order.id, account_id=account.id
        )

        email_info["title"] = "Signed Rental Agreement"
        email_info["text"] = "You can view a PDF of your signed agreement by clicking on the button below."

        # we have to send them the signed pdf url
        email_service_mailersend.send_signed_agreement(email_info=email_info)
        # if they have selected autopay, then we automatically send them an authorization form
        if is_auto_pay_selected:
            await contracts.send_authorization_agreement(order_id=existing_order.id)

    if (
        account_name.lower() == A_MOBILE_BOX_ACCOUNT_NAME
        and "authorization" in contract_title.lower()
        and contract_status.lower() == "contract-signed"
    ):
        is_auto_pay_selected = await order_contract.is_autopay_from_signed_contract(
            order_id=existing_order.id, account_id=account.id
        )
        authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})

        email_info["title"] = "Signed Authorization Form"
        email_info["text"] = "You can view a PDF of your signed form by clicking on the button below."

        # we have to send them the signed pdf url
        email_service_mailersend.send_signed_agreement(email_info=email_info)

        payment_obj: Payment = Payment(
            first_name=customer_info.get("first_name", ""),
            last_name=customer_info.get("last_name", ""),
            zip=first_signer_signed_info.get("zip", ""),
            avs_street=first_signer_signed_info.get("billing_address"),
            city=first_signer_signed_info.get("city", ""),
            state=first_signer_signed_info.get("state", ""),
            cardNumber=first_signer_signed_info.get("card_number", ""),
            expirationDate=first_signer_signed_info.get("expiration_date", ""),
            cardCode=first_signer_signed_info.get("cvv", ""),
            total_paid=0,
            convenience_fee_total=0,
            merchant_name=first_signer_signed_info.get("card_brand", ""),
            type=first_signer_signed_info.get("card_type", ""),
        )

        payment_info: dict[str, Any] = create_payment_info(existing_order=existing_order, payment_requst=payment_obj)

        # check to see if they selected auto pay or not
        # if they did, then we will want to set is_autopay = true for the order
        # else dont do anything

        # this will also handle if it is an autopay or not and updating the order
        await handle_create_authorize_customer_profile_id(
            existing_order=existing_order,
            payment_info=payment_info,
            authorize_int=authorize_int_rentals,
            account_id=account.id,
            is_autopay=is_auto_pay_selected,
        )

    if (
        account_name == "USA Containers"
        and (contract_status.lower() == "contract-signed")
        and contract_title.lower().startswith("rent")
    ):
        is_auto_pay_selected = True
        authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})

        payment_obj: Payment = Payment(
            first_name=customer_info.get("first_name", ""),
            last_name=customer_info.get("last_name", ""),
            zip=first_signer_signed_info.get("zip", ""),
            avs_street=first_signer_signed_info.get("billing_address"),
            city=first_signer_signed_info.get("city", ""),
            state=first_signer_signed_info.get("state", ""),
            cardNumber=first_signer_signed_info.get("card_number", ""),
            expirationDate=first_signer_signed_info.get("expiration_date", ""),
            cardCode=first_signer_signed_info.get("cvv", ""),
            total_paid=0,
            convenience_fee_total=0,
            merchant_name=first_signer_signed_info.get("card_brand", ""),
            type=first_signer_signed_info.get("card_type", ""),
        )

        payment_info: dict[str, Any] = create_payment_info(existing_order=existing_order, payment_requst=payment_obj)

        payment_info['cardNumber'] = first_signer_signed_info.get("credit_card_number", "")
        payment_info['expirationDate'] = first_signer_signed_info.get("credit_card_expiration_date", "")
        payment_info['cardCode'] = first_signer_signed_info.get("credit_card_cvv", "")
        payment_info['first_name'] = customer_info.get("first_name", "")
        payment_info['last_name'] = customer_info.get("last_name", "")
        payment_info['avs_street'] = first_signer_signed_info.get("credit_card_billing_address")
        payment_info['city'] = first_signer_signed_info.get("credit_card_billing_city", "")
        payment_info['state'] = first_signer_signed_info.get("credit_card_billing_state", "")
        payment_info['zip'] = first_signer_signed_info.get("credit_card_billing_zip", "")

        if first_signer_signed_info.get("bank_name"):
            payment_info['bank_name'] = first_signer_signed_info.get("bank_name")
            payment_info['routing_number'] = first_signer_signed_info.get("routing_number")
            payment_info['account_number'] = first_signer_signed_info.get("account_number")

        ach_priority = first_signer_signed_info.get('ach_payment_priority', False)
        if ach_priority:
            await order_crud.update(
                account_id,
                existing_order.id,
                OrderInUpdate(
                    **{
                        "primary_payment_method": "ACH",
                        "account_id": account_id,
                    }
                ),
            )
        else:
            await order_crud.update(
                account_id,
                existing_order.id,
                OrderInUpdate(
                    **{
                        "primary_payment_method": "CREDIT_CARD",
                        "account_id": account_id,
                    }
                ),
            )

        # this will also handle if it is an autopay or not and updating the order
        await handle_create_authorize_customer_profile_id(
            existing_order=existing_order,
            payment_info=payment_info,
            authorize_int=authorize_int_rentals,
            account_id=account.id,
            is_autopay=is_auto_pay_selected,
        )

    if contract_status.lower() == "contract-signed":
        if existing_order.type == 'RENT':
            await order_crud.update(
                account_id,
                existing_order.id,
                OrderInUpdate(
                    **{
                        "status": "Signed",
                        "user_id": existing_order.user.id,
                        "account_id": account_id,
                    }
                ),
            )
        # check if it is a py on delivery contract and set the signed date
        elif existing_order.type == "PURCHASE":
            if not existing_order.signed_at:
                await order_crud.update(
                    account_id,
                    existing_order.id,
                    OrderInUpdate(
                        **{"signed_at": datetime.now(timezone.utc), "account_id": account_id, "status": 'Pod'}
                    ),
                )
                # send paid questionnaire
                await notifications_controller.send_paid_email(existing_order.id, background_tasks)
                # send signed mail to agent
                email_text = f"You just had a customer sign the contract! Order #{existing_order.display_order_id}"
                if account.cms_attributes.get("sendInternalAgentEmails", True):
                    external_integrations = account.external_integrations
                    if external_integrations is not None and external_integrations.get("resources") is not None and len(external_integrations.get("resources")) > 0 and len([res for res in external_integrations.get("resources") if "update:user:signed_at" in res.get("event_types")]) > 0:
                        await order_pod_signed_agent_notification(existing_order.display_order_id, True, account_id, await order_controller.get_agent(existing_order), existing_order, await order_controller.get_agent_emails(existing_order), background_tasks)
                    else:
                        email_service.send_agent_email(email_text, await order_controller.get_agent_emails(existing_order))

    return status.HTTP_200_OK
