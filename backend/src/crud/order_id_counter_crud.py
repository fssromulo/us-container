# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.order_id_counter import OrderIdCounter
from src.schemas.order_id_counter import OrderIdCounterIn, OrderIdCounterOut, OrderIdCounterUpdate


class OrderIdCounterCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OrderIdCounterOut
        self.create_schema = OrderIdCounterIn
        self.update_schema = OrderIdCounterUpdate
        self.db_model = OrderIdCounter
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )


order_id_counter_crud = OrderIdCounterCrud()
