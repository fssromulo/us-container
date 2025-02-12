# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.reports import Reports
from src.schemas.reports import ReportsIn, ReportsInUpdate, ReportsOut


class ReportsCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = ReportsOut
        self.create_schema = ReportsIn
        self.update_schema = ReportsInUpdate
        self.db_model = Reports
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema)

    async def get_by_name(self, account_id: int, name: str) -> List[Model]:
        queryset = self.db_model.filter(account_id=account_id, name=name)
        ordered_queryset = queryset.order_by('created_at')
        return await self.schema.from_queryset(ordered_queryset)

    async def get_by_hash(self, account_id: int, name: str, hash: str) -> List[Model]:
        queryset = self.db_model.filter(account_id=account_id, name=name, query_hash=hash, status='COMPLETED')
        ordered_queryset = queryset.order_by('created_at')
        return await self.schema.from_queryset(ordered_queryset)

    async def delete_by_hash(self, hash: str):
        await self.db_model.filter(query_hash=hash, status__in=["COMPLETED", "RUNNING"]).delete()

    async def delete_by_name(self, name: str, account_id: str):
        await self.db_model.filter(name=name, account_id=int(account_id)).delete()


reports_crud = ReportsCrud()
