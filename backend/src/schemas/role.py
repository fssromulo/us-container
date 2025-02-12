
# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.role import Role


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True

RoleIn = pydantic_model_creator(
    Role,
    name="RoleIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    optional=("account_id"),
    config_class=Config,
)

RoleOut = pydantic_model_creator(
    Role,
    name="RoleOut",
    exclude_readonly=True
)
