# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.rent_period_tax_balance import RentPeriodTaxBalance
from src.schemas.rent_period_tax_balance import RentPeriodTaxBalanceIn, RentPeriodTaxBalanceOut


class RentPeriodTaxBalanceCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = RentPeriodTaxBalanceOut
        self.create_schema = RentPeriodTaxBalanceIn
        self.update_schema = RentPeriodTaxBalanceIn
        self.db_model = RentPeriodTaxBalance
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

    async def get_by_rental_id(self, rent_period_id):
        query = self.db_model.filter(rent_period_id=rent_period_id)
        return await self.schema.from_queryset(query)

    async def get_all_by_rent_period_id(self, rent_period_id):
        query = self.db_model.filter(rent_period_id=rent_period_id)
        return await self.schema.from_queryset(query)

rent_period_tax_balance_crud = RentPeriodTaxBalanceCRUD()
