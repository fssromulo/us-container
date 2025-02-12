# Python imports
from typing import Dict, List, Union

# Pip imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.crud.auth0_management import Auth0Management
from src.crud.user_crud import user_crud
from src.dependencies import auth
from src.schemas.role_permissions import DuplicateRole, UpdateRole
from src.schemas.token import Status

auth_0_management = Auth0Management()


async def get_roles(auth_user: Auth0User) -> Dict[str, str]:
    try:
        return await auth_0_management.get_all_roles(auth_user.app_metadata.get("account_id"))
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role does not exist")

async def assign_user_to_role(user_id: str, role_id: str, auth_user: Auth0User) -> Status:
    user = await user_crud.get_one(auth_user.app_metadata.get("account_id"), user_id)
    await auth_0_management.assign_user_to_role(user, role_id)
    return Status(message="User assigned to role")

async def create_role(role: UpdateRole, auth_user: Auth0User) -> Status:
    await auth_0_management.create_role(role, auth_user.app_metadata.get("account_id"))
    return Status(message="Role created")

async def get_role_for_user(user_id: str, auth_user: Auth0User) -> Dict[str, str]:
    user = await user_crud.get_one(auth_user.app_metadata.get("account_id"), user_id)
    return await auth_0_management.get_user_role(user)

async def get_permissions_for_role(role_id: str, auth_user: Auth0User) -> List[Dict[str, str]]:
    return await auth_0_management.get_roles_permissions(role_id, auth_user.app_metadata.get("account_id"))

async def get_permissions(auth_user: Auth0User) -> Union[List[str], str]:
    result = await auth_0_management.get_resource_server_by_id(auth_user.app_metadata.get("account_id"))
    return result.get('scopes')

async def assign_permission_to_role(
    permissions: List[dict], role_id: str, auth_user: Auth0User = Depends(auth.get_user)
) -> Dict[str, str]:
    await FastAPICache.clear(namespace="role_permissions")
    return await auth_0_management.add_permission_to_role(
        role_id, permissions, auth_user.app_metadata.get("account_id")
    )

async def delete_permission_from_role(
    permissions: List[dict], role_id: str, auth_user: Auth0User = Depends(auth.get_user)
) -> Status:
    await auth_0_management.delete_permissions_from_role(role_id, permissions, auth_user.app_metadata.get("account_id"))
    await FastAPICache.clear(namespace="role_permissions")
    return Status(message="Permission deleted from role")

async def duplicate_role_with_permissions(role: DuplicateRole, auth_user: Auth0User = Depends(auth.get_user)) -> Status:
    await auth_0_management.duplicate_role_with_permissions(
        role.role_id, role.role_name, auth_user.app_metadata.get("account_id")
    )
    await FastAPICache.clear(namespace="role_permissions")

    return Status(message="Role and permissions duplicated")
