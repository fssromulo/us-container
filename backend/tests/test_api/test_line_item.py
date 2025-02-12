# Python imports
import json
from typing import Generator
from unittest import skip
from unittest.mock import patch

# Pip imports
import pytest
from faker import Faker
from fastapi import status

# Internal imports
from tests.conftest import AsyncClientCustom
from tests.fixture import LineItemFactory, UserFactory


fake = Faker()


@pytest.mark.anyio
async def test_update_line_item(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "tax": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=750)),
        "potential_driver_charge": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=750)),
        "convenience_fee": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=250)),
        "rent_period": fake.pyint(min_value=1, max_value=100),
        "interest_owed": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000)),
        "total_rental_price": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000)),
        "monthly_owed": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000)),
        "attributes": json.loads(fake.json(data_columns={"id": "pyint", "name": "name", "email": "email"}, num_rows=1)),
    }

    user = await UserFactory.create()
    line_item = await LineItemFactory.create(account=user.account)

    response = await client.patch(f"/line_item/{line_item.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/line_item/{line_item.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("tax") == data.get("tax")
    assert result.get("potential_driver_charge") == data.get("potential_driver_charge")
    assert result.get("convenience_fee") == data.get("convenience_fee")


@pytest.mark.anyio
async def test_calculated_potential_driver_charge(client: AsyncClientCustom, db: Generator) -> None:
    data = {
        "potential_dollar_per_mile": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=500)),
        "potential_miles": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000)),
        "shipping_cost": float(fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=100)),
    }

    user = await UserFactory.create()
    line_item = await LineItemFactory.create(shipping_cost=data.get("shipping_cost"), account=user.account)

    response = await client.patch(f"/line_item/{line_item.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/line_item/{line_item.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("shipping_cost") != float(line_item.shipping_cost)
    assert result.get("potential_miles") == data.get("potential_miles")
    assert result.get("potential_dollar_per_mile") == data.get("potential_dollar_per_mile")


@pytest.mark.anyio
async def test_get_line_item(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    line_item = await LineItemFactory.create(account=user.account)

    response = await client.get(f"/line_item/{line_item.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/line_item/{line_item.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result.get("potential_dollar_per_mile") == float(line_item.potential_dollar_per_mile)
    assert result.get("potential_miles") == float(line_item.potential_miles)
    assert result.get("product_cost") == float(line_item.product_cost)
    assert result.get("revenue") == float(line_item.revenue)
    assert result.get("shipping_revenue") == float(line_item.shipping_revenue)
    assert result.get("shipping_cost") == float(line_item.shipping_cost)
    assert result.get("tax") == float(line_item.tax)


@skip("TODO: Need some logic to test this")
@patch("src.services.email_service.post_email_message", return_value=True)
@pytest.mark.anyio
async def test_send_pickup_email(mocked_post_email_message, client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    line_item = await LineItemFactory.create(account=user.account)

    response = await client.get(
        f"/line_item/pickup_email/{line_item.id}", headers={"Authorization": "Bearer unauth_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.get(f"/line_item/pickup_email/{line_item.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "Success sending pickup email"
    mocked_post_email_message.assert_called_once()
