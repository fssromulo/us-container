
from src.schemas.orders import (
    OrderAddressIn,
    OrderAddressOut,
)
from tortoise.models import Model

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.order_address import OrderAddress

class AddressCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OrderAddressOut
        self.create_schema = OrderAddressIn
        self.update_schema = OrderAddressIn
        self.db_model = OrderAddress
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

address_crud = AddressCrud()