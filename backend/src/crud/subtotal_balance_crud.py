# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.subtotal_balance import SubtotalBalance
from src.schemas.subtotal_balance import SubtotalBalanceIn, SubtotalBalanceOut


class SubtotalBalanceCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = SubtotalBalanceOut
        self.create_schema = SubtotalBalanceIn
        self.update_schema = SubtotalBalanceIn
        self.db_model = SubtotalBalance
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_by_order_id(self, order_id: str):
        models = await self.db_model.filter(order_id=order_id)
        if models:
            results = []
            for model in models:
                await model.fetch_related()
                result = await self.schema.from_tortoise_orm(model)
                results.append(result)
            return results
        else:
            return []


subtotal_balance_crud = SubtotalBalanceCRUD()
