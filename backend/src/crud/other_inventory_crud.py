# Python imports
from typing import List, cast

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.inventory.other_inventory import OtherInventory
from src.schemas.other_inventory import OtherInventoryIn, OtherInventoryOut, OtherInventoryUpdateIn

from ._types import PAGINATION


class OtherInventoryCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OtherInventoryOut
        self.create_schema = OtherInventoryIn
        self.update_schema = OtherInventoryIn
        self.db_model = OtherInventory
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_inventory_by_depot(self, account_id: int, depot_id: str) -> Model:

        query = (
            self.db_model.filter(account_id=account_id)
            .filter(depot_id=depot_id)
            .filter(status="Available")
            .order_by("-created_at")
        )

        return await self.schema.from_queryset(query)

    async def get_by_status_type(
        self, account_id: int, status: str, purchase_type: str, pagination: PAGINATION
    ) -> Model:
        skip, limit = pagination.get("skip"), pagination.get("limit")

        if purchase_type:
            query = (
                self.db_model.filter(account_id=account_id)
                .filter(purchase_type__in=[purchase_type])
                .order_by("-created_at")
                .offset(cast(int, skip))
            )
        else:
            query = self.db_model.filter(account_id=account_id).order_by("-created_at").offset(cast(int, skip))

        if status != "All":
            query = query.filter(status=status)

        if limit:
            query = query.limit(limit)

        return await self.schema.from_queryset(query)

    async def get_one_prefix(self, account_id: int, item_id: str) -> Model:
        if self.has_account_id():
            model = await self.db_model.filter(account_id=account_id).filter(id__startswith=item_id).first()
        else:
            model = await self.db_model.filter(id__startswith=item_id).first()
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def search_inventory(
        self,
        account_id: int,
        other_release: str = None,
        other_number: str = None,
        other_availability: str = None,
    ) -> Model:

        query = self.db_model.filter(account_id=account_id)

        if other_release:
            query = query.filter(other_release_number__icontains=other_release)

        if other_number:
            query = query.filter(other_number__icontains=other_number)

        if other_availability and other_availability != 'All':
            query = query.filter(status=other_availability)

        query = query.order_by("-created_at")
        return await self.schema.from_queryset(query)


other_inventory_crud = OtherInventoryCRUD()
