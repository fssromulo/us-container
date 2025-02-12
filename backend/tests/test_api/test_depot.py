# Python imports
from typing import Generator

# Pip imports
import pytest
from faker import Faker
from fastapi import status

# Internal imports
from tests.conftest import AsyncClientCustom
from tests.fixture import DepotFactory, UserFactory


fake = Faker()


@pytest.mark.anyio
async def test_get_container_depots(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    await DepotFactory.create_batch(2, account=user.account)

    response = await client.get("/depots", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get("/depots")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


@pytest.mark.anyio
async def test_get_container_depot(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    depot = await DepotFactory.create(account=user.account)

    response = await client.get(f"/depot/{depot.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/depot/{depot.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("id") == str(depot.id)
    assert result.get("name") == depot.name
    assert result.get("account_id") == depot.account_id


@pytest.mark.anyio
async def test_create_depot(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "name": fake.name(),
        "street_address": fake.street_address(),
        "zip": fake.zipcode(),
        "primary_email": fake.email(),
        "secondary_email": fake.email(),
        "primary_phone": fake.phone_number(),
        "secondary_phone": fake.phone_number(),
        "city": fake.city(),
        "state": fake.state_abbr(),
    }
    user = await UserFactory.create()

    response = await client.post("/depot", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post("/depot", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result.get("name") == data.get("name")
    assert result.get("street_address") == data.get("street_address")
    assert result.get("zip") == str(float(data.get("zip")))
    assert result.get("account_id") == user.account_id


@pytest.mark.anyio
async def test_update_depot(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "secondary_email": fake.email(),
        "secondary_phone": fake.phone_number(),
        "note": {"title": fake.name(), "content": fake.text()},
    }

    user = await UserFactory.create()
    depot = await DepotFactory.create(account=user.account)

    response = await client.patch(f"/depot/{depot.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/depot/{depot.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("secondary_email") == data.get("secondary_email")
    assert result.get("secondary_phone") == data.get("secondary_phone")


@pytest.mark.anyio
async def test_delete_container_depot(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    depot = await DepotFactory.create(account=user.account)

    response = await client.delete(f"/depot/{depot.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.delete(f"/depot/{depot.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "Deleted depot"
