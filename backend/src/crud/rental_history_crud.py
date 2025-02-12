# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.rental_history import RentalHistory
from src.schemas.rental_history import RentalHistoryIn, RentalHistoryOut, RentalHistoryUpdate


class RentalHistoryCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = RentalHistoryOut
        self.create_schema = RentalHistoryIn
        self.update_schema = RentalHistoryUpdate
        self.db_model = RentalHistory

    async def get_one(self, rental_history_id: str) -> Model:
        model = await self.db_model.filter(id=rental_history_id).first()

        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def update(self, rental_history_id: str, model: Model) -> Model:
        if isinstance(model, self.update_schema):
            model = model.dict(exclude_unset=True)
            query = self.db_model.filter(id=rental_history_id)
            await query.update(**model)
            return await self.schema.from_queryset_single(self.db_model.get(id=rental_history_id))

    async def get_one_by_line_item_id(self, line_item_id: str) -> Model:
        model = await self.db_model.filter(line_item_id=line_item_id).first()

        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            return None


rental_history_crud = RentalHistoryCRUD()
