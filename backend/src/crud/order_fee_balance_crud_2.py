# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.order_fee_balance import OrderFeeBalance
from src.schemas.order_fee_balance import OrderFeeBalanceIn2, OrderFeeBalanceOut


class OrderFeeBalanceCRUD2(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OrderFeeBalanceOut
        self.create_schema = OrderFeeBalanceIn2
        self.update_schema = OrderFeeBalanceIn2
        self.db_model = OrderFeeBalance
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)


order_fee_balance_crud_2 = OrderFeeBalanceCRUD2()
