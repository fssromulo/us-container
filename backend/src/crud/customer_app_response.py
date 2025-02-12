# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.customer_application_response import CustomerApplicationResponse
from src.schemas.customer_application import CustomerApplicationResponseIn, CustomerApplicationResponseOut


customer_app_response_crud = TortoiseCRUD(
    schema=CustomerApplicationResponseOut,
    create_schema=CustomerApplicationResponseIn,
    update_schema=CustomerApplicationResponseIn,
    db_model=CustomerApplicationResponse,
)
