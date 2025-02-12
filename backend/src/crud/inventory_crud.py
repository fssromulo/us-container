# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.inventory.inventory import Inventory
from src.schemas.inventory import InventoryIn, InventoryOut


class InventoryCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = InventoryOut
        self.create_schema = InventoryIn
        self.update_schema = InventoryIn
        self.db_model = Inventory
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)


inventory_crud = InventoryCRUD()
