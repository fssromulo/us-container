# Python imports
from typing import Generator

# Pip imports
import pytest
from faker import Faker
from fastapi import status

# Internal imports
from src.controllers import orders
from tests.conftest import AsyncClientCustom
from tests.fixture import LineItemFactory, NoteFactory, OrderFactory, UserFactory


fake = Faker()


@pytest.mark.anyio
async def test_order_discount_with_three_line_items(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    order = await OrderFactory.create(user=user)
    note = await NoteFactory.create(order=order)
    data = {
        "payment_type": order.payment_type,
        "remaining_balance": str(order.remaining_balance),
        "sub_total_price": str(order.sub_total_price),
        "total_price": str(order.total_price),
        "status": order.status,
        "note": {"title": note.title, "content": note.content},
        "user_id": str(order.user_id),
    }
    revenue = fake.pydecimal(positive=True, min_value=1000, max_value=10000, right_digits=2)
    line_items = await LineItemFactory.create_batch(3, revenue=revenue, order=order)

    response = await client.patch(f"/order_discount/{order.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/order_discount/{order.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    # assert result.get("is_discount_applied") is True

    line_items_quantity = len(line_items)
    discount_value = orders.get_discount_value(line_items_quantity)
    for i in range(line_items_quantity):
        assert result.get("line_items")[i].get("revenue") == float(line_items[i].revenue - discount_value)


@pytest.mark.anyio
async def test_order_discount_with_ten_line_items(client: AsyncClientCustom, db: Generator) -> None:
    user = await UserFactory.create()
    order = await OrderFactory.create(user=user)
    note = await NoteFactory.create(order=order)
    data = {
        "payment_type": order.payment_type,
        "remaining_balance": str(order.remaining_balance),
        "sub_total_price": str(order.sub_total_price),
        "total_price": str(order.total_price),
        "status": order.status,
        "note": {"title": note.title, "content": note.content},
        "user_id": str(order.user_id),
    }
    revenue = fake.pydecimal(positive=True, min_value=1000, max_value=10000, right_digits=2)
    line_items = await LineItemFactory.create_batch(10, revenue=revenue, order=order)

    response = await client.patch(f"/order_discount/{order.id}", headers={"Authorization": "Bearer unauth_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client.force_login(user)
    response = await client.patch(f"/order_discount/{order.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    # assert result.get("is_discount_applied") is True

    line_items_quantity = len(line_items)
    discount_value = orders.get_discount_value(line_items_quantity)
    for i in range(line_items_quantity):
        assert result.get("line_items")[i].get("revenue") == float(line_items[i].revenue - discount_value)
