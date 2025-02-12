# Python imports
import json
from decimal import Decimal
from typing import Generator
from unittest import skip
from unittest.mock import patch

# Pip imports
import pytest
from faker import Faker

# Internal imports
from src.auth import Auth0User
from src.controllers import line_item
from src.schemas.line_items import UpdateLineItem
from tests.fixture import LineItemFactory, UserFactory


fake = Faker()


def test_random_number() -> None:
    assert isinstance(line_item.random_number(), int)


@pytest.mark.anyio
async def test_save_line_item_update(db: Generator) -> None:
    data = {
        "minimum_shipping_cost": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=200),
        "potential_dollar_per_mile": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=500),
        "potential_miles": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000),
        "product_cost": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000),
        "revenue": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000),
        "shipping_revenue": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=100),
        "shipping_cost": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=100),
        "tax": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=750),
        "potential_driver_charge": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=750),
        "convenience_fee": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=250),
        "rent_period": fake.pyint(min_value=1, max_value=100),
        "interest_owed": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000),
        "total_rental_price": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000),
        "monthly_owed": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000),
        "attributes": json.loads(fake.json(data_columns={"id": "pyint", "name": "name", "email": "email"}, num_rows=1)),
    }

    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    line_item_obj = await LineItemFactory.create(account=user.account)
    assert line_item_obj.shipping_cost != data.get("shipping_cost")
    assert line_item_obj.potential_miles != data.get("potential_miles")
    assert line_item_obj.potential_dollar_per_mile != data.get("potential_dollar_per_mile")

    result = await line_item.save_line_item(
        line_item=UpdateLineItem(**data), user=auth0_user, line_item_id=line_item_obj.id
    )
    assert result.shipping_cost == data.get("shipping_cost")
    assert result.potential_miles == data.get("potential_miles")
    assert result.potential_dollar_per_mile == data.get("potential_dollar_per_mile")


@pytest.mark.anyio
async def test_calculated_potential_driver_charge(db: Generator) -> None:
    data = {
        "potential_dollar_per_mile": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=500),
        "potential_miles": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=10000),
        "shipping_cost": fake.pydecimal(right_digits=2, positive=True, min_value=1, max_value=100),
    }

    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})

    line_item_obj = await LineItemFactory.create(shipping_cost=data.get("shipping_cost"), account=user.account)
    assert isinstance(line_item_obj.shipping_cost, Decimal)
    assert line_item_obj.potential_dollar_per_mile != data.get("potential_dollar_per_mile")
    assert line_item_obj.potential_miles != data.get("potential_miles")

    result = await line_item.update_line_item(
        line_item=UpdateLineItem(**data), user=auth0_user, line_item_id=line_item_obj.id
    )
    assert result.shipping_cost != line_item_obj.shipping_cost
    assert result.potential_miles == data.get("potential_miles")
    assert result.potential_dollar_per_mile == data.get("potential_dollar_per_mile")


@pytest.mark.anyio
async def test_get_line_item(db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    line_item_obj = await LineItemFactory.create(account=user.account)
    result = await line_item.get_line_item(line_item_id=line_item_obj.id, user=auth0_user)
    assert result.potential_dollar_per_mile == line_item_obj.potential_dollar_per_mile
    assert result.potential_miles == line_item_obj.potential_miles
    assert result.product_cost == line_item_obj.product_cost
    assert result.revenue == line_item_obj.revenue
    assert result.shipping_revenue == line_item_obj.shipping_revenue
    assert result.shipping_cost == line_item_obj.shipping_cost
    assert result.tax == line_item_obj.tax


@skip("TODO: Need some logic to test this")
@patch("src.services.email_service.post_email_message", return_value=True)
@pytest.mark.anyio
async def test_send_pickup_email(mocked_post_email_message, db: Generator) -> None:
    user = await UserFactory.create()
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    line_item_obj = await LineItemFactory.create(account=user.account)
    result = await line_item.send_pickup_email(line_item_id=line_item_obj.id, user=auth0_user)
    assert result.message == "Success sending pickup email"
    mocked_post_email_message.assert_called_once()
