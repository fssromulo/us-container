# Python imports
from typing import Generator

# Pip imports
import pytest
from faker import Faker

# Internal imports
from src.auth import Auth0User
from src.controllers import depot
from src.schemas.depot import CreateOrUpdateDepot
from tests.fixture import DepotFactory, UserFactory


fake = Faker()


@pytest.mark.anyio
async def test_save_depot_create(db: Generator) -> None:
    data = {
        "name": fake.name(),
        "primary_email": fake.email(),
        "primary_phone": fake.phone_number(),
        "street_address": fake.street_address(),
        "zip": fake.zipcode(),
        "city": fake.city(),
        "state": fake.state_abbr(),
    }
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})

    result = await depot.save_depot(depot=CreateOrUpdateDepot(**data), user=auth0_user)
    assert result.name == data.get("name")
    assert result.primary_email == data.get("primary_email")
    assert result.primary_phone == data.get("primary_phone")
    assert result.street_address == data.get("street_address")
    assert result.zip == str(float(data.get("zip")))
    assert result.city == data.get("city")
    assert result.state == data.get("state")
    assert result.secondary_email is None
    assert result.secondary_phone is None


@pytest.mark.anyio
async def test_save_depot_update(db: Generator) -> None:
    data = {
        "name": fake.name(),
        "secondary_email": fake.email(),
        "secondary_phone": fake.phone_number(),
    }
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    depot_obj = await DepotFactory.create(account=user.account)

    assert depot_obj.name != data.get("name")
    assert depot_obj.secondary_email != data.get("secondary_email")
    assert depot_obj.secondary_phone != data.get("secondary_phone")

    result = await depot.save_depot(depot=CreateOrUpdateDepot(**data), user=auth0_user, depot_id=depot_obj.id)
    assert result.name == data.get("name")
    assert result.secondary_email == data.get("secondary_email")
    assert result.secondary_phone == data.get("secondary_phone")


@pytest.mark.anyio
async def test_get_all_container_depots(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    await DepotFactory.create_batch(2, account=user.account)
    result = await depot.get_all_container_depots(user=auth0_user)
    assert len(result) == 2


@pytest.mark.anyio
async def test_get_container_depot(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    depot_obj = await DepotFactory.create(account=user.account)
    result = await depot.get_container_depot(container_depot_id=depot_obj.id, user=auth0_user)
    assert result.name == depot_obj.name
    assert result.primary_email == depot_obj.primary_email
    assert result.primary_phone == depot_obj.primary_phone
    assert result.city == depot_obj.city


@pytest.mark.anyio
async def test_delete_container_depot(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    depot_obj = await DepotFactory.create(account=user.account)
    result = await depot.delete_container_depot(container_depot_id=depot_obj.id, user=auth0_user)
    assert result.message == "Deleted depot"
