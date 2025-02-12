# Python imports
import logging
from typing import List

# Pip imports
from tortoise.expressions import Q
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.notification import Notification
from src.schemas.notification import NotificationIn, NotificationOut


class NotificationCRUD(TortoiseCRUD):
    def __init__(self) -> None:
        self.db_model = Notification
        self.schema = NotificationOut
        self.create_schema = NotificationIn
        self.update_schema = NotificationIn
        self.out_schema = NotificationOut
        super().__init__(self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=5)

    async def find_notification_by_name(self, name: str) -> Model:
        model = await self.db_model.filter(name=name).first()
        result = await self.schema.from_tortoise_orm(model)
        return result


notification_crud = NotificationCRUD()
