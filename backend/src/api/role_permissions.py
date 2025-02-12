# Python imports

# Python imports
from typing import Dict, List, Union

# Pip imports
from fastapi import APIRouter, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import role_permissions
from src.dependencies import auth
from src.schemas.role_permissions import DuplicateRole, UpdateRole
from src.schemas.token import Status


router = APIRouter(tags=["roles"], dependencies=[Depends(auth.implicit_scheme)])


@router.get("/full_roles")
@cache(namespace="roles_internal", expire=60 * 10)
async def get_roles_with_permissions(auth_user: Auth0User = Depends(auth.get_user)) -> Dict[str, str]:
    roles = await role_permissions.get_roles(auth_user)
    for role in roles:
        if role['name'] not in ['admin', 'superadmin']:
            permissions = await role_permissions.get_permissions_for_role(role['id'], auth_user)
            if len(permissions):
                role['permissions'] = [x['permission_name'] for x in permissions]
    return roles


@router.get("/roles")
@cache(namespace="roles_internal", expire=60 * 60)
async def get_roles(auth_user: Auth0User = Depends(auth.get_user)) -> Dict[str, str]:
    return await role_permissions.get_roles(auth_user)


@router.post("/user_role/{user_id}/{role_id}", response_model=Status)
async def assign_user_to_role(user_id: str, role_id: str, auth_user: Auth0User = Depends(auth.get_user)) -> Status:
    await FastAPICache.clear(namespace="roles")
    return await role_permissions.assign_user_to_role(user_id, role_id, auth_user)


@router.post("/role", response_model=Status)
async def create_role(role: UpdateRole, auth_user: Auth0User = Depends(auth.get_user)) -> Status:
    await FastAPICache.clear(namespace="roles")
    return await role_permissions.create_role(role, auth_user)


@router.get("/role/{user_id}")
async def get_role_for_user(user_id: str, auth_user: Auth0User = Depends(auth.get_user)) -> Dict[str, str]:
    return await role_permissions.get_role_for_user(user_id, auth_user)


@router.get("/role_permissions/{role_id}")
async def get_permissions_for_role(role_id: str, auth_user: Auth0User = Depends(auth.get_user)) -> List[Dict[str, str]]:
    return await role_permissions.get_permissions_for_role(role_id, auth_user)


@router.get("/permissions")
async def get_permissions(auth_user: Auth0User = Depends(auth.get_user)) -> List[Dict[str, str]]:
    return await role_permissions.get_permissions(auth_user)


@router.post("/assign_permission_to_role/{role_id}")
async def assign_permission_to_role(
    permissions: List[dict], role_id: str, auth_user: Auth0User = Depends(auth.get_user)
) -> Dict[str, str]:
    return await role_permissions.assign_permission_to_role(permissions, role_id, auth_user)


@router.delete("/delete_permission_from_role/{role_id}")
async def delete_permission_from_role(
    permissions: List[dict], role_id: str, auth_user: Auth0User = Depends(auth.get_user)
) -> Status:
    return await role_permissions.delete_permission_from_role(permissions, role_id, auth_user)


@router.post("/duplicate-role", response_model=Status)
async def duplicate_role_with_permissions(role: DuplicateRole, auth_user: Auth0User = Depends(auth.get_user)) -> Status:
    return await role_permissions.duplicate_role_with_permissions(role, auth_user)
