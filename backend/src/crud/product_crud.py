# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.pricing.product import Product
from src.schemas.product import ProductIn, ProductOut


class ProductCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = ProductOut
        self.create_schema = ProductIn
        self.update_schema = ProductIn
        self.db_model = Product
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)


product_crud = ProductCRUD()
