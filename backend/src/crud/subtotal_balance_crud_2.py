# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.subtotal_balance import SubtotalBalance
from src.schemas.subtotal_balance import SubtotalBalanceIn2, SubtotalBalanceOut


class SubtotalBalanceCRUD2(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = SubtotalBalanceOut
        self.create_schema = SubtotalBalanceIn2
        self.update_schema = SubtotalBalanceIn2
        self.db_model = SubtotalBalance
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)


subtotal_balance_crud_2 = SubtotalBalanceCRUD2()
