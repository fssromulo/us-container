# Python imports
from typing import Any, Iterable, List, Optional, Type, cast

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.pricing.container_product import ContainerProduct
from src.schemas.container_product import ContainerProductIn, ContainerProductOut

from ._types import PAGINATION


class ContainerProductCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = ContainerProductOut
        self.create_schema = ContainerProductIn
        self.update_schema = ContainerProductIn
        self.db_model = ContainerProduct
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_all(self, account_id: int, pagination: PAGINATION = {}) -> List[Model]:
        skip, limit = pagination.get("skip", 0), pagination.get("limit", 0)
        query = self.db_model.filter(location__account_id=account_id).offset(cast(int, skip)).order_by("-created_at")
        if limit:
            query = query.limit(min(limit, self.max_limit))
        return await self.schema.from_queryset(query)

    async def get_all_all_accounts(self, pagination: PAGINATION = {}) -> List[Model]:
        skip, limit = pagination.get("skip", 0), pagination.get("limit", 0)
        query = self.db_model.all().offset(cast(int, skip)).order_by("-created_at")
        if limit:
            query = query.limit(min(limit, self.max_limit))
        return await self.schema.from_queryset(query)

container_product_crud = ContainerProductCRUD()
