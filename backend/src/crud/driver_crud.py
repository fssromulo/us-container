# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.driver import Driver
from src.schemas.driver import DriverInSchema, DriverOutSchema


driver_crud = TortoiseCRUD(
    schema=DriverOutSchema,
    create_schema=DriverInSchema,
    update_schema=DriverInSchema,
    db_model=Driver,
)
