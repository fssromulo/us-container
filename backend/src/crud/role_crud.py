
# ...
from typing import List

from src.schemas.role import (
    RoleIn,
    RoleOut,
)

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.role import Role

class RoleCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = RoleOut
        self.create_schema = RoleIn
        self.update_schema = RoleIn
        self.db_model = Role
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
        )

    async def fetch_by_role_id(self, role_id: str) :
        return await self.db_model.filter(role_id=role_id).first()

    async def get_by_id(self, account_id: int):
        query = self.db_model.filter(account_id=account_id)
        return await self.schema.from_queryset(query)


role_crud = RoleCrud()
