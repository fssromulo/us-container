# ...
# Python imports
from datetime import date, datetime
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.transaction_type import TransactionType
from src.schemas.transaction_type import TransactionTypeIn, TransactionTypeInUpdate, TransactionTypeOut


class TransactionTypeCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = TransactionTypeOut
        self.create_schema = TransactionTypeIn
        self.update_schema = TransactionTypeInUpdate
        self.db_model = TransactionType
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema)

    async def get_all_between_dates(self, account_id: int, date_start: date, date_end: date) -> List[Model]:
        if self.has_account_id():
            query = self.db_model.filter(
                account_id=account_id,
                created_at__range=(
                    datetime.combine(date_start, datetime.min.time()),
                    datetime.combine(date_end, datetime.max.time()),
                ),
            ).order_by("-created_at")
        else:
            query = self.db_model.filter(
                created_at__range=(
                    datetime.combine(date_start, datetime.min.time()),
                    datetime.combine(date_end, datetime.max.time()),
                )
            ).order_by("-created_at")
        return await self.schema.from_queryset(query)

    async def get_by_id(self, type_id: str):
        """Retrieve a transaction type by its ID."""
        return await self.db_model.filter(id=type_id).first()

    async def get_transaction_types_by_group_id(self, group_id):
        """Retrieve all transaction types associated with a specific group ID."""
        query = self.db_model.filter(group_id=group_id).order_by("-created_at")
        return await self.schema.from_queryset(query)

    async def delete_without_account(self, item_id):
        return await self.db_model.filter(id=item_id).delete()


transaction_type_crud = TransactionTypeCrud()
