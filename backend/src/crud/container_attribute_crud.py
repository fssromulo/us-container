# Python imports
from datetime import datetime

# Pip imports
from fastapi import HTTPException
from loguru import logger
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.comission import Commission
from src.schemas.container_attribute import ContainerAttribute, ContainerAttributeIn, ContainerAttributeOut


NOT_FOUND = HTTPException(404, "Item not found")


class ContainerAttributeCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = ContainerAttributeOut
        self.create_schema = ContainerAttributeIn
        self.update_schema = ContainerAttributeOut
        self.db_model = ContainerAttribute
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    async def get_by_name(self, name: str) -> Model:
        model = await self.db_model.filter(name=name).first()
        if model:
            results = await self.schema.from_tortoise_orm(model)
            logger.info(results)
            return results
        else:
            raise NOT_FOUND
        
    async def get_by_value(self, value: str) -> Model:
        model = await self.db_model.filter(value=value).first()
        if model:
            results = await self.schema.from_tortoise_orm(model)
            logger.info(results)
            return results
        else:
            raise NOT_FOUND


container_attribute_crud = ContainerAttributeCRUD()
