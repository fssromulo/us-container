# Python imports
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

# Pip imports
import httpx
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from loguru import logger
from requests import request

# Internal imports
from src.crud.account_crud import account_crud
from src.database.models.account import Account
from src.database.models.user import User
from src.schemas.accounts import AccountInSchema
from src.schemas.role_permissions import UpdateRole
from src.services.notifications import email_service, email_service_mailersend


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)
        return super(JsonEncoder, self).default(o)


async def get_auth0_admin_token(account: Account, account_id: str) -> str:
    # token_list = await auth0_management_token_crud.get_all(account_id=account.id)
    token_from_db = account.auth0_management_token

    if not token_from_db or account.auth0_management_token_modified_at.replace(tzinfo=None) + timedelta(
        days=5
    ) < datetime.now().replace(tzinfo=None):
        logger.info("Getting new token")
        auth_dict = account.cms_attributes.get('auth')
        payload = {
            "client_id": auth_dict.get("AUTH0_MNG_CLIENT_ID"),
            "client_secret": auth_dict.get("AUTH0_MNG_SECRET"),
            "audience": f"https://{auth_dict.get('AUTH0_DOMAIN')}/api/v2/",
            "grant_type": "client_credentials",
        }

        headers = {"content-type": "application/json"}
        url = f"https://{auth_dict.get('AUTH0_DOMAIN')}/oauth/token"
        response = request("POST", url, headers=headers, data=json.dumps(payload))

        token_update = {
            "auth0_management_token": response.json().get("access_token"),
            "auth0_management_token_modified_at": datetime.now(),
        }
        logger.info(token_update)
        auth_token = AccountInSchema(**token_update)
        updated_account = await account_crud.update(account_id, account_id, auth_token)
        return updated_account.auth0_management_token

    return token_from_db


async def get_headers_and_url(account_id: int, accept: str = None) -> Dict[str, str]:
    account = await account_crud.get_one(account_id)

    token = await get_auth0_admin_token(account, account_id)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    if accept:
        headers["Accept"] = accept

    return {
        "headers": headers,
        "url": f"https://{account.cms_attributes.get('auth', {}).get('AUTH0_DOMAIN')}/api/v2",
        "account": account,
    }


