# Python imports
from typing import List

# Pip imports
from loguru import logger
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.account import Account
from src.schemas.accounts import AccountInSchema, AccountOutSchema, UpdateAccount


class AccountCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = AccountOutSchema
        self.create_schema = AccountInSchema
        self.update_schema = AccountInSchema
        self.db_model = Account
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    async def get_one(self, account_id: int) -> Model:
        if self.has_account_id:
            model = await self.db_model.filter(id=account_id).first()
        else:
            model = await self.db_model.get(id=account_id)
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_all(self) -> List[Model]:
        query = self.db_model.all().order_by("-created_at")
        return await self.schema.from_queryset(query)

    async def update_attributes(self, account_id: int, updatedData: UpdateAccount) -> Model:  # type: ignore
        # retrieve the current data from db, patch it and update
        account = await self.db_model.filter(id=account_id).first()
        logger.info(account)
        if updatedData.type == 'integrations':
            integrations = account.integrations
            merged_integrations = {**integrations, **updatedData.integrations}
            await self.db_model.filter(id=account_id).update(integrations=merged_integrations)
        if updatedData.type == 'cms_attributes':
            cms_attributes = account.cms_attributes
            merged_attributes = {**cms_attributes, **updatedData.cms_attributes}
            await self.db_model.filter(id=account_id).update(cms_attributes=merged_attributes)
        return await self.db_model.filter(id=account_id).first()


account_crud = AccountCRUD()
