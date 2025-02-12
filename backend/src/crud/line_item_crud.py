# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.schemas.line_items import LineItemIn, LineItemInUpdate, LineItemOut
from src.crud.accessory_line_item_crud import accessory_line_item_crud
from src.schemas.acccessory_line_items import CreateAccessoryLineItem

from ..database.models.orders.line_item import LineItem

# pip imports
from tortoise.models import Model

# python imports
from typing import List


class LineItemCrud(TortoiseCRUD):
    def __init__(self) -> None:
        self.schema = LineItemOut
        self.create_schema = LineItemIn
        self.update_schema = LineItemInUpdate
        self.db_model = LineItem
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_by_order_id(self, order_id:str) -> List[Model]:
        query = self.db_model.filter(order_id=order_id)
        return await self.schema.from_queryset(query)
    async def get_by_ids(self, line_item_ids:List[str]) -> List[Model]:
        query = self.db_model.filter(id__in=line_item_ids)
        return await self.schema.from_queryset(query)

    async def saveWithAccessory(self, line_item: LineItemIn, accessory_line_item: CreateAccessoryLineItem) -> Model:
            line_item_model = line_item.dict()
            db_model = self.db_model(**line_item_model)
            await db_model.save()
            line_item_out = await self.schema.from_tortoise_orm(db_model)
            accessory_line_item.line_item_id = str(line_item_out.id)
            await accessory_line_item_crud.create(accessory_line_item)
            return line_item_out

line_item_crud = LineItemCrud()
