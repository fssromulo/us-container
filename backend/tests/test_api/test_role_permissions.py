# Python imports
from typing import Generator
from unittest.mock import patch

# Pip imports
import pytest
from fastapi import status

# Internal imports
from tests.conftest import AsyncClientCustom
from tests.fixture import UserFactory, mocked_requests_auth


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_get_roles(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()

    response = await client.get("/roles", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get("/roles")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result[0].get('name') == "create:product"
    assert result[0].get('description') == "USAC Role"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_assign_user_to_role(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    data = ["auth0|29af51b2-7b39-447b-a2ac-0036a9097be7", "auth0|891b104c-4a72-474a-b146-deee17d3b996"]

    role_id = "12f29f09-0091-4aa5-9351-b61171557a7d"
    response = await client.post(f"/user_role/{user.id}/{role_id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post(f"/user_role/{user.id}/{role_id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "User assigned to role"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_create_role(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    data = {"name": "read:all_orders", "description": "USAC Role", "account_id": user.account.id}

    response = await client.post("/role", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post("/role", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "Role created"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_get_role_for_user(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()

    response = await client.get(f"/role/{user.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/role/{user.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get('name') == "create:product"
    assert result.get('description') == "USAC Role"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_get_permissions_for_role(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    role_id = "12f29f09-0091-4aa5-9351-b61171557a7d"

    response = await client.get(f"/role_permissions/{role_id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/role_permissions/{role_id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result[0].get("resource_server_identifier") == "usac.us"
    assert result[0].get("permission_name") == "read:all_orders"
    assert result[0].get("resource_server_name") == "USAC"
    assert result[0].get("description") == "Read all orders"
    mocked_requests_auth.assert_called()


# @patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
# @pytest.mark.anyio
# async def test_create_permission(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
#     user = await UserFactory.create()
#     data = {
#         "name": "read:all_orders",
#         "action": "read",
#         "subject": "Read all orders",
#         "type": "resource",
#         "account_id": 1,
#     }
#
#     response = await client.post("/permissions", headers={"Authorization": "Bearer unauth_token"})
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#     client.force_login(user)
#     response = await client.post("/permissions", json=data)
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {}
#     mocked_requests_auth.assert_called()


# @patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
# @pytest.mark.anyio
# async def test_get_permissions(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
#     user = await UserFactory.create()
#
#     response = await client.get("/permissions")
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#     client.force_login(user)
#     response = await client.get("/permissions")
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == ["approve:team_members", "create:product", "read:all_orders"]
#     mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_assign_permission_to_role(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    data = [{"value": "approve:team_members"}, {"value": "create:product"}, {"value": "read:all_orders"}]
    role_id = "12f29f09-0091-4aa5-9351-b61171557a7d"

    response = await client.post(
        f"/assign_permission_to_role/{role_id}", headers={"Authorization": "Bearer unauth_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post(f"/assign_permission_to_role/{role_id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    mocked_requests_auth.assert_called()


@pytest.mark.skip("httpx library doesn't accept 'body' parameters in the request for the '.delete()' method.")
@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_delete_permission_from_role(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
    """
    We have a problem in this test because the httpx library doesn't
    accept 'body' parameters in the request for the '.delete()' method.
    We need to find a way to test this endpoint. Would be better if we change to a POST method.
    """
    user = await UserFactory.create()
    # data = [{"value": "approve:team_members"}]
    role_id = "12f29f09-0091-4aa5-9351-b61171557a7d"

    response = await client.delete(
        f"/delete_permission_from_role/{role_id}", headers={"Authorization": "Bearer unauth_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.delete(f"/delete_permission_from_role/{role_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "Permission deleted from role"
    mocked_requests_auth.assert_called()


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_duplicate_role_with_permissions(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    data = {"role_id": "12f29f09-0091-4aa5-9351-b61171557a7d", "role_name": "Manager"}

    response = await client.post("/duplicate-role", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post("/duplicate-role", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "Role and permissions duplicated"
    mocked_requests_auth.assert_called()
