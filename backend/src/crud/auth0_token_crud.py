from src.schemas.auth0_token import (
    Auth0ManagementTokenIn,
    Auth0ManagementTokenOut,
)

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.auth_management_token import AuthManagementToken

auth0_management_token_crud = TortoiseCRUD(
    schema=Auth0ManagementTokenOut,
    create_schema=Auth0ManagementTokenIn,
    update_schema=Auth0ManagementTokenIn,
    db_model=AuthManagementToken,
)
