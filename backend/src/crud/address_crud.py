# Python imports
import logging
from typing import List

# Pip imports
from tortoise.expressions import Q
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.address import Address
from src.schemas.address import AddressIn, AddressOut


class AddressCRUD(TortoiseCRUD):
    def __init__(self) -> None:
        self.db_model = Address
        self.schema = AddressOut
        self.create_schema = AddressIn
        self.update_schema = AddressIn
        self.out_schema = AddressOut
        super().__init__(self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=5)

    async def updateWithoutRetrieval(self, account_id: int, item_id: int, model: Model) -> Model:  # type: ignore
        if isinstance(model, self.update_schema):
            model = model.dict(exclude_unset=True)
            if self.has_account_id():
                query = self.db_model.filter(account_id=account_id).filter(id=item_id)
            else:
                query = self.db_model.filter(id=item_id)
            await query.update(**model)


address_crud = AddressCRUD()
