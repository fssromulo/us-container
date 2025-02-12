# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.pricing.other_product import OtherProduct
from src.schemas.other_product import OtherProductIn, OtherProductOut


class OtherProductCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OtherProductOut
        self.create_schema = OtherProductIn
        self.update_schema = OtherProductIn
        self.db_model = OtherProduct
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)


other_product_crud = OtherProductCRUD()
