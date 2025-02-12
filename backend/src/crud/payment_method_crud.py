# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.payment_method import PaymentMethod
from src.schemas.payment_method import PaymentMethodInSchema, PaymentMethodOutSchema


class PaymentMethodCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = PaymentMethodOutSchema
        self.create_schema = PaymentMethodInSchema
        self.update_schema = PaymentMethodInSchema
        self.db_model = PaymentMethod
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

payment_method_crud = PaymentMethodCrud()
