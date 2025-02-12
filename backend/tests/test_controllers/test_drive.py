# Python imports
from typing import Generator

# Pip imports
import pytest
from faker import Faker

# Internal imports
from src.auth import Auth0User
from src.controllers import driver
from src.schemas.driver import UpdateDriver
from tests.fixture import DriverFactory, UserFactory


fake = Faker()


@pytest.mark.anyio
async def test_save_driver_create(db: Generator) -> None:
    data = {
        "company_name": fake.name(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "phone_number": fake.phone_number(),
        "email": fake.email(),
    }
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})

    result = await driver.save_driver(driver=UpdateDriver(**data), user=auth0_user)
    assert result.company_name == data.get("company_name")
    assert result.city == data.get("city")
    assert result.state == data.get("state")
    assert result.phone_number == data.get("phone_number")
    assert result.email == data.get("email")
    assert result.cost_per_mile is None
    assert result.cost_per_100_miles is None


@pytest.mark.anyio
async def test_save_driver_update(db: Generator) -> None:
    data = {
        "company_name": fake.name(),
        "cost_per_mile": fake.pyfloat(right_digits=2, positive=True, min_value=2, max_value=10),
        "cost_per_100_miles": fake.pyfloat(right_digits=2, positive=True, min_value=100, max_value=10000),
    }

    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    driver_obj = await DriverFactory.create(account=user.account)
    assert driver_obj.company_name != data.get("company_name")
    assert driver_obj.cost_per_mile != data.get("cost_per_mile")
    assert driver_obj.cost_per_100_miles != data.get("cost_per_100_miles")

    result = await driver.save_driver(driver=UpdateDriver(**data), user=auth0_user, driver_id=driver_obj.id)
    assert result.company_name == data.get("company_name")
    assert float(result.cost_per_mile) == data.get("cost_per_mile")
    assert float(result.cost_per_100_miles) == data.get("cost_per_100_miles")


@pytest.mark.anyio
async def test_get_all_container_drivers(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    await DriverFactory.create_batch(3, account=user.account)
    result = await driver.get_all_container_drivers(user=auth0_user)
    assert len(result) == 3


@pytest.mark.anyio
async def test_get_container_driver(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    driver_obj = await DriverFactory.create(account=user.account)
    result = await driver.get_container_driver(driver_id=driver_obj.id, user=auth0_user)
    assert result.company_name == driver_obj.company_name
    assert result.phone_number == driver_obj.phone_number
    assert result.email == driver_obj.email
    assert result.city == driver_obj.city
    assert result.state == driver_obj.state


@pytest.mark.anyio
async def test_delete_container_driver(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    driver_obj = await DriverFactory.create(account=user.account)
    result = await driver.delete_container_driver(driver_id=driver_obj.id, user=auth0_user)
    assert result.message == "Deleted driver"
