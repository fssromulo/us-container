# Python imports
from typing import Generator

# Pip imports
import pytest
from faker import Faker
from fastapi import status

# Internal imports
from tests.conftest import AsyncClientCustom
from tests.fixture import CMSFactory, UserFactory


fake = Faker()


@pytest.mark.anyio
async def test_get_all_cms(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    await CMSFactory.create_batch(2, account=user.account)

    response = await client.get("/cms", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get("/cms")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


@pytest.mark.anyio
async def test_get_cms(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    cms = await CMSFactory.create(account=user.account)

    response = await client.get(f"/cms/{cms.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/cms/{cms.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("id") == str(cms.id)
    assert result.get("attributes").get("name") == cms.attributes.get("name")
    assert result.get("account_id") == cms.account_id


@pytest.mark.anyio
async def test_create_cms(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    data = {
        "attributes": {
            "name": fake.name(),
            "email": fake.email(),
        },
        "account_id": user.account_id,
    }

    response = await client.post("/cms", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post("/cms", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result.get("attributes").get("name") == data.get("attributes").get("name")
    assert result.get("attributes").get("email") == data.get("attributes").get("email")
    assert result.get("account_id") == user.account_id


@pytest.mark.anyio
async def test_update_cms(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "attributes": {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
        }
    }

    user = await UserFactory.create()
    cms = await CMSFactory.create(account=user.account)

    response = await client.patch(f"/cms/{cms.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/cms/{cms.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("attributes").get("name") is None
    assert result.get("attributes").get("email") is None
    assert result.get("attributes").get("first_name") == data.get("attributes").get("first_name")
    assert result.get("attributes").get("last_name") == data.get("attributes").get("last_name")
