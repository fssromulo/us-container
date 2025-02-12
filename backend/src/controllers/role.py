
# Python imports
#import logging
#import os
#import random
from typing import List

# Pip imports
#from fastapi import HTTPException, status
#from tortoise import Model
#from tortoise.exceptions import DoesNotExist

# Internal imports
from src.schemas.role import RoleOut, RoleIn
from src.crud.role_crud import role_crud
from src.auth.auth import Auth0User

async def create_role(role: RoleIn, auth_user: Auth0User) -> RoleOut:
    role.account_id = auth_user.app_metadata.get("account_id")
    try :
        existing_role: RoleOut = await role_crud.fetch_by_role_id(role.role_id)
        if existing_role is not None:
            saved_role = await role_crud.update(auth_user.app_metadata.get("account_id"), existing_role.id, role)
        else:
            saved_role = await role_crud.create(role)
    except:
        saved_role = await role_crud.create(role)
    return saved_role

async def fetch_account_roles(auth_user: Auth0User):
    return await role_crud.get_all(auth_user.app_metadata.get("account_id"))

