# ...
# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.auth.auth import Auth0User
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.fee_type import FeeType
from src.schemas.fee_type import FeeTypeIn, FeeTypeOut, FeeTypeUpdate


class FeeTypeCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = FeeTypeOut
        self.create_schema = FeeTypeIn
        self.update_schema = FeeTypeUpdate
        self.db_model = FeeType
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=200,
        )

    async def get_fee_types(self, user: Auth0User) -> List[Model]:
        return await self.db_model.filter(account_id=user.app_metadata["account_id"])

    async def update(self, id: str, fee_type: FeeTypeUpdate, user: Auth0User) -> Model:
        update_type = {key: value for key, value in fee_type.dict().items() if value is not None}
        return (
            await self.db_model.filter(account_id=user.app_metadata["account_id"]).filter(id=id).update(**update_type)
        )

    async def get_by_name(self, account_id: int, fee_type_name: str) -> Model:
        fee_type = await self.db_model.filter(account_id=account_id).filter(name=fee_type_name).first()
        return fee_type


fee_type_crud = FeeTypeCrud()
