# Python imports
import csv
import os
from typing import Any, Iterable, List, Optional, Type, cast

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND

from ._types import PAGINATION
from ._types import PYDANTIC_SCHEMA as SCHEMA
from ._utils import pagination_factory


class TortoiseCRUD:
    def __init__(
        self,
        schema: Type[SCHEMA],
        db_model: Type[Model],
        create_schema: Optional[Type[SCHEMA]] = None,
        update_schema: Optional[Type[SCHEMA]] = None,
        max_limit: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        self.db_model = db_model
        self.schema = schema
        self.create_schema = create_schema or schema
        self.update_schema = update_schema or schema
        self.pagination_depends = pagination_factory(max_limit=max_limit, return_type="depends")
        self.max_limit = max_limit or 100
        # self.is_account_model = True if self.db_model.__name__ == "Account" else False
        self._pk: str = db_model.describe()["pk_field"]["db_column"]

    def has_account_id(self):
        return "account_id" in [field['name'] for field in self.db_model.describe()["data_fields"]]

    async def get_by_ids(self, account_id: int, ids: List[str]) -> List[Model]:
        query = self.db_model.filter(account_id=account_id).filter(id__in=ids)
        return await self.schema.from_queryset(query)

    async def get_by_display_order_ids(self, account_id: int, ids: List[str]) -> List[Model]:
        query = self.db_model.filter(account_id=account_id).filter(display_order_id__in=ids)
        return await self.schema.from_queryset(query)

    async def get_all(self, account_id: int, pagination: PAGINATION = {}) -> List[Model]:
        skip, limit = pagination.get("skip", 0), pagination.get("limit", 0)
        if self.has_account_id():
            query = self.db_model.filter(account_id=account_id).offset(cast(int, skip)).order_by("-created_at")
        else:
            query = self.db_model.all().offset(cast(int, skip)).order_by("-created_at")
        if limit:
            query = query.limit(min(limit, self.max_limit))
        return await self.schema.from_queryset(query)

    async def get_one_without_account(self, item_id: str) -> Model:
        model = await self.db_model.get(id=item_id)
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_one(self, account_id: int, item_id: str) -> Model:
        if self.has_account_id():
            model = await self.db_model.filter(account_id=account_id).filter(id=item_id).first()
        else:
            model = await self.db_model.get(id=item_id)
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def create(self, model: Model) -> Model:
        if isinstance(model, self.create_schema):
            model = model.dict()
            db_model = self.db_model(**model)
            await db_model.save()
            return await self.schema.from_tortoise_orm(db_model)

    async def bulk_create(self, models: List[Model], batch_size: int = None) -> List[Model]:
        return await self.db_model.bulk_create([self.db_model(**m.dict()) for m in models], batch_size)

    async def bulk_update(self, models: List[Model], fields: List[str], batch_size: int = None) -> List[Model]:
        return await self.db_model.bulk_update(models, fields, batch_size)

    async def update(self, account_id: int, item_id: int, model: Model) -> Model:  # type: ignore
        if isinstance(model, self.update_schema):
            model = model.dict(exclude_unset=True)
            if self.has_account_id():
                query = self.db_model.filter(account_id=account_id).filter(id=item_id)
            else:
                query = self.db_model.filter(id=item_id)
            await query.update(**model)
            return await self.schema.from_queryset_single(self.db_model.get(id=item_id))

    async def get_by_email(self, account_id: int, email: str) -> Model:
        if self.schema.schema().get("properties").get("email"):
            model = await self.db_model.filter(account_id=account_id).filter(email=email).first()
        if self.schema.schema().get("properties").get("primary_email"):
            model = await self.db_model.filter(account_id=account_id).filter(primary_email=email).first()
        if model:
            results = await self.schema.from_tortoise_orm(model)
            return results
        else:
            raise NOT_FOUND

    async def delete_all(
        self,
        account_id: int,
    ) -> List[Model]:
        await self.db_model.filter(account_id=account_id).delete()
        return await self.get_all(account_id)

    async def delete_all_ids(
        self,
        account_id: int,
        ids: list
    ) -> List[Model]:
        await self.db_model.filter(account_id=account_id).filter(id__in=ids).delete()
        return await self.get_all(account_id)

    async def delete_all_ids_without_account(
        self,
        account_id: int,
        ids: list
    ) -> List[Model]:
        await self.db_model.filter(id__in=ids).delete()

    async def delete_all_dangerous(
        self,
    ) -> List[Model]:
        await self.db_model.all().delete()

    async def delete_one(self, account_id: int, item_id: str) -> Model:
        model: Model = await self.get_one(account_id, item_id)
        await self.db_model.filter(id=item_id).delete()

        return model

    async def convert_to_csv(self, models: Iterable[Model], new_csv_file_name: str):
        """
        param: new_csv_file_name: This is a string, but do not include the .csv. That will
        be included in the rest of the method
        """
        fieldnames = list(self.schema.schema()["properties"].keys())

        with open(os.path.join(os.getcwd(), f"/backend/src/{new_csv_file_name}.csv"), "w") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for model in models:
                writer.writerow(self.schema.from_orm(model).dict())
