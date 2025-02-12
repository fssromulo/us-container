# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.inventory.inventory_category import InventoryCategory
from src.schemas.inventory_category import InventoryCategoryIn, InventoryCategoryOut


class InventoryCategoryCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = InventoryCategoryOut
        self.create_schema = InventoryCategoryIn
        self.update_schema = InventoryCategoryIn
        self.db_model = InventoryCategory
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)


inventory_category_crud = InventoryCategoryCRUD()
