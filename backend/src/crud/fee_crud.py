
# ...
from src.auth.auth import Auth0User
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.schemas.fee import (
    FeeIn,
    FeeOut,
    FeeInUpdate
)

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.fee import Fee

class FeeCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = FeeOut
        self.create_schema = FeeIn
        self.update_schema = FeeInUpdate
        self.db_model = Fee
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=200,
        )

    async def remove_order_rush_fees(self, order_id: str, user: Auth0User) -> List[Model]:
        fees = await self.db_model.filter(fee_type="RUSH", order_id=order_id)
        await self.db_model.filter(fee_type="RUSH", order_id=order_id).delete()
        return fees
        # return await self.db_model.filter(fee_type="RUSH", order_id=order_id)


fee_crud = FeeCrud()
