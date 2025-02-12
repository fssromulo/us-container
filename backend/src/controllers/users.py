# Python imports
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

# Pip imports
from fastapi import HTTPException, status
from fastapi_cache import FastAPICache
from loguru import logger
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.controllers.event_controller import send_event
from src.crud.account_crud import account_crud
from src.crud.assistant_crud import assistant_crud
from src.crud.auth0_management import Auth0Management
from src.crud.commission_crud import commission_crud
from src.crud.order_commission_crud import order_commission_crud
from src.crud.team_member_crud import team_member_crud
from src.crud.user_crud import UserCRUD
from src.database.models.user import User
from src.schemas.commission import CommissionIn, CreateUpdateCommission
from src.schemas.token import Status
from src.schemas.users import (
    AssistantIn,
    CreateAssistant,
    CreateTeamMember,
    CreateUpdateUser,
    TeamMemberIn,
    UserInSchema,
    UserInUpdateSchema,
    UserOutSchema,
)
from src.services.notifications import email_service, email_service_mailersend
from src.services.tenant_switcher import migrate_user
from src.utils.users import ROLES_DICT
from src.utils.utility import make_json_serializable


class CreateUpdateUserCommission(BaseModel):
    user: Optional[CreateUpdateUser]
    commission: Optional[CreateUpdateCommission]


STAGE = os.environ.get("STAGE", "dev")

user_crud = UserCRUD()

auth_0_management = Auth0Management()


async def save_user(user: CreateUpdateUser, auth_user, user_id=None, background_tasks=None):
    user_dict = user.dict(exclude_unset=True)
    user_dict["account_id"] = auth_user.app_metadata.get("account_id")

    if user_id:
        if not user_dict.get("email"):
            existing_user = await user_crud.get_one(auth_user.app_metadata.get("account_id"), user_id)
            user_dict["email"] = existing_user.email

        # send event to event controller
        if background_tasks:
            background_tasks.add_task(
                send_event,
                auth_user.app_metadata['account_id'],
                str(user_id),
                make_json_serializable(user_dict),
                "user",
                "update",
            )

        return await user_crud.update(
            auth_user.app_metadata.get("account_id"), user_id, UserInUpdateSchema(**user_dict)
        )

    # Remove after migration
    # user_dict["id"] = str(uuid.uuid4())
    new_user = await user_crud.create(UserInSchema(**user_dict))
    # send event to event controller
    if background_tasks:
        background_tasks.add_task(
            send_event,
            auth_user.app_metadata['account_id'],
            str(new_user.id),
            make_json_serializable(new_user.dict()),
            "user",
            "create",
        )

    return new_user


async def save_commission(
    commission_effective_date: datetime,
    user_id: str,
    flat_commission: Decimal = 0.0,
    commission_percentage: Decimal = 0.0,
    rental_total_flat_commission_rate: Decimal = 0.0,
    rental_effective_rate: Decimal = 0.0,
):
    new_commission: dict = {
        "commission_effective_date": commission_effective_date,
        "flat_commission": flat_commission,
        "commission_percentage": commission_percentage,
        "rental_effective_rate": rental_effective_rate,
        "rental_total_flat_commission_rate": rental_total_flat_commission_rate,
        "user_id": user_id,
    }

    try:
        await commission_crud.create(CommissionIn(**new_commission))
    except Exception as e:
        raise e


async def save_assisstant_or_team(user, isTeamMember=True):
    user_dict = user.dict(exclude_unset=True)
    if isTeamMember:
        return await team_member_crud.create(TeamMemberIn(**user_dict))

    return await assistant_crud.create(AssistantIn(**user_dict))


async def create_team_membre(user: CreateTeamMember):
    return await save_assisstant_or_team(user, True)


async def get_team(user: CreateAssistant):
    return await save_assisstant_or_team(user, False)


async def get_team_by_team_lead_id(team_lead_id: str):  # noqa
    return await team_member_crud.get_by_team_lead_id(team_lead_id)


