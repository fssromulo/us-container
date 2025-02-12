# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

# Internal imports
from src.database.models.notification_history import NotificationHistory



class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True



NotificationHistoryIn = pydantic_model_creator(
    NotificationHistory,
    name="NotificationHistoryIn",
    exclude=(
        "id",
        "created_at",
        "modified_at",
        "account",
    ),
    exclude_readonly=True,
    config_class=Config,
)

NotificationHistoryOut = pydantic_model_creator(
    cls=NotificationHistory,
    name="NotificationHistoryOut",
    exclude=(
        "account",
    )
)

