# Python imports
from datetime import datetime

# Pip imports
from fastapi import HTTPException
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.comission import Commission
from src.schemas.container_product_attribute import (
    ContainerProductAttribute,
    ContainerProductAttributeIn,
    ContainerProductAttributeOut,
)


NOT_FOUND = HTTPException(404, "Item not found")


class ContainerProductAttributeCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = ContainerProductAttributeOut
        self.create_schema = ContainerProductAttributeIn
        self.update_schema = ContainerProductAttributeOut
        self.db_model = ContainerProductAttribute
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )


container_product_attribute_crud = ContainerProductAttributeCRUD()
