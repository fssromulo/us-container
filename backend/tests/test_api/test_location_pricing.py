# Python imports
from typing import Generator

# Pip imports
import pytest
from faker import Faker
from fastapi import status

# Internal imports
from tests.conftest import AsyncClientCustom
from tests.fixture import LocationPriceFactory, UserFactory


fake = Faker()

HEADERS = {"Authorization": "Bearer unauth_token"}


@pytest.mark.anyio
async def test_create_location(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    data = {
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip": fake.zipcode(),
        "region": "WEST",
        "cost_per_mile": fake.pyfloat(right_digits=2, positive=True, min_value=2, max_value=10),
        "minimum_shipping_cost": fake.pyfloat(right_digits=2, positive=True, min_value=100, max_value=10000),
    }
    response = await client.post("/location", json=data, headers=HEADERS)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post("/location", json=data)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result.get("city") == data.get("city")
    assert result.get("state") == data.get("state")
    assert result.get("zip") == data.get("zip")
    assert result.get("region") == data.get("region")
    assert result.get("cost_per_mile") == data.get("cost_per_mile")
    assert result.get("minimum_shipping_cost") == data.get("minimum_shipping_cost")


@pytest.mark.anyio
async def test_get_container_locations(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    await LocationPriceFactory.create_batch(2, account_id=user.account.id)

    response = await client.get("/locations", headers=HEADERS)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get("/locations")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


@pytest.mark.anyio
async def test_get_container_location(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    location_price = await LocationPriceFactory.create(account_id=user.account.id)

    response = await client.get(f"/location/{location_price.id}", headers=HEADERS)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/location/{location_price.id}")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result.get("id") == str(location_price.id)
    assert result.get("city") == location_price.city
    assert result.get("state") == location_price.state
    assert result.get("zip") == location_price.zip
    assert result.get("region") == location_price.region
    assert result.get("cost_per_mile") == float(location_price.cost_per_mile)
    assert result.get("minimum_shipping_cost") == float(location_price.minimum_shipping_cost)


@pytest.mark.anyio
async def test_update_container_location(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    location_price = await LocationPriceFactory.create(account_id=user.account.id)
    data = {
        "cost_per_mile": fake.pyfloat(right_digits=2, positive=True, min_value=2, max_value=10),
        "minimum_shipping_cost": fake.pyfloat(right_digits=2, positive=True, min_value=100, max_value=10000),
    }

    response = await client.patch(f"/location/{location_price.id}", json=data, headers=HEADERS)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/location/{location_price.id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result.get("cost_per_mile") == data.get("cost_per_mile")
    assert result.get("minimum_shipping_cost") == data.get("minimum_shipping_cost")


@pytest.mark.anyio
async def test_delete_container_location(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    location_price = await LocationPriceFactory.create(account_id=user.account.id)

    response = await client.delete(f"/location/{location_price.id}", headers=HEADERS)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.delete(f"/location/{location_price.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "Deleted location"
