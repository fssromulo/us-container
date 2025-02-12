# Python imports
from typing import Generator

# Pip imports
import pytest
from faker import Faker
from fastapi import status

# Internal imports
from tests.conftest import AsyncClientCustom
from tests.fixture import UserFactory, VendorsFactory


fake = Faker()


@pytest.mark.anyio
async def test_get_all_vendors(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    await VendorsFactory.create_batch(2, account=user.account)

    response = await client.get("/vendor", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get("/vendor")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


@pytest.mark.anyio
async def test_get_vendor(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    vendor = await VendorsFactory.create(account=user.account)

    response = await client.get(f"/vendor/{vendor.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/vendor/{vendor.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("id") == str(vendor.id)
    assert result.get("name") == vendor.name


@pytest.mark.anyio
async def test_create_vendor(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "name": fake.name(),
        "address": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip": fake.zipcode(),
    }
    user = await UserFactory.create()

    response = await client.post("/vendor", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post("/vendor", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result.get("name") == data.get("name")
    assert result.get("address") == data.get("address")
    assert result.get("city") == data.get("city")
    assert result.get("state") == data.get("state")
    assert result.get("zip") == data.get("zip")


@pytest.mark.anyio
async def test_update_vendor(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "secondary_email": fake.email(),
        "secondary_phone": fake.phone_number(),
        "note": {"title": fake.name(), "content": fake.text()},
    }

    user = await UserFactory.create()
    vendor = await VendorsFactory.create(account=user.account)

    response = await client.patch(f"/vendor/{vendor.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/vendor/{vendor.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("secondary_email") == data.get("secondary_email")
    assert result.get("secondary_phone") == data.get("secondary_phone")


@pytest.mark.anyio
async def test_delete_vendor(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    vendor = await VendorsFactory.create(account=user.account)

    response = await client.delete(f"/vendor/{vendor.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.delete(f"/vendor/{vendor.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "Deleted vendor"