async def get_assistants(manager_id: str):
    return await assistant_crud.get_by_manager_id(manager_id)


async def get_team_member(team_member_id: str):
    return await team_member_crud.get_by_team_member_id(team_member_id)


async def delete_team_member(team_member_id: str, user: Auth0User):
    await team_member_crud.delete_one(user.app_metadata.get("account_id"), team_member_id)


async def delete_assistant(assistant_id: str, user: Auth0User):
    await assistant_crud.delete_one(user.app_metadata.get("account_id"), assistant_id)


async def get_assistant(assistant_id: str):
    return await assistant_crud.get_by_assistant_id(assistant_id)


async def get_users(user: Auth0User):
    return await user_crud.get_all(user.app_metadata.get("account_id"))


async def send_password_reset_email(user_id, auth_user: Auth0User):
    user = await user_crud.get_one(auth_user.app_metadata.get("account_id"), user_id)
    account = await account_crud.get_one(user.account_id)

    ticket = await auth_0_management.send_password_change_tickets(user, account)
    return Status(message=str(ticket))


async def get_user(user_id: str, user: Auth0User) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user does not exist")

        existing_user = await user_crud.get_one(user.app_metadata.get("account_id"), user_id)
        permissions = await auth_0_management.get_roles_permissions(existing_user.role_id, existing_user.account_id)
        permissions = {"permissions": [p["permission_name"] for p in permissions]}
        return {**existing_user.dict(), **permissions}
        # return existing_user
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user does not exist")


async def create_user(
    userCommission: CreateUpdateUserCommission, auth_user: Auth0User, background_tasks=None
) -> UserOutSchema:
    if userCommission.user.role_id and userCommission.user.role_id == ROLES_DICT.get(STAGE, {}).get("superadmin", ""):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User cannot be assigned to this role")

    try:
        userCommission.user.birthday = (
            datetime.strptime(str(userCommission.user.birthday), "%Y-%m-%dT%H:%M:%S.%fZ")
            if userCommission.user.birthday
            else None
        )
    except:
        pass
    saved_user: User = await save_user(userCommission.user, auth_user, background_tasks=background_tasks)
    # saved_user = await get_user("aff18fce-ee11-11ea-84aa-ee00dfd3400d", auth_user)

    # if the createupdateuser has the flat_commission or the commission_percentage, then we will create those records in the commission table
    if (
        userCommission.commission.flat_commission is not None
        or userCommission.commission.commission_percentage is not None
        or userCommission.commission.rental_total_flat_commission_rate is not None
        or userCommission.commission.rental_effective_rate is not None
    ) and userCommission.commission.commission_effective_date is not None:
        await FastAPICache.clear(
            namespace="commissions"
        )  # we need to clear this commissions cache if we update the commissions at all, so that that change is reflected elsewhere
        await save_commission(
            userCommission.commission.commission_effective_date,
            saved_user.id,
            userCommission.commission.flat_commission,
            userCommission.commission.commission_percentage,
            userCommission.commission.rental_total_flat_commission_rate,
            userCommission.commission.rental_effective_rate,
        )

    result = await auth_0_management.create_user(saved_user, saved_user.account_id)
    if not result:
        await user_crud.delete_one(saved_user.account_id, saved_user.id)
        return auth_user

    result = await auth_0_management.create_password_change_ticket(saved_user.id, saved_user.account_id)

    if userCommission.user.role_id:
        await auth_0_management.assign_user_to_role(saved_user, saved_user.role_id)

    account = await account_crud.get_one(saved_user.account_id)
    account_name = None
    if account.name == 'Amobilebox':
        account_name = 'A Mobile Box'
    else:
        account_name = account.name

    data = {
        "first_name": saved_user.first_name,
        "company_name": account_name,
        "url": result.get("ticket"),
        "email": saved_user.email,
    }
    if account.name.startswith("USA Containers"):
        email_service.send_change_password_email(data)
    else:
        email_service_mailersend.send_change_password_email(data, account)
    return saved_user


