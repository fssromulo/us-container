# Python imports
import json
from typing import Generator

# Pip imports
import pytest
from faker import Faker

# Internal imports
from src.auth import Auth0User
from src.controllers import container_pricing
from src.database.models.container_types import ContainerTypes
from src.schemas.container_locations import CreateUpdateContainerPrice
from tests.fixture import ContainerPriceFactory, LocationPriceFactory, UserFactory


fake = Faker()


@pytest.mark.anyio
async def test_save_container_price_create(db: Generator) -> None:
    location_price = await LocationPriceFactory.create()
    data = {
        "container_size": fake.paragraph(nb_sentences=1),
        "product_type": ContainerTypes.SHIPPING_CONTAINER,
        "sale_price": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000),
        "attributes": json.loads(fake.json(data_columns={"id": "pyint", "high_cube": "pystr"}, num_rows=1)),
        "location_id": str(location_price.id),
    }
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})

    result = await container_pricing.save_container_price(
        container_price=CreateUpdateContainerPrice(**data), user=auth0_user
    )
    assert result.container_size == data.get("container_size")
    assert result.product_type == data.get("product_type")
    assert result.sale_price == data.get("sale_price")
    assert result.daily_rental_price is None
    assert result.condition is None
    assert result.description is None


@pytest.mark.anyio
async def test_save_container_price_update(db: Generator) -> None:
    data = {
        "condition": fake.paragraph(nb_sentences=1),
        "description": fake.paragraph(nb_sentences=1),
        "attributes": json.loads(fake.json(data_columns={"id": "pyint", "high_cube": "pystr"}, num_rows=1)),
    }
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    container_price_obj = await ContainerPriceFactory.create(account=user.account)
    assert container_price_obj.condition != data.get("condition")
    assert container_price_obj.description != data.get("description")

    result = await container_pricing.save_container_price(
        container_price=CreateUpdateContainerPrice(**data), user=auth0_user, container_price_id=container_price_obj.id
    )
    assert result.condition == data.get("condition")
    assert result.description == data.get("description")


@pytest.mark.anyio
async def test_get_all_container_price(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    await ContainerPriceFactory.create_batch(3, account=user.account)
    result = await container_pricing.get_all_container_prices(user=auth0_user)
    assert len(result) == 3


@pytest.mark.anyio
async def test_get_container_price(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    container_price_obj = await ContainerPriceFactory.create(account=user.account)
    result = await container_pricing.get_container_price(container_price_id=container_price_obj.id, user=auth0_user)
    assert result.container_size == container_price_obj.container_size
    assert result.product_type == container_price_obj.product_type
    assert result.sale_price == container_price_obj.sale_price
    assert result.daily_rental_price == container_price_obj.daily_rental_price


@pytest.mark.anyio
async def test_delete_container_price(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    container_price_obj = await ContainerPriceFactory.create(account=user.account)
    result = await container_pricing.delete_container_price(container_price_id=container_price_obj.id, user=auth0_user)
    assert result.message == f"Deleted container price {container_price_obj.id}"
