# Pip imports
from pydantic import BaseConfig, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.auth_management_token import AuthManagementToken


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


Auth0ManagementTokenIn = pydantic_model_creator(
    AuthManagementToken, name="Auth0ManagementTokenIn", exclude_readonly=True, config_class=Config
)
Auth0ManagementTokenOut = pydantic_model_creator(
    AuthManagementToken, name="Auth0ManagementTokenOut", exclude=["account"]
)