async def update_user(
    user_id: str, userCommission: CreateUpdateUserCommission, auth_user: Auth0User, background_tasks=None
) -> UserOutSchema:
    try:
        if userCommission.user.role_id and userCommission.user.role_id == ROLES_DICT.get(STAGE, {}).get(
            "superadmin", ""
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User cannot be assigned to this role")

        can_update_user_role = len([p for p in auth_user.permissions if p == "update:user_role"])
        existing_user: User = await user_crud.get_one(auth_user.app_metadata.get("account_id"), user_id)

        if (
            not can_update_user_role
            and userCommission.user.role_id
            and existing_user.role_id != userCommission.user.role_id
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User is unauthorized to perform this action"
            )
        saved_user = existing_user
        if (
            userCommission.user
            and userCommission.user.role_id
            and ROLES_DICT.get(STAGE, {}).get(userCommission.user.role_id) == 'sales_manager'
            and ROLES_DICT.get(STAGE, {}).get(existing_user.role_id) == 'sales_agent'
        ):
            logger.info("UPGRADING AGENT TO MANAGER")
            await order_commission_crud.upgrading_agent_to_manager(user_id)

        if (userCommission.commission is not None) and (
            (userCommission.commission.flat_commission is not None and userCommission.commission.flat_commission != 0)
            or (
                userCommission.commission.commission_percentage is not None
                and userCommission.commission.commission_percentage != 0
            )
            or (
                userCommission.commission.rental_total_flat_commission_rate is not None
                and userCommission.commission.rental_total_flat_commission_rate != 0
            )
            or (
                userCommission.commission.rental_effective_rate is not None
                and userCommission.commission.rental_effective_rate != 0
            )
        ):
            await FastAPICache.clear(
                namespace="commissions"
            )  # we need to clear this commissions cache if we update the commissions at all, so that that change is reflected elsewhere
            await save_commission(
                userCommission.commission.commission_effective_date,
                saved_user.id,
                userCommission.commission.flat_commission,
                userCommission.commission.commission_percentage,
                userCommission.commission.rental_total_flat_commission_rate,
                userCommission.commission.rental_effective_rate,
            )
        saved_user = await save_user(userCommission.user, auth_user, user_id, background_tasks=background_tasks)
        if userCommission.user and userCommission.user.role_id:
            current_role = await auth_0_management.get_user_role(saved_user)
            if current_role:
                removed = await auth_0_management.remove_role_from_user(saved_user, [current_role["id"]])
                if not removed:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not update user role")
            auth_user = await auth_0_management.assign_user_to_role(saved_user, saved_user.role_id)
        new_user = {**saved_user.dict(), **userCommission.user.dict(exclude_unset=True)}
        new_user["is_active"] = str(new_user["is_active"]).lower() == "true"
        await auth_0_management.update_user(saved_user, new_user)
        return saved_user
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")


async def update_user_preference(
    user_id: str, userData: CreateUpdateUser, auth_user: Auth0User, preferences: Dict
) -> UserOutSchema:
    try:
        # can_update_user_role = len([p for p in auth_user.permissions if p == "update:user_role"])
        # if not can_update_user_role:
        #    raise HTTPException(
        #        status_code=status.HTTP_401_UNAUTHORIZED, detail="User is unauthorized to perform this action"
        #    )
        return await user_crud.update_user_preference(user_id, userData, preferences)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")


async def delete_user(user_id: str, user: Auth0User):
    await user_crud.delete_one(user.app_metadata.get("account_id"), user_id)
    # send event to event controller
    await send_event(user.app_metadata['account_id'], str(user_id), {}, "user", "delete")

    return Status(message="User deleted")


async def switch_account(user_id: str, user: Auth0User, target_account: int):
    user_account = await user_crud.get_one(user.app_metadata.get("account_id"), user_id)
    await migrate_user(
        from_account_id=user.app_metadata.get("account_id"), to_account_id=target_account, user_email=user_account.email
    )
    return Status(message="User account switched")
