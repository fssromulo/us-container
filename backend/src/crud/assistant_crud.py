# Python imports
from typing import Any, Callable, Coroutine, List, Optional, Type, Union, cast

# Pip imports
from fastapi.params import Depends
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.assistant import Assistant
from src.schemas.users import AssistantIn, AssistantOut

from ._types import DEPENDENCIES, PAGINATION
from ._types import PYDANTIC_SCHEMA as SCHEMA


class AssistantCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = AssistantOut
        self.create_schema = AssistantIn
        self.update_schema = AssistantIn
        self.db_model = Assistant
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    async def get_by_manager_id(
        self,
        manager_id: str,
    ) -> Model:
        query = self.db_model.filter(manager_id=manager_id)
        return await self.schema.from_queryset(query)

    async def get_by_assistant_id(
        self,
        assistant_id: str,
    ) -> Model:
        model = await self.db_model.filter(assistant_id=assistant_id).first()
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def delete_one(self, account_id: int, item_id: int) -> Model:
        model: Model = await self.get_one(account_id, item_id)
        await self.db_model.filter(id=item_id).delete()

        return model


assistant_crud = AssistantCrud()
