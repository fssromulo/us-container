# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.schemas.acccessory_line_items import CreateAccessoryLineItem, AccessoryLineItemOut, AccessoryLineItemIn

from ..database.models.orders.accessory_line_item import AccessoryLineItem

# pip imports
from tortoise.models import Model

# python imports
from typing import List


class AccessoryLineItemCRUD(TortoiseCRUD):
    def __init__(self) -> None:
        self.schema = AccessoryLineItemOut
        self.create_schema = CreateAccessoryLineItem
        self.update_schema = AccessoryLineItemIn
        self.db_model = AccessoryLineItem
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

accessory_line_item_crud = AccessoryLineItemCRUD()
