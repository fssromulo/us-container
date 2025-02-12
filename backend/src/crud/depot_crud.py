from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.inventory.depot import Depot
from tortoise.models import Model

from src.schemas.depot import (
    DepotOutSchema,
    DepotInSchema,
    CreateOrUpdateDepot
)


depot_crud = TortoiseCRUD(
    schema=DepotOutSchema,
    create_schema=DepotInSchema,
    update_schema=DepotInSchema,
    db_model=Depot,
)

class DepotCrud(TortoiseCRUD):
    def __init__(self) -> None:
        self.db_model = Depot
        self.schema = DepotOutSchema
        self.create_schema = DepotInSchema
        self.update_schema = DepotInSchema
        super().__init__(self.schema, self.db_model,self.create_schema, self.update_schema)

    async def get_by_name(self, account_id:int, name:str) -> Model:
        try:
            query = self.db_model.filter(account_id=account_id)
            results = await query.get(name=name)
            return results
        except:
            raise

    async def get_by_account(self, account_id:int):
        try:
            query = await self.db_model.filter(account_id=account_id).get()
            return query
        except:
            raise

depot_crud = DepotCrud()
