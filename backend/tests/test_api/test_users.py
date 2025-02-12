# Python imports
from typing import Generator
from unittest.mock import patch

# Pip imports
import pytest
from faker import Faker
from fastapi import status

# Internal imports
from src.database.models.user import User
from tests.conftest import AsyncClientCustom
from tests.fixture import UserFactory, mocked_requests_auth


fake = Faker()

HEADERS = {"Authorization": "Bearer unauth_token"}


@patch("src.crud.auth0_management.request", side_effect=mocked_requests_auth)
@pytest.mark.anyio
async def test_create_user(mocked_requests_auth, client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    user = await UserFactory.create()

    response = await client.post("/user", json=data, headers=HEADERS)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post("/user", json=data)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result.get("id") is not None
    assert result.get("email") == data.get("email")
    assert result.get("is_active") is True
    assert await User.filter(email=data.get("email")).count() == 1
    mocked_requests_auth.assert_called()


@pytest.mark.anyio
async def test_get_users(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    await UserFactory.create_batch(2, account=user.account)

    response = await client.get("/users", headers=HEADERS)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3
