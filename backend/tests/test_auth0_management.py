# Python imports
from typing import Generator
from unittest import skip
from unittest.mock import patch

# Pip imports
import pytest

# Internal imports
from src.config import settings
from src.crud.auth0_management import Auth0Management, get_auth0_admin_token, get_headers

# from src.schemas.role_permissions import UpdatePermission, UpdateRole
from src.schemas.role_permissions import UpdateRole
from tests.fixture import AccountFactory, UserFactory, mocked_requests_auth
from tests.fixture.auth0_mngmt_token import Auth0TokenFactory


auth0_management = Auth0Management()
ROLE_ID = "12f29f09-0091-4aa5-9351-b61171557a7d"


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_get_new_auth0_admin_token(mocked_requests_auth, db: Generator):
    account = await AccountFactory.create()
    token = await get_auth0_admin_token(account.id)
    assert len(token) > 0
    assert isinstance(token, str)
    mocked_requests_auth.assert_called()


@pytest.mark.anyio
async def test_get_headers():
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    headers = await get_headers(account_id=user.account.id)
    assert headers.get("Content-Type") == "application/json"
    assert headers.get("Accept") is None

    headers = await get_headers(accept="*/*", account_id=user.account.id)
    assert headers.get("Accept") == "*/*"


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_create_user(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.create_user(user=user, account_id=user.account.id)
    assert result.get('user_id') == f"auth0|{user.id}"
    assert result.get('email') == user.email
    assert result.get('given_name') == user.first_name
    assert result.get('family_name') == user.last_name
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_delete_user(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.delete_user(user)
    assert result == {}
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_create_password_change_ticket(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.create_password_change_ticket(user_id=user.id, account_id=user.account.id)
    assert settings.AUTH0_CLIENT_ID in result.get('ticket')
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@patch("src.services.email_service.post_email_message", return_value=True)
@pytest.mark.anyio
async def test_send_password_change_tickets(mocked_requests_auth, mocked_post_email_message, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)
    ticket = await auth0_management.send_password_change_tickets(user=user)
    assert 'https://login.auth0.com/' in ticket
    mocked_requests_auth.assert_called()
    mocked_post_email_message.assert_called_once()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
async def test_list_users(mocked_requests_auth, db: Generator):
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.list_users(account_id=user.account.id)
    assert result[0].get("email") == "jane@doe.com"
    assert result[0].get("given_name") == "Jane"
    assert result[0].get("family_name") == "Doe"
    assert result[0].get("nickname") == "JaneDoe"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_update_user(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    user_dict = dict(email=user.email, is_active=user.is_active, first_name=user.first_name, last_name=user.last_name)
    result = await auth0_management.update_user(existing_user=user, user=user_dict)
    assert result.get('user_id') == f"auth0|{user.id}"
    assert result.get('email') == user.email
    assert result.get('given_name') == user.first_name
    assert result.get('family_name') == user.last_name
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_get_user_role(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.get_user_role(user)
    assert result.get('name') == "create:product"
    assert result.get('description') == "USAC Role"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_get_all_roles(mocked_requests_auth, db: Generator):
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.get_all_roles(account_id=user.account.id)
    assert result[0].get('name') == "create:product"
    assert result[0].get('description') == "USAC Role"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_get_roles_permissions(mocked_requests_auth, db: Generator):
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.get_roles_permissions(role_id=ROLE_ID, account_id=user.account.id)
    assert result[0].get("resource_server_identifier") == "usac.us"
    assert result[0].get("permission_name") == "read:all_orders"
    assert result[0].get("resource_server_name") == "USAC"
    assert result[0].get("description") == "Read all orders"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_add_user_role(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.add_user_role(user_id=user.id, account_id=user.account.id)
    assert result == {}
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_add_metadata_to_user(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    metadata = {"id": str(user.id), "account_id": user.account.id}
    result = await auth0_management.add_metadata_to_user(metadata=metadata, user=user)
    assert result.get("app_metadata").get("id") == metadata.get("id")
    assert result.get("app_metadata").get("account_id") == metadata.get("account_id")
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_add_permission_to_role(mocked_requests_auth, db: Generator):
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    permission_list = [dict(value="read:all_orders", action="read", subject="Read all orders", type="resource")]
    result = await auth0_management.add_permission_to_role(
        role_id=ROLE_ID, permission_list=permission_list, account_id=user.account.id
    )
    assert isinstance(result.get("permissions"), list)
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
async def test_delete_permissions_from_role(mocked_requests_auth, db: Generator):
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    permissions = [dict(value="approve:team_members"), dict(value="create:product"), dict(value="read:all_orders")]
    result = await auth0_management.delete_permissions_from_role(
        role_id=ROLE_ID, permissions=permissions, account_id=user.account.id
    )
    assert result == {}
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
async def test_assign_user_to_role(mocked_requests_auth, db: Generator):
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.assign_user_to_role(user=user, role_id=ROLE_ID)
    assert result == {}
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_remove_role_from_user(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    result = await auth0_management.remove_role_from_user(user=user, role_ids=[ROLE_ID])
    assert result == {}
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_create_role(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    role = UpdateRole(name="read:all_orders", description="USAC Role", account_id=user.account.id)
    result = await auth0_management.create_role(role=role, account_id=user.account.id)
    assert result.get('id') is not None
    assert result.get('name') == "read:all_orders"
    assert result.get('description') == "USAC Role"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_duplicate_role_with_permissions(mocked_requests_auth, db: Generator) -> None:
    user = await UserFactory.create()
    await Auth0TokenFactory(account=user.account)

    role_id = "12f29f09-0091-4aa5-9351-b61171557a7d"
    new_role_name = "Manager"
    result = await auth0_management.duplicate_role_with_permissions(
        role_to_duplicate_id=role_id, new_role_name=new_role_name, account_id=user.account.id
    )
    assert result.get('id') is not None
    assert result.get('name') == new_role_name
    assert result.get('description') == "USAC Role"
    assert isinstance(result.get("permissions"), list)
    mocked_requests_auth.assert_called()


@skip("Not implemented")
@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
async def test_add_permission_to_resource_server(mocked_requests_auth, db: Generator) -> None:
    # permission_list = [
    #     UpdatePermission(value="read:all_orders", action="read", subject="Read all orders", type="resource")
    # ]
    # result = await auth0_management.add_permission_to_resource_server(permission_list=permission_list)
    # assert result == {}
    mocked_requests_auth.assert_called()


@skip("Not implemented")
@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
async def test_get_resource_server_by_id(mocked_requests_auth, db: Generator) -> None:
    # result = await auth0_management.get_resource_server_by_id()
    # assert result.get("id") == "Test_ID"
    # assert result.get("name") == "Test Name"
    # assert result.get("identifier") == "Test_Identifier"
    # assert result.get("token_dialect") == "Test_Token_Dialect"
    # assert result.get("scopes") == ["approve:team_members", "create:product", "read:all_orders"]
    mocked_requests_auth.assert_called()
