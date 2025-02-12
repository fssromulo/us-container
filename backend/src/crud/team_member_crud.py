from typing import Any, Callable, List, Type, cast, Coroutine, Optional, Union

from src.crud._utils import NOT_FOUND
from ._types import DEPENDENCIES, PYDANTIC_SCHEMA as SCHEMA, PAGINATION
from fastapi.params import Depends
from tortoise.models import Model

from src.schemas.users import TeamMemberIn, TeamMemberOut

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.team_member import TeamMember


class TeamMemberCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = TeamMemberOut
        self.create_schema = TeamMemberIn
        self.update_schema = TeamMemberIn
        self.db_model = TeamMember
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    async def get_by_team_lead_id(
        self,
        team_lead_id: str,
    ) -> Model:
        query = self.db_model.filter(team_lead_id=team_lead_id)
        return await self.schema.from_queryset(query)

    async def get_by_team_member_id(
        self,
        team_member_id: str,
    ) -> Model:
        model = await self.db_model.filter(team_member_id=team_member_id).first()
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND
    
    async def delete_one(self, account_id: int, item_id: int) -> Model:
        model: Model = await self.get_one(account_id, item_id)
        if model:
            await self.db_model.filter(
                id=item_id
            ).delete()
        else:
            raise NOT_FOUND
        return model


team_member_crud = TeamMemberCrud()
