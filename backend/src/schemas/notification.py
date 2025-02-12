# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

# Internal imports
from src.database.models.notification import Notification



class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True



NotificationIn = pydantic_model_creator(
    Notification,
    name="NotificationIn",
    exclude=(
        "id",
        "created_at",
        "modified_at",
        "account",
    ),
    exclude_readonly=True,
    config_class=Config,
)

NotificationOut = pydantic_model_creator(
    cls=Notification,
    name="NotificationOut",
    exclude=(
        "account",
    )
)

