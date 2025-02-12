# Python imports
import logging
from datetime import datetime
from typing import List

# Pip imports
from tortoise.expressions import Q
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.notification_history import NotificationHistory
from src.schemas.notification_history import NotificationHistoryIn, NotificationHistoryOut


class NotificationHistoryCRUD(TortoiseCRUD):
    def __init__(self) -> None:
        self.db_model = NotificationHistory
        self.schema = NotificationHistoryOut
        self.create_schema = NotificationHistoryIn
        self.update_schema = NotificationHistoryIn
        self.out_schema = NotificationHistoryOut
        super().__init__(self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=5)

    async def find_notification_history(
        self, email: str, notification_name: str, account_id: int, completed_at: datetime
    ) -> Model:
        model = (
            await self.db_model.filter(account_id=account_id)
            .filter(notification__name=notification_name)
            .filter(notification__email=email)
            .all()
        )

        result = await self.schema.from_tortoise_orm(model)
        result = [x for x in result if x.create_at.date() == completed_at.date()]
        return result


notification_history_crud = NotificationHistoryCRUD()
