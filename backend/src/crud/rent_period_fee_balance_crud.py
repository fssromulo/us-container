# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.rent_period_fee_balance import RentPeriodFeeBalance
from src.schemas.rent_period_fee_balance import RentPeriodFeeBalanceIn, RentPeriodFeeBalanceOut


class RentPeriodFeeBalanceCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = RentPeriodFeeBalanceOut
        self.create_schema = RentPeriodFeeBalanceIn
        self.update_schema = RentPeriodFeeBalanceIn
        self.db_model = RentPeriodFeeBalance
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
        )

    async def get_distinct_rent_period_ids(self):
        order_ids = await self.db_model.all().distinct().values("rent_period_id")
        return [entry['rent_period_id'] for entry in order_ids]

    async def get_by_rental_id(self, rent_period_id):
        query = self.db_model.filter(rent_period_id=rent_period_id)
        return await self.schema.from_queryset(query)


    async def get_all_by_rent_period_id(self, rent_period_id):
        query = self.db_model.filter(rent_period_id=rent_period_id)
        return await self.schema.from_queryset(query)

rent_period_fee_balance_crud = RentPeriodFeeBalanceCRUD()
