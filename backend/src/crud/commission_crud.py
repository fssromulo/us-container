# Python imports
from datetime import datetime
from typing import List

# Pip imports
from fastapi import HTTPException
from loguru import logger
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.comission import Commission
from src.schemas.commission import CommissionIn, CommissionInUpdate, CommissionOut


NOT_FOUND = HTTPException(404, "Item not found")


class CommissionCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = CommissionOut
        self.create_schema = CommissionIn
        self.update_schema = CommissionInUpdate
        self.db_model = Commission
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    async def get_commission_by_order_paid_date(self, order_paid_date: str, user_id: str) -> Model:
        # check type of start date and end date
        if isinstance(order_paid_date, str):
            order_paid_date = datetime.strptime(order_paid_date, "%m/%d/%y")

        model = (
            await self.db_model.filter(user_id=user_id)
            .filter(commission_effective_date__lte=order_paid_date)
            .order_by("-created_at")
            .first()
        )
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            return None

    async def get_by_user_id(self, user_id: str) -> Model:
        return await self.db_model.filter(user_id=user_id).first()

    async def get_user_by_user_ids(self, user_ids: list = []):
        return await self.db_model.filter(user_id__in=user_ids)
        # return await self.schema.from_queryset(query)

    async def get_all(self, account_id) -> List[Model]:
        logger.info("Fetching commission rates")
        logger.info(account_id)
        query = self.db_model.all().order_by("-created_at")
        return await self.schema.from_queryset(query)


commission_crud = CommissionCRUD()
