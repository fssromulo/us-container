# Python imports
import json
import os
from datetime import datetime, timedelta

# Pip imports
import requests
from loguru import logger


"""
Charge a credit card
"""
TEST_URL = "https://sandbox.usaepay.com/api/v2"
LIVE_URL = "https://usaepay.com/api/v2"

URL = LIVE_URL if os.environ.get("STAGE", "dev") == "prod" else TEST_URL


def get_all_data(retrieval_function, api_key, *args):
    limit = 500
    offset = 0
    all_data = []

    while True:
        response = retrieval_function(limit, offset, api_key, *args)
        data = response.get('data', [])

        if not data:
            logger.info(f"no data found for {retrieval_function.__name__}")
            break

        all_data.extend(data)
        total_records = response.get('total', 0)

        offset += limit
        if offset >= int(total_records):
            break

    return all_data


def create_description(order_details):
    if order_details.get('order_type') == 'RENT':
        description = "RENT"
    elif order_details.get('order_type') == 'PURCHASE' or order_details.get('order_type') == 'PURCHASE_ACCESSORY':
        description = "PURCHASE"
    elif order_details.get('order_type') == 'RENT_TO_OWN':
        description = "RENT_TO_OWN"
    return description[:-2]


def charge_credit_card(order_details, api_key, customer_key=None):
    save_customer = order_details.get('order_type') == 'RENT' or order_details.get('order_type') == 'RENT_TO_OWN'

    jsonRequest = {
        "command": "sale",
        "invoice": order_details['display_order_id'],
        "description": create_description(order_details),
        "email": order_details['email'],
        "send_receipt": 1,
        "ignore_duplicate": 1,
        "merchemailaddr": "",
        "custkey": customer_key or "",
        "save_customer": save_customer,
        "save_customer_paymethod": save_customer,
        "amount": str(order_details['total_paid']),
        "creditcard": {
            "cardholder": "{} {}".format(order_details['first_name'].strip(), order_details['last_name'].strip()),
            "number": order_details['cardNumber'],
            "expiration": order_details['expirationDate'],
            "cvc": order_details['cardCode'],
            "avs_street": f"{order_details['avs_street'].strip()} {order_details['city'].strip()}",
            "avs_zip": order_details['zip'],
        },
        "billing_address": {
            "firstname": order_details['first_name'],
            "lastname": order_details['last_name'],
            "street": order_details['avs_street'],
            "city": order_details['city'],
            "state": order_details['state'],
            "postalcode": order_details['zip'],
            "country": "USA",
        },
        "shipping_address": {
            "firstName": order_details['shipping_details']['first_name'],
            "lastName": order_details['shipping_details']['last_name'],
            "street": order_details['shipping_details']['street_address'],
            "city": order_details['shipping_details']['city'],
            "state": order_details['shipping_details']['state'],
            "postalcode": order_details['shipping_details']['zip'],
            "country": "USA",
        },
        "lineitems": [
            {
                "name": item['name'],
                "cost": str(item['price']),
                "qty": 1,
            }
            for item in order_details['line_items']
        ],
    }
    headers = {"content-type": "application/json", "Authorization": "Basic {}".format(api_key)}

    response = requests.post(f"{URL}/transactions", data=json.dumps(jsonRequest), headers=headers)
    if response.status_code == 200:
        response = response.json()
        # approved or partially approved.
        if response['result_code'] == 'E':
            return {'errorMessage': response['error']}
        if response['result_code'] not in ['A', 'P']:
            return {'errorMessage': response['result']}
        # if response['avs']['result_code'] != 'Y':
        #   return {
        #       'errorMessage': '''Billing address/zip doesn't match credit card'''
        #   }
        # if response['cvc']['result_code'] != 'M':
        #   return {
        #       'errorMessage': 'CVC is incorrect'
        #   }
    else:
        return {'errorMessage': '''Couldn't process credit card'''}

    return response


def create_customer_from_transaction(transaction_key, api_key):
    body = {"transaction_key": transaction_key}
    headers = {"content-type": "application/json", "Authorization": "Basic {}".format(api_key)}

    response = requests.post(f"{URL}/customers", data=json.dumps(body), headers=headers)
    return response.json()


def create_customer(order_details, api_key):
    body = {
        "company": "",
        "customerid": "",
        "first_name": order_details['first_name'],
        "last_name": order_details['last_name'],
        "street": order_details['avs_street'],
        "city": order_details['city'],
        "state": order_details['state'],
        "postalcode": order_details['zip'],
        "country": "USA",
        "phone": order_details['phone_number'],
        "email": order_details['email'],
    }

    headers = {"content-type": "application/json", "Authorization": "Basic {}".format(api_key)}

    response = requests.post(f"{URL}/customers", data=json.dumps(body), headers=headers)
    return response.json()


def setup_schedule(order_details, api_key):
    # 2019-01-31
    # start_date = datetime.now().strftime("%Y-%m-%d")
    # get current day of month
    current_day = datetime.now().day
    # set to 30 days from now. First month is in a regular transaction.
    request_data = [
        {
            "amount": str(order_details['calculated_monthly_owed_total']),
            "currency_code": "",
            "paymethod_key": order_details['paymethod_key'],
            "description": "Container purchase",
            "enabled": True,
            "frequency": "monthly",
            "next_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "numleft": "-1" if order_details.get('type') == 'RENT' else str(order_details.get('rent_period')),
            "orderid": str(order_details['display_order_id']),
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "tax": "0.00",
            "source": "",
            "send_receipt": True,
            "skip_count": "1",
            "rules": [{"day_offset": current_day, "month_offset": "0", "subject": "Day"}],
        }
    ]
    logger.info(request_data)

    headers = {"content-type": "application/json", "Authorization": "Basic {}".format(api_key)}

    response = requests.post(f"{URL}/transactions", data=json.dumps(request_data), headers=headers)
    return response.json()


def get_schedule_list(customer_id, api_key):
    headers = {"content-type": "application/json", "Authorization": "Basic {}".format(api_key)}

    return requests.get(f"{URL}/customers/{customer_id}/billing_schedules", headers=headers)


def get_customer(customer_id, api_key):
    headers = {"content-type": "application/json", "Authorization": "Basic {}".format(api_key)}

    response = requests.get(f"{URL}/customers/{customer_id}", headers=headers)
    return response.json()


def get_customers(limit, offset, api_key):
    headers = {"content-type": "application/json", "Authorization": "Basic {}".format(api_key)}

    response = requests.get(f"{URL}/customers?limit={limit}&offset={offset}", headers=headers)
    return response.json()


def get_customer_transactions(limit, offset, api_key, cust_key=None):
    headers = {"content-type": "application/json", "Authorization": "Basic {}".format(api_key)}
    response = requests.get(f"{URL}/customers/{cust_key}/transactions?limit={limit}&offset={offset}", headers=headers)
    return response.json()


def quick_sale(tran_key, amount, api_key):
    headers = {"content-type": "application/json", "Authorization": "Basic {}".format(api_key)}

    body = {
        "command": "quicksale",
        "trankey": tran_key,
        "amount": str(amount),
    }

    response = requests.post(f"{URL}/transactions", data=json.dumps(body), headers=headers)
    return response.json()
