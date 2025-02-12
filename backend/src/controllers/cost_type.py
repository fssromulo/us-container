# Python imports

# Pip imports
from typing import List
from tortoise import Model

# interal imports
from src.crud.cost_type import cost_type_crud
from src.auth.auth import Auth0User
from src.schemas.cost_type import CostTypeOut
from src.database.models.cost_type import CostType

async def get_all_types(user: Auth0User) -> List[CostTypeOut]:
    return await cost_type_crud.get_all(user.app_metadata.get("account_id"))
    
    
