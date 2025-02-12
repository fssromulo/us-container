# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.vendor_types import VendorType
from src.schemas.vendor_types import VendorTypeInSchema, VendorTypeOutSchema


class VendorTypeCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = VendorTypeOutSchema
        self.create_schema = VendorTypeInSchema
        self.update_schema = VendorTypeInSchema
        self.db_model = VendorType
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )


vendor_type_crud = VendorTypeCRUD()
