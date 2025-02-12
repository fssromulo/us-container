# Python imports
import os

# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends, status, HTTPException
from loguru import logger

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import customers
from src.crud.account_crud import account_crud
from src.database.models.account import Account
from src.dependencies import auth
from src.schemas.address import CreateAddress
from src.schemas.customer import CreateCustomerOrder, CustomerOut, UpdateCustomerOrder
from src.schemas.customer_contact import CreateCustomerContact, EditCustomerContact, NewCustomerContact
from src.schemas.customer_simple import CreateCustomer
from src.schemas.orders import OrderOut
from src.schemas.payment import QuickRent, QuickSalePayment
from src.crud.assistant_crud import assistant_crud
from src.utils.order_update_in_cache import clear_cache
from loguru import logger

BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")

router = APIRouter(
    tags=["customers"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/single_customer/{customer_id}")
async def get_single_customer(customer_id: str, user: Auth0User = Depends(auth.get_user)):
    return await customers.get_single_customer(customer_id, user)


@router.get("/customer/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: str, user: Auth0User = Depends(auth.get_user)):
    return await customers.get_customer(customer_id, user)


@router.get("/unlink_single_customer/{order_id}")
async def unlink_single_customer(order_id: str, user: Auth0User = Depends(auth.get_user)):
    return await customers.unlink_single_customer(order_id, user.app_metadata["account_id"])


@router.get("/single_customer_contacts/{single_customer_id}")
async def fetch_customers_contact(single_customer_id: str, user: Auth0User = Depends(auth.get_user)):
    logger.info(single_customer_id)
    return await customers.fetch_single_customer_contacts(single_customer_id, user.app_metadata["account_id"])


@router.delete("/single_customer_contacts/{contact_id}/{address_id}")
async def delete_customers_contact(contact_id: str, address_id: str, user: Auth0User = Depends(auth.get_user)):
    return await customers.remove_single_customer_contacts(contact_id=contact_id, address_id=address_id)


@router.patch("/single_customer_contacts")
async def edit_customers_contact(data: EditCustomerContact, user: Auth0User = Depends(auth.get_user)):
    return await customers.edit_single_customer_contacts(data, user.app_metadata["account_id"])


@router.post("/single_customer_contacts")
async def add_customers_contact(data: NewCustomerContact, user: Auth0User = Depends(auth.get_user)):
    return await customers.add_single_customer_contacts(data, user.app_metadata["account_id"])


@router.get("/single_customer_id_orders/{single_customer_id}")
async def search_single_customers_by_query_parameters(
    single_customer_id: str, user: Auth0User = Depends(auth.get_user)
):
    return await customers.search_single_customer_id(single_customer_id, user.app_metadata["account_id"])


@router.get("/search_customers")
async def search_customers_by_query_parameters(
    name: str = None,
    phone: str = None,
    email: str = None,
    companyName: str = None,
    user: Auth0User = Depends(auth.get_user),
):
    return await customers.search_customers_by_query_parameters(
        name, phone, email, companyName, user.app_metadata["account_id"]
    )


@router.get("/search_single_customers")
async def search_single_customers_by_query_parameters(
    name: str = None, phone: str = None, email: str = None, user: Auth0User = Depends(auth.get_user)
):
    return await customers.search_single_customers_by_query_parameters(
        name, phone, email, user.app_metadata["account_id"]
    )


@router.post("/merge_customers")
async def merge_customers(data: UpdateCustomerOrder, user: Auth0User = Depends(auth.get_user)):
    return await customers.merge_customers(data, user.app_metadata["account_id"])


@router.post("/customer", response_model=CustomerOut)
async def create_customer(
    customer: CreateCustomerOrder, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    type = customer.order.type
    result = await customers.create_customer(customer, user, background_tasks)
    
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

    try:
        clear_cache(['Invoiced', 'Estimate'], type, user_ids, user.app_metadata['account_id'])
    except Exception as e:
        logger.info(str(e))
        
    return result


@router.post("/quick_sale")
async def create_quick_sale_customer(
    quick_sale: QuickSalePayment, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    account: Account = await account_crud.get_one(user.app_metadata.get("account_id"))
    order_configuration = {}
    result = await customers.create_quick_sale(
        quick_sale, user, account, order_configuration, background_tasks=background_tasks
    )
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
    
    try:
        clear_cache(['Invoiced', 'Estimate'], "PURCHASE", user_ids, user.app_metadata['account_id'])
    except Exception as e:
        logger.error(str(e))
    return result


@router.post("/quick_rent")
async def create_quick_rent_customer(
    quick_rent: QuickRent, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    account: Account = await account_crud.get_one(user.app_metadata.get("account_id"))
    order_configuration = {}
    result = await customers.create_quick_rent(quick_rent, user, account, order_configuration, background_tasks)

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

    try:
        clear_cache(['Invoiced', 'Estimate'], "RENT", user_ids, user.app_metadata['account_id'])
    except Exception as e:
        logger.info(str(e))
    return result

@router.post("/generic_customer", response_model=CustomerOut)
async def create_generic_customer(
    customer: CreateCustomerOrder, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    account: Account = await account_crud.get_one(user.app_metadata.get("account_id"))
    order_configuration = {}
    order_configuration["remaining_balance_is_zero"] = True
    order_configuration["create_initial_rent_period"] = False
    result = await customers.create_generic_customer(customer, account, user, order_configuration, background_tasks)
    
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

    try:
        clear_cache(['Invoiced', 'Estimate'], customer.order.type, user_ids, user.app_metadata['account_id'])
    except Exception as e:
        logger.info(str(e))
        
    return result

@router.patch("/customer/{customer_id}", response_model=OrderOut)
async def update_customer(
    customer_id: str,
    customer: UpdateCustomerOrder,
    background_tasks: BackgroundTasks,
    user: Auth0User = Depends(auth.get_user),
):
    result = await customers.update_customer(customer_id, customer, user)
    
    return result


@router.patch("/customer_profile/{customer_id}", response_model=OrderOut)
async def update_customer_profile(customer_id: str, customer: CreateCustomer, user: Auth0User = Depends(auth.get_user)):
    return await customers.update_customer_profile(customer_id, customer, user)


@router.patch("/customer_contacts/{customer_contacts_id}")
async def update_customer_contacts(
    customer_contacts_id: str, customer_contacts: CreateCustomerContact, user: Auth0User = Depends(auth.get_user)
):
    return await customers.update_customer_contacts(customer_contacts_id, customer_contacts, user)


@router.patch("/customer_address/{customer_address_id}")
async def update_customer_address(
    customer_address_id: str, customer_address: CreateAddress, user: Auth0User = Depends(auth.get_user)
):
    return await customers.update_customer_address(customer_address_id, customer_address, user)
