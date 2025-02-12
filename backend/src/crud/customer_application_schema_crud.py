# Python imports
from datetime import datetime, timedelta
from typing import Any, Dict, List, cast

# Pip imports
from tortoise.models import Model
from tortoise.expressions import Q

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.customer_application_schema import CustomerApplicationSchema

from src.schemas.customer_application import CustomerApplicationSchemaIn, CustomerApplicationSchemaOut

from ._types import PAGINATION


class CustomerApplicationSchemaCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = CustomerApplicationSchemaOut
        self.create_schema = CustomerApplicationSchemaIn
        self.update_schema = CustomerApplicationSchemaIn
        self.db_model = CustomerApplicationSchema
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=200,
        )

    async def get_by_name(self, account_id:int, name:str) -> Model:
        try:
            query = self.db_model.filter(account_id=account_id).filter(name=name)
            results = await self.schema.from_queryset(query)
            return results
        except:
            raise

customerApplicationSchemaCRUD = CustomerApplicationSchemaCRUD()