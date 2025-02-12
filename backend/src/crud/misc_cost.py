from src.schemas.misc_cost import (
    MiscCostIn,
    MiscCostOut
)

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.misc_cost import MiscCost

misc_cost_crud = TortoiseCRUD(
    schema=MiscCostOut,
    create_schema=MiscCostIn,
    update_schema=MiscCostIn,
    db_model=MiscCost
)