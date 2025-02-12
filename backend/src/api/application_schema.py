# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends

# Internal imports
from src.controllers import application_schema as application_schema_controller
from src.dependencies import auth
from src.schemas.customer_application import CustomerApplicationSchemaIn, CustomerApplicationSchemaOut


router = APIRouter(
    tags=["customer_application_schema"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.post("/customer_application_schema", response_model=CustomerApplicationSchemaOut)
async def create_customer_application_schema(
    application_schema: CustomerApplicationSchemaIn,
) -> CustomerApplicationSchemaOut:
    return await application_schema_controller.create_customer_application_schema(application_schema)


@router.get("/customer_application_schema/{account_id}/{id}", response_model=CustomerApplicationSchemaOut)
async def get_customer_application_schema(id: str, account_id: str) -> CustomerApplicationSchemaOut:
    return await application_schema_controller.get_customer_application_schema(id, account_id)


@router.get("/get_application_schemas_by_name/{name}/{order_id}", response_model=List[CustomerApplicationSchemaOut])
async def get_customer_application_schemas_by_name(name: str, order_id: str):
    return await application_schema_controller.get_customer_application_schemas_by_name(name, order_id)
