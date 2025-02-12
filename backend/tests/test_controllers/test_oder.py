# Python imports
from decimal import Decimal
from typing import Generator

# Pip imports
import pytest
from faker import Faker
from fastapi import HTTPException

# Internal imports
from src.auth import Auth0User
from src.controllers import orders
from tests.fixture import DriverFactory, LineItemFactory, OrderFactory, UserFactory


fake = Faker()


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (1, Decimal("0")),
        (2, Decimal("0")),
        (3, Decimal("100")),
        (9, Decimal("100")),
        (10, Decimal("150")),
        (15, Decimal("150")),
    ],
)
def test_get_discount_value(test_input, expected) -> None:
    assert orders.get_discount_value(test_input) == expected


@pytest.mark.anyio
async def test_update_order_discount_already_applied(db: Generator) -> None:
    user = await UserFactory.create()
    order = await OrderFactory.create(user=user, is_discount_applied=True)
    await LineItemFactory.create_batch(3, revenue=1000, order=order)
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    with pytest.raises(HTTPException):
        await orders.update_order_discount(order.id, auth0_user)


@pytest.mark.anyio
async def test_update_order_discount_not_applicable(db: Generator) -> None:
    user = await UserFactory.create()
    order = await OrderFactory.create(user=user)
    await LineItemFactory.create_batch(2, revenue=1000, order=order)
    auth0_user = Auth0User(sub=f"auth0|{user.id}", email=user.email, app_metadata={"account_id": user.account.id})
    with pytest.raises(HTTPException):
        await orders.update_order_discount(order.id, auth0_user)


@pytest.mark.anyio
async def test_update_order_discount_with_three_line_items(db: Generator) -> None:
    user = await UserFactory.create()
    driver = await DriverFactory.create(account=user.account)
    potential_driver = await DriverFactory.create(account=user.account)
    order = await OrderFactory.create(user=user, driver=driver)
    revenue = fake.pydecimal(positive=True, min_value=1000, max_value=10000, right_digits=2)

    line_items = await LineItemFactory.create_batch(
        3, revenue=revenue, order=order, potential_driver=potential_driver, account=user.account
    )
    auth0_user = Auth0User(
        sub=f"auth0|{user.id}", email=user.email, app_metadata={"id": user.id, "account_id": user.account.id}
    )
    update_order = await orders.update_order_discount(order.id, auth0_user)
    # assert update_order.is_discount_applied is True

    line_items_quantity = len(line_items)
    discount_value = orders.get_discount_value(line_items_quantity)
    for i in range(line_items_quantity):
        assert update_order.line_items[i].revenue == line_items[i].revenue - discount_value


@pytest.mark.anyio
async def test_update_order_discount_with_ten_line_items(db: Generator) -> None:
    user = await UserFactory.create()
    driver = await DriverFactory.create(account=user.account)
    potential_driver = await DriverFactory.create(account=user.account)
    order = await OrderFactory.create(user=user, driver=driver)
    revenue = fake.pydecimal(positive=True, min_value=1000, max_value=10000, right_digits=2)

    line_items = await LineItemFactory.create_batch(
        10, revenue=revenue, order=order, potential_driver=potential_driver, account=user.account
    )
    auth0_user = Auth0User(
        sub=f"auth0|{user.id}", email=user.email, app_metadata={"id": user.id, "account_id": user.account.id}
    )
    update_order = await orders.update_order_discount(order.id, auth0_user)
    # assert update_order.is_discount_applied is True

    line_items_quantity = len(line_items)
    discount_value = orders.get_discount_value(line_items_quantity)
    for i in range(line_items_quantity):
        assert update_order.line_items[i].revenue == line_items[i].revenue - discount_value
