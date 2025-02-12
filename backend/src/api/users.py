# Python imports
import os
from typing import List

# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import users
from src.controllers.users import CreateUpdateUserCommission
from src.crud.role_crud import role_crud
from src.database.models.user import User
from src.dependencies import auth
from src.schemas.token import Status
from src.schemas.users import (
    AssistantOut,
    CreateAssistant,
    CreateTeamMember,
    CreateUpdateUser,
    TeamMemberOut,
    UserOutSchema,
)


STAGE = os.environ.get("STAGE", "dev")

router = APIRouter(tags=["users"], dependencies=[Depends(auth.implicit_scheme)])


@router.post("/team_member")
async def create_team_membre(user: CreateTeamMember):
    return await users.create_team_membre(user)


@router.post("/assistant")
async def get_team(user: CreateAssistant):
    return await users.get_team(user)


@router.get("/team/{team_lead_id}", response_model=List[TeamMemberOut])
async def get_team_by_team_lead_id(team_lead_id: str):  # noqa
    return await users.get_team_by_team_lead_id(team_lead_id)


@router.get("/assistants/{manager_id}", response_model=List[AssistantOut])
async def get_assistants(manager_id: str):
    return await users.get_assistants(manager_id)


@router.get("/team_member/{team_member_id}", response_model=TeamMemberOut)
async def get_team_member(team_member_id: str):
    return await users.get_team_member(team_member_id)


@router.get("/team_member_lead/{team_member_id}")
async def get_team_member_lead(team_member_id: str, user: Auth0User = Depends(auth.get_user)):
    teamMember = await users.get_team_member(team_member_id)
    if teamMember:
        return await users.get_user(teamMember.team_lead.id, user)
    else:
        return None


@router.delete("/team_member/{team_member_id}")
async def delete_team_member(team_member_id: str, user: Auth0User = Depends(auth.get_user)):
    return await users.delete_team_member(team_member_id, user)


@router.delete("/assistant/{assistant_id}")
async def delete_assistant(assistant_id: str, user: Auth0User = Depends(auth.get_user)):
    return await users.delete_assistant(assistant_id, user)


@router.get("/assistant/{assistant_id}", response_model=AssistantOut)
async def get_assistant(assistant_id: str):
    return await users.get_assistant(assistant_id)


@router.get("/users")
@cache(namespace="users", expire=60 * 20)
async def get_users(user: Auth0User = Depends(auth.get_user)):
    return await users.get_users(user)


@router.get("/user/password_reset/{user_id}")
async def send_password_reset_email(user_id, auth_user: Auth0User = Depends(auth.get_user)):
    return await users.send_password_reset_email(user_id, auth_user)


@router.get("/user/{user_id}", response_model=dict)
@cache(namespace="user", expire=60 * 20)
async def get_user(user_id: str, user: Auth0User = Depends(auth.get_user)) -> dict:
    return await users.get_user(user_id, user)


@router.get("/get_roles")
@cache(namespace="user", expire=60 * 20)
async def get_roles(user: Auth0User = Depends(auth.get_user)):
    return await role_crud.get_all(user.app_metadata['account_id'])


@router.post("/user", response_model=UserOutSchema)
async def create_user(
    userCommission: CreateUpdateUserCommission,
    background_tasks: BackgroundTasks,
    auth_user: Auth0User = Depends(auth.get_user),
) -> UserOutSchema:
    await FastAPICache.clear(namespace="users")
    await FastAPICache.clear(namespace="user")
    return await users.create_user(userCommission, auth_user, background_tasks=background_tasks)


@router.patch(
    "/user/{user_id}", response_model=UserOutSchema, responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}}
)
async def update_user(
    user_id: str,
    userCommission: CreateUpdateUserCommission,
    background_tasks: BackgroundTasks,
    auth_user: Auth0User = Depends(auth.get_user),
) -> UserOutSchema:
    await FastAPICache.clear(namespace="users")
    await FastAPICache.clear(namespace="user")
    return await users.update_user(user_id, userCommission, auth_user, background_tasks=background_tasks)


@router.patch("/user/preference/{user_id}", responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}})
async def update_user_preference(
    user_id: str, userData: CreateUpdateUser, auth_user: Auth0User = Depends(auth.get_user)
) -> UserOutSchema:
    await FastAPICache.clear(namespace="users")
    await FastAPICache.clear(namespace="user")
    user: User = await users.get_user(user_id, auth_user)
    userPreferences = user['preferences'] if user['preferences'] else {}
    return await users.update_user_preference(user_id, userData, auth_user, userPreferences)


@router.patch("/user/switch/{user_id}/{target_account}", responses={404: {"model": HTTPNotFoundError}})
async def switch_account(
    user_id: str,
    target_account: int,
    user: Auth0User = Depends(auth.get_user),
):
    await FastAPICache.clear(namespace="account")
    return await users.switch_account(user_id, user, target_account)


@router.delete(
    "/user/{user_id}", response_model=Status, responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}}
)
async def delete_user(user_id: str, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)):
    return await users.delete_user(user_id, user, background_tasks=background_tasks)