class Auth0Management:
    async def create_user(self, user: User, account_id: int) -> Dict[str, str]:
        headers_url = await get_headers_and_url(account_id)

        url = f"{headers_url.get('url')}/users"
        data = {
            "email": user.email,
            "nickname": "Johnny",
            "name": f"{user.first_name} {user.last_name}",
            "user_metadata": {},
            "blocked": False,
            "email_verified": True,
            "app_metadata": {
                "account_id": account_id,
                "id": user.id,
            },
            "given_name": user.first_name,
            "family_name": user.last_name,
            "user_id": user.id,
            "connection": "Username-Password-Authentication",
            "password": "DSkjlasda&^$!",
        }
        response = request("POST", url, headers=headers_url.get('headers'), data=json.dumps(data, cls=JsonEncoder))
        return {} if not response.ok else response.json()

    async def delete_user(self, user: User) -> Dict[str, str]:
        headers_url = await get_headers_and_url(user.account_id)
        url = f"{headers_url.get('url')}/users/auth0|{user.id}"
        response = request("DELETE", url, headers=headers_url.get('headers'))
        return {} if not response.ok else response.json()

    async def create_password_change_ticket(self, user_id: str, account_id: int) -> Dict[str, str]:
        headers_url = await get_headers_and_url(account_id=account_id)
        url = f"{headers_url.get('url')}/tickets/password-change"

        auth0_client_id = headers_url.get('account').cms_attributes.get('auth', {}).get('AUTH0_CLIENT_ID')
        data = {
            "client_id": auth0_client_id,
            "user_id": "auth0|" + str(user_id),
            "ttl_sec": 0,
            "mark_email_as_verified": True,
            "includeEmailInRedirect": False,
        }
        response = request("POST", url, headers=headers_url.get('headers'), data=json.dumps(data, cls=JsonEncoder))
        logger.info(response.json())
        return {} if not response.ok else response.json()

    async def send_password_change_tickets(self, user: User, account: Account) -> str:
        result = await self.create_password_change_ticket(user.id, user.account_id)
        data = {
            "first_name": user.first_name,
            "company_name": account.name,
            "url": result.get("ticket"),
            "email": user.email,
        }
        if account.name.startswith("USA Containers"):
            email_service.send_change_password_email(data)
        else:
            email_service_mailersend.send_change_password_email(data, account)

        return result.get("ticket", '')

    async def list_users(self, account_id) -> Dict[str, str]:
        headers_url = await get_headers_and_url(account_id)
        url = f"{headers_url.get('url')}/users"
        response = request("GET", url, headers=headers_url.get('headers'))
        return {} if not response.ok else response.json()

    async def update_user(self, existing_user: User, user: Dict[str, str]) -> Dict[str, str]:
        headers_url = await get_headers_and_url(existing_user.account_id)
        url = f"{headers_url.get('url')}/users/auth0|{existing_user.id}"
        body = {
            "email": user.get("email"),
            "user_metadata": {},
            "blocked": not user.get("is_active"),
            "app_metadata": {"account_id": existing_user.account_id, "id": str(existing_user.id)},
            "given_name": user.get("first_name"),
            "family_name": user.get("last_name"),
        }
        response = request("PATCH", url, headers=headers_url.get('headers'), data=json.dumps(body))

        return {} if not response.ok else response.json()

    @cache(namespace="user_role", expire=60 * 10)
    async def get_user_role(self, user: User) -> Dict[str, str]:
        headers_url = await get_headers_and_url(user.account_id)
        url = f"{headers_url.get('url')}/users/auth0|{user.id}/roles"
        response = request("GET", url, headers=headers_url.get('headers'))
        if not response.ok:
            return {}
        response = response.json()
        return response[0] if len(response) == 1 else {}

    @cache(namespace="roles", expire=60 * 10)
    async def get_all_roles(self, account_id: int) -> Dict[str, str]:
        headers_url = await get_headers_and_url(account_id)
        url = f"{headers_url.get('url')}/roles"
        response = request("GET", url, headers=headers_url.get('headers'))
        return {} if not response.ok else response.json()

    # @cache(namespace="permissions", expire=60 * 5)
    # async def get_roles_permissions(self, role_id: str, account_id: int) -> List[Dict[str, str]]:
    #     headers_url = await get_headers_and_url(account_id)
    #     base_url = f"{headers_url.get('url')}/roles/{role_id}/permissions?per_page=100"

    #     result = []
    #     page = 1

    #     while True:
    #         response = request("GET", f"{base_url}&page={page}", headers=headers_url.get('headers'))

    #         if not response.ok:
    #             return result

    #         page_data = response.json()
    #         result.extend(page_data)

    #         if len(page_data) < 100:
    #             break

    #         page += 1

    #     return result

    @cache(namespace="role_permissions", expire=60 * 10)
    async def get_roles_permissions(self, role_id: str, account_id: int) -> List[Dict[str, str]]:
        headers_url = await get_headers_and_url(account_id)
        base_url = f"{headers_url.get('url')}/roles/{role_id}/permissions?per_page=100"
        response = None
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, headers=headers_url.get('headers'))

        if not response.is_success:
            return []

        result = response.json()
        page = 1

        while len(result) == 100:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}&page={page}", headers=headers_url.get('headers'))
                response = response.json()
            # Check each item in the response before appending
            for item in response:
                # Assuming a successful response item is a dictionary with 'permission_name'
                if isinstance(item, dict) and 'permission_name' in item:
                    result.append(item)  # Append the individual dictionary
                else:
                    # Log or handle unexpected item
                    logger.info(f"Unexpected item in response: {item}")

        return result

    async def add_user_role(self, user_id: str, account_id: int) -> Dict[str, str]:
        headers_url = await get_headers_and_url(account_id)
        url = f"{headers_url.get('url')}/users/{user_id}/roles"
        data = {"roles": []}
        response = request("POST", url, headers=headers_url.get('headers'), data=json.dumps(data))
        return {} if not response.ok else response.json()

    async def add_metadata_to_user(self, metadata: Dict[str, str], user: User) -> Dict[str, str]:
        headers_url = await get_headers_and_url(accept="*/*", account_id=user.account_id)
        url = f"{headers_url.get('url')}/users/auth0|{user.id}"
        data = {"app_metadata": metadata}
        response = request("PATCH", url, data=json.dumps(data), headers=headers_url.get('headers'))
        return {} if not response.ok else response.json()

    async def add_metadata_to_user_account(
        self, metadata: Dict[str, str], user: User, account_id: int
    ) -> Dict[str, str]:
        headers_url = await get_headers_and_url(accept="*/*", account_id=account_id)
        url = f"{headers_url.get('url')}/users/auth0|{user.id}"
        data = {"app_metadata": metadata}
        response = request("PATCH", url, data=json.dumps(data), headers=headers_url.get('headers'))
        return {} if not response.ok else response.json()

    # async def add_permission_to_resource_server(self, permission_list: List[UpdatePermission]) -> Dict[str, str]:
    #     url = f"{headers_url.get('url')}/resource-servers/{settings.AUTH0_RESOURCE_SERVER}"
    #     headers = await get_headers_and_url(accept="*/*", account_id=account_id)
    #
    #     scopes = [
    #         {
    #             "value": f"{permission.action}:{permission.subject}",
    #             "description": f"{permission.type}, USAC",
    #         }
    #         for permission in permission_list
    #     ]
    #
    #     data = {"scopes": scopes}
    #     response = request("PATCH", url, data=json.dumps(data), headers=headers_url.get('headers'))
    #     return {} if not response.ok else response.json()

    async def get_resource_server_by_id(self, account_id) -> Dict[str, str]:
        headers_url = await get_headers_and_url(accept="*/*", account_id=account_id)
        AUTH0_RESOURCE_SERVER = headers_url["account"].cms_attributes.get("auth", {}).get("AUTH0_RESOURCE_SERVER")
        url = f"{headers_url.get('url')}/resource-servers/{AUTH0_RESOURCE_SERVER}"
        response = request("GET", url, headers=headers_url.get('headers'))
        return {} if not response.ok else response.json()

    async def add_permission_to_role(
        self, role_id: str, permission_list: List[Dict[str, str]], account_id: int
    ) -> Dict[str, str]:
        headers_url = await get_headers_and_url(accept="*/*", account_id=account_id)
        url = f"{headers_url.get('url')}/roles/{role_id}/permissions"
        added_permissions = [
            {
                "resource_server_identifier": "containerCrmApi",
                "permission_name": f"{permission.get('value')}",
            }
            for permission in permission_list
        ]

        data = {"permissions": added_permissions}
        response = request("POST", url, data=json.dumps(data), headers=headers_url.get('headers'))
        return {} if not response.ok else response.json()

    async def delete_permissions_from_role(
        self, role_id: str, permissions: List[Dict[str, str]], account_id: int
    ) -> Dict[str, str]:
        headers_url = await get_headers_and_url(account_id=account_id)
        url = f"{headers_url.get('url')}/roles/{role_id}/permissions"

        removed_permissions = [
            {
                "resource_server_identifier": "containerCrmApi",
                "permission_name": f"{permission.get('value')}",
            }
            for permission in permissions
        ]

        data = {"permissions": removed_permissions}

        response = request("DELETE", url, data=json.dumps(data), headers=headers_url.get('headers'))
        if response.status_code == 204:
            return {}
        else:
            return {} if not response.ok else response.json()

    async def assign_user_to_role(self, user: User, role_id: str) -> Dict[str, str]:
        headers_url = await get_headers_and_url(accept="*/*", account_id=user.account_id)
        url = f"{headers_url.get('url')}/roles/{role_id}/users"
        data = {"users": [f"auth0|{user.id}"]}
        response = request("POST", url, data=json.dumps(data), headers=headers_url.get('headers'))
        return {} if not response.ok else response.json()

    async def remove_role_from_user(self, user: User, role_ids: List[str]) -> Dict[str, str]:
        headers_url = await get_headers_and_url(user.account_id)
        url = f"{headers_url.get('url')}/users/auth0|{user.id}/roles"
        data = {"roles": role_ids}
        response = request("DELETE", url, data=json.dumps(data), headers=headers_url.get('headers'))
        return response.ok

    async def create_role(self, role: UpdateRole, account_id: int) -> Dict[str, str]:
        await FastAPICache.clear(namespace="roles")
        headers_url = await get_headers_and_url(account_id=account_id, accept="*/*")
        url = f"{headers_url.get('url')}/roles"
        data = {"name": role.name, "description": "USAC Role"}
        response = request("POST", url, data=json.dumps(data), headers=headers_url.get('headers'))
        return {} if not response.ok else response.json()

    async def duplicate_role_with_permissions(
        self, role_to_duplicate_id: str, new_role_name: str, account_id: int
    ) -> Dict[str, str]:
        permissions = await self.get_roles_permissions(role_to_duplicate_id, account_id)
        new_role = UpdateRole(name=new_role_name, description="USAC Role", account_id=account_id)
        duplicated_role = await self.create_role(new_role, account_id)

        permission_list = [{"value": permission.get("permission_name")} for permission in permissions]
        roles_added = await self.add_permission_to_role(duplicated_role.get("id"), permission_list, account_id)

        return {
            "id": duplicated_role.get("id"),
            "name": duplicated_role.get("name"),
            "description": duplicated_role.get("description"),
            "permissions": roles_added.get("permissions"),
        }
