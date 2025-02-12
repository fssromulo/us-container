# Python imports
from typing import Generator

# Pip imports
import pytest
from faker import Faker
from fastapi import status

# Internal imports
from tests.conftest import AsyncClientCustom
from tests.fixture import DriverFactory, UserFactory


fake = Faker()


@pytest.mark.anyio
async def test_get_container_drivers(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    await DriverFactory.create_batch(2, account=user.account)

    response = await client.get("/drivers", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get("/drivers")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


@pytest.mark.anyio
async def test_get_container_driver(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    driver = await DriverFactory.create(account=user.account)

    response = await client.get(f"/driver/{driver.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/driver/{driver.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("id") == str(driver.id)
    assert result.get("company_name") == driver.company_name
    assert result.get("account_id") == driver.account_id


@pytest.mark.anyio
async def test_create_driver(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "company_name": fake.name(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "phone_number": fake.phone_number(),
        "email": fake.email(),
        "cost_per_mile": fake.pyfloat(right_digits=2, positive=True, min_value=2, max_value=10),
        "cost_per_100_miles": fake.pyfloat(right_digits=2, positive=True, min_value=100, max_value=10000),
    }
    user = await UserFactory.create()

    response = await client.post("/driver", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post("/driver", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result.get("company_name") == data.get("company_name")
    assert result.get("city") == data.get("city")
    assert result.get("state") == data.get("state")
    assert result.get("phone_number") == data.get("phone_number")
    assert result.get("email") == data.get("email")
    assert result.get("cost_per_mile") == data.get("cost_per_mile")
    assert result.get("cost_per_100_miles") == data.get("cost_per_100_miles")
    assert result.get("account_id") == user.account_id


@pytest.mark.anyio
async def test_update_driver(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "city": fake.city(),
        "state": fake.state_abbr(),
        "cost_per_mile": fake.pyfloat(right_digits=2, positive=True, min_value=2, max_value=10),
        "cost_per_100_miles": fake.pyfloat(right_digits=2, positive=True, min_value=100, max_value=10000),
        "note": {"title": fake.name(), "content": fake.text()},
    }

    user = await UserFactory.create()
    driver = await DriverFactory.create(account=user.account)

    response = await client.patch(f"/driver/{driver.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/driver/{driver.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("city") == data.get("city")
    assert result.get("state") == data.get("state")
    assert result.get("cost_per_mile") == data.get("cost_per_mile")
    assert result.get("cost_per_100_miles") == data.get("cost_per_100_miles")


@pytest.mark.anyio
async def test_delete_container_driver(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    driver = await DriverFactory.create(account=user.account)

    response = await client.delete(f"/driver/{driver.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.delete(f"/driver/{driver.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "Deleted driver"
