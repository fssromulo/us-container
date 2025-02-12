from src.schemas.cost_type import (
    CostTypeIn,
    CostTypeOut
)

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.cost_type import CostType

cost_type_crud = TortoiseCRUD(
    schema=CostTypeOut,
    create_schema=CostTypeIn,
    update_schema=CostTypeIn,
    db_model=CostType
)