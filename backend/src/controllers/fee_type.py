# python imports
# Python imports
from typing import List

# Internal imports
from src.auth.auth import Auth0User
from src.crud.fee_type_crud import fee_type_crud
from src.schemas.fee_type import FeeTypeIn, FeeTypeOut, FeeTypeUpdate


async def create_fee_type(fee_type: FeeTypeIn, user: Auth0User) -> FeeTypeOut:
    saved_fee_type = await fee_type_crud.create(fee_type)
    return saved_fee_type


async def fetch_fee_types(user: Auth0User) -> List[FeeTypeOut]:
    saved_fee_type = await fee_type_crud.get_fee_types(user)
    return saved_fee_type


async def fetch_fee_type_by_name(account_id: int, fee_type_name: str) -> FeeTypeOut:
    return await fee_type_crud.get_by_name(account_id, fee_type_name)


async def update_fee_type(id: str, fee_type: FeeTypeUpdate, user: Auth0User) -> FeeTypeOut:
    return await fee_type_crud.update(id, fee_type, user)
