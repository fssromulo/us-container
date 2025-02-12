
# ...

from src.schemas.country import (
    countryIn,
    countryOut,
)

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.country import Country

country_crud = TortoiseCRUD(
    schema=countryOut,
    create_schema=countryIn,
    update_schema=countryIn,
    db_model=Country,
)
