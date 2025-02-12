# Python imports
import json
from typing import Generator
from unittest import skip

# Pip imports
import pytest
from faker import Faker
from fastapi import status

# Internal imports
from src.database.models.container_types import ContainerTypes
from tests.conftest import AsyncClientCustom
from tests.fixture import ContainerPriceFactory, LocationPriceFactory, UserFactory


fake = Faker()


@pytest.mark.anyio
async def test_get_all_container_prices(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    await ContainerPriceFactory.create_batch(2, account=user.account)

    response = await client.get("/prices", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get("/prices")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


@pytest.mark.anyio
async def test_get_container_price(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    container_price = await ContainerPriceFactory.create(account=user.account)

    response = await client.get(f"/price/{container_price.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/price/{container_price.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("id") == str(container_price.id)
    assert result.get("container_size") == container_price.container_size
    assert result.get("product_type") == container_price.product_type
    assert result.get("sale_price") == float(container_price.sale_price)


@pytest.mark.anyio
async def test_create_container_price(client: AsyncClientCustom, db: Generator) -> None:
    location = await LocationPriceFactory.create()
    data = {
        "container_size": fake.paragraph(nb_sentences=1),
        "product_type": ContainerTypes.SHIPPING_CONTAINER,
        "sale_price": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000)),
        "attributes": json.loads(fake.json(data_columns={"id": "pyint", "high_cube": "pystr"}, num_rows=1)),
        "condition": fake.paragraph(nb_sentences=1),
        "description": fake.paragraph(nb_sentences=1),
        "location_id": str(location.id),
    }
    user = await UserFactory.create()

    response = await client.post("/price", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.post("/price", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result.get("container_size") == data.get("container_size")
    assert result.get("product_type") == data.get("product_type")
    assert result.get("sale_price") == float(data.get("sale_price"))
    assert result.get("condition") == data.get("condition")
    assert result.get("description") == data.get("description")


@skip("Validate the reason for not finding the item")
@pytest.mark.anyio
async def test_update_container_price(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "sale_price": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000)),
        "condition": fake.paragraph(nb_sentences=1),
        "description": fake.paragraph(nb_sentences=1),
    }

    user = await UserFactory.create()
    container_price = await LocationPriceFactory.create(account=user.account)

    response = await client.patch(f"/price/{container_price.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/price/{container_price.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("sale_price") == float(data.get("sale_price"))
    assert result.get("condition") == data.get("condition")
    assert result.get("description") == data.get("description")


@skip("Validate the reason for not finding the item")
@pytest.mark.anyio
async def test_delete_container_price(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    container_price = await LocationPriceFactory.create(account=user.account)

    response = await client.delete(f"/price/{container_price.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.delete(f"/price/{container_price.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == f"Deleted container price {container_price.id}"
