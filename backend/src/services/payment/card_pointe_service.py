# Python imports
import decimal

# Pip imports
import httpx
from loguru import logger


async def authorize_and_capture_transaction(
    payment_info, merchant_id, authorization, base_url="https://fts-uat.cardconnect.com/cardconnect/rest/"
):
    """
    Authorize and capture a transaction
    """
    endpoint = base_url + "auth"
    if payment_info['cardNumber']:
        logger.info("cardNumber")
        payload = {
            "orderid": str(payment_info['display_order_id']),
            "merchid": merchant_id,
            "amount": str(round(decimal.Decimal(payment_info['total_paid']), 2)),
            "account": payment_info["cardNumber"],
            "curreny": "CAD",
            "name": payment_info['first_name'] + " " + payment_info['last_name'],
            "address": payment_info['avs_street'],
            "city": payment_info['city'],
            "expiry": payment_info['expirationDate'].replace("/", ""),
            "country": "Canada",
            "capture": "y",
            "receipt": "y",
            "ecomind": "E",
        }
    else:
        logger.info("card_pointe_token")
        payload = {
            "orderid": str(payment_info['display_order_id']),
            "merchid": merchant_id,
            "amount": str(round(decimal.Decimal(payment_info['total_paid']), 2)),
            "account": payment_info["card_pointe_token"],
            "expiry": payment_info['expirationDate'].replace("/", ""),
            "cvv2": payment_info['cardCode'],
            "name": payment_info['first_name'] + " " + payment_info['last_name'],
            "address": payment_info['avs_street'],
            "city": payment_info['city'],
            "curreny": "CAD",
            "country": "Canada",
            "capture": "y",
            "receipt": "y",
            "ecomind": "E",
        }

    headersList = {
        "Accept": "application/json",
        "Authorization": "Basic " + authorization,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(endpoint, json=payload, headers=headersList)
            response_json = response.json()
            logger.info(response_json)

            if response.status_code == 200:
                logger.info(response_json)
                if response_json['respstat'] == 'A':
                    return response_json
                else:
                    return {'errorMessage': response_json['resptext']}

            else:

                return {'errorMessage': 'Unexpected error'}

        except httpx.HTTPStatusError as e:
            return {'errorMessage': f'Error authorizing transaction: {str(e)}'}
        except Exception as e:
            return {'errorMessage': f'Unexpected error: {str(e)}'}
