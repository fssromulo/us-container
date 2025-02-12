# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.tax_balance import TaxBalance
from src.schemas.tax_balance import TaxBalanceIn, TaxBalanceOut


class TaxBalanceCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = TaxBalanceOut
        self.create_schema = TaxBalanceIn
        self.update_schema = TaxBalanceIn
        self.db_model = TaxBalance
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_latest_balance(self, account_id: int, order_id: str):
        model = (
            await self.db_model.filter(account_id=account_id)
            .filter(order_id=order_id)
            .filter(is_currently_owed=True)
            .first()
        )
        return await self.schema.from_tortoise_orm(model)

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


tax_balance_crud = TaxBalanceCRUD()
