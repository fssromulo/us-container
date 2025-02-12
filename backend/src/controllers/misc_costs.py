# Python imports

# Pip imports
from typing import List
from tortoise import Model

# interal imports
from src.schemas.misc_cost import MiscCostIn
from src.crud.misc_cost import misc_cost_crud
from src.auth.auth import Auth0User
from src.schemas.token import Status

async def create_misc_cost(misc_cost: List[MiscCostIn], user: Auth0User) -> Status:
    await misc_cost_crud.db_model.bulk_create([misc_cost_crud.db_model(**m.dict())for m in misc_cost])
    return Status(message="Misc Cost(s) created")

async def update_misc_cost(misc_cost: List[MiscCostIn], user: Auth0User) -> Status:
    await misc_cost_crud.db_model.bulk_update([misc_cost_crud.db_model(**m.dict())for m in misc_cost], fields=["cost_type_id", "amount"])
    return Status(message="Misc Costs updated")

async def delete_misc_cost(misc_cost_id: str, user: Auth0User) -> Status:
    await misc_cost_crud.delete_one(user.app_metadata.get("account_id"), misc_cost_id)
    return Status(message="Misc Cost deleted")
