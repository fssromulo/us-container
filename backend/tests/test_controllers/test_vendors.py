# Python imports
from typing import Generator

# Pip imports
import pytest
from faker import Faker

# Internal imports
from src.auth import Auth0User
from src.controllers import vendors
from src.schemas.vendors import UpdateVendor
from tests.fixture import UserFactory, VendorsFactory


fake = Faker()


@pytest.mark.anyio
async def test_save_vendor_create(db: Generator) -> None:
    data = {
        "name": fake.name(),
        "address": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip": fake.zipcode(),
    }
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})

    result = await vendors.save_vendor(vendor=UpdateVendor(**data), user=auth0_user)
    assert result.name == data.get("name")
    assert result.address == data.get("address")
    assert result.city == data.get("city")
    assert result.state == data.get("state")
    assert result.zip == data.get("zip")
    assert result.primary_email is None
    assert result.secondary_email is None
    assert result.primary_phone is None
    assert result.secondary_phone is None


@pytest.mark.anyio
async def test_save_vendor_update(db: Generator) -> None:
    data = {
        "primary_email": fake.email(),
        "secondary_email": fake.email(),
        "primary_phone": fake.phone_number(),
        "secondary_phone": fake.phone_number(),
    }

    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    vendor_obj = await VendorsFactory.create(account=user.account)
    assert vendor_obj.primary_email != data.get("primary_email")
    assert vendor_obj.secondary_email != data.get("secondary_email")
    assert vendor_obj.primary_phone != data.get("primary_phone")
    assert vendor_obj.secondary_phone != data.get("secondary_phone")

    result = await vendors.save_vendor(vendor=UpdateVendor(**data), user=auth0_user, vendor_id=vendor_obj.id)
    assert result.primary_email == data.get("primary_email")
    assert result.secondary_email == data.get("secondary_email")
    assert result.primary_phone == data.get("primary_phone")
    assert result.secondary_phone == data.get("secondary_phone")


@pytest.mark.anyio
async def test_get_all_vendor(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    await VendorsFactory.create_batch(3, account=user.account)
    result = await vendors.get_all_vendor(user=auth0_user)
    assert len(result) == 3


@pytest.mark.anyio
async def test_get_vendor(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    vendor_obj = await VendorsFactory.create(account=user.account)
    result = await vendors.get_vendor(vendor_id=vendor_obj.id, user=auth0_user)
    assert result.name == vendor_obj.name
    assert result.address == vendor_obj.address
    assert result.city == vendor_obj.city
    assert result.state == vendor_obj.state


@pytest.mark.anyio
async def test_delete_vendor(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    vendor_obj = await VendorsFactory.create(account=user.account)
    result = await vendors.delete_vendor(vendor_id=vendor_obj.id, user=auth0_user)
    assert result.message == "Deleted vendor"
