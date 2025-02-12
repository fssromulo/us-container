# Python imports
import asyncio

# Pip imports
from loguru import logger

# Internal imports
from src.services.payment.card_pointe_service import authorize_and_capture_transaction


payment_info = {
    "display_order_id": 12345,
    "total_paid": "1100.35",
    "cardNumber": "374245001721009",  # Sample Visa test card
    "first_name": "John",
    "last_name": "Doe",
    "avs_street": "123 Main St",
    "city": "Toronto",
    "country": "Canada",
    "card_pointe_token": "",
    "expirationDate": "12/24",
    "cardCode": "123",
}

# Test merchant ID and basic authorization
merchant_id = "800000009928"
authorization = ""  # Example base64-encoded string

# Testing function
async def test_authorize_and_capture_transaction():
    result = await authorize_and_capture_transaction(payment_info, merchant_id, authorization)
    logger.info("Result:", result)


# Run the test
asyncio.run(test_authorize_and_capture_transaction())
