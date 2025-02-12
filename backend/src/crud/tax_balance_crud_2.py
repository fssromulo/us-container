# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.tax_balance import TaxBalance
from src.schemas.tax_balance import TaxBalanceIn2, TaxBalanceOut


class TaxBalanceCRUD2(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = TaxBalanceOut
        self.create_schema = TaxBalanceIn2
        self.update_schema = TaxBalanceIn2
        self.db_model = TaxBalance
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_all_small_balance(self):
        model = self.db_model.filter(balance__lt=0.01, balance__gt=0)
        return await self.schema.from_queryset(model)

    async def get_from_order_id(self, order_id):
        model = self.db_model.filter(order_id=order_id)
        return await self.schema.from_queryset(model)

tax_balance_crud_2 = TaxBalanceCRUD2()
