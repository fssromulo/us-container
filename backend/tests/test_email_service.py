# Python imports
import unittest
from datetime import datetime
from typing import Generator
from unittest.mock import patch

# Pip imports
import pytest

# Internal imports
from src.database.models.pricing.region import Region
from src.schemas.orders import OrderOut
from src.services.notifications import email_service
from tests.fixture import mocked_requests_get


@patch("requests.get", side_effect=mocked_requests_get)
def test_validate_email(mocked_requests_get) -> None:
    assert email_service.validate_email("test@container-crm.com") is True
    mocked_requests_get.assert_called_once()


@unittest.skip("Need a way to create a OrderOut object")
@patch("requests.get", side_effect=mocked_requests_get)
@patch("src.services.email_service.post_email_message", return_value=True)
def test_send_driver_email(mocked_post_email_message) -> None:
    customer_order = OrderOut()
    assert email_service.send_driver_email(customer_order=customer_order, region=Region.WEST) is True
    mocked_post_email_message.assert_called_once()


@unittest.skip("Need a way to create a OrderOut object")
@patch("src.services.email_service.post_email_message", return_value=True)
@pytest.mark.anyio
async def test_send_customer_pickup_email(mocked_post_email_message, db: Generator) -> None:
    customer_order = OrderOut()
    assert email_service.send_customer_pickup_email(customer_order=customer_order, region=Region.WEST) is True
    mocked_post_email_message.assert_called_once()


@patch("src.services.email_service.post_email_message", return_value=True)
def test_send_customer_invoice_email(mocked_post_email_message) -> None:
    item = {
        "customer_email": "test@container-crm.com",
        "attributes": dict(is_quote_title=True),
        "created_at": datetime.now(),
        "line_items": [],
        "display_order_id": "1",
        "is_rent_to_own": False,
        "quote_title": "test quote title",
    }
    assert email_service.send_customer_invoice_email(item=item) is True
    mocked_post_email_message.assert_called_once()


@patch("src.services.email_service.post_email_message", return_value=True)
def test_send_customer_general_receipt_email(mocked_post_email_message) -> None:
    order = {
        "id": 1,
        "order_id": 1,
        "display_order_id": "1",
        "customer": dict(full_name="Full Name", email="test@container-crm.com", phone="1234567890"),
        "address": dict(full_address="test address"),
        "is_rent_to_own": False,
        "type": "RENT_TO_OWN",
    }
    assert email_service.send_customer_general_receipt_email(order=order) is True
    mocked_post_email_message.assert_called_once()


@patch("src.services.email_service.post_email_message", return_value=True)
def test_send_paid_email(mocked_post_email_message) -> None:
    order = {
        "order_id": 1,
        "display_order_id": "1",
        "customer": dict(full_name="Full Name", email="test@container-crm.com", phone="1234567890"),
        "address": dict(full_address="test address"),
        "is_rent_to_own": False,
    }
    assert email_service.send_paid_email(order=order) is True
    mocked_post_email_message.assert_called_once()


@patch("src.services.email_service.post_email_message", return_value=True)
def test_send_change_password_email(mocked_post_email_message) -> None:
    info = dict(first_name="Name Test", company_name="Company Test", url="http://example.com")
    assert email_service.send_change_password_email(info=info) is True
    mocked_post_email_message.assert_called_once()


@patch("src.services.email_service.post_email_message", return_value=True)
def test_send_agent_email(mocked_post_email_message):
    assert email_service.send_agent_email(text="text", emails=["test@container-crm.com"]) is True
    mocked_post_email_message.assert_called_once()
