# Internal imports
from src.crud.customer_application_schema_crud import customerApplicationSchemaCRUD
from src.crud.order_crud import order_crud
from src.schemas.customer_application import CustomerApplicationSchemaIn


async def create_customer_application_schema(application_schema: CustomerApplicationSchemaIn):
    return await customerApplicationSchemaCRUD.create(application_schema)


async def get_customer_application_schema(id: str, account_id: str):
    return await customerApplicationSchemaCRUD.get_one(account_id, id)


async def get_customer_application_schemas_by_name(name: str, order_id: str):
    order = await order_crud.get_one(order_id)
    return await customerApplicationSchemaCRUD.get_by_name(order.account_id, name)
