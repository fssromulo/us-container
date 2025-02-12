# Python imports
import decimal
import json
from typing import Any

# Pip imports
import requests
from loguru import logger

# Internal imports
from src.controllers import orders as order_controller
from src.crud.note_crud import note_crud
from src.crud.order_crud import order_crud
from src.database.models.orders.order import Order
from src.schemas.notes import NoteInSchema
from src.schemas.orders import OrderInUpdate
from src.utils.convert_string import extract_integers_from_string


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)


def create_line_item(i):
    name = i['name'].replace('High Cube', 'HC')
    name = name.replace('Standard', 'STD')
    name = name.replace('Double Door', 'DD')
    name = name[:30]

    return {
        "itemId": str(i['id'])[:5],
        "name": name,
        "quantity": 1,
        "unitPrice": i['price'],
        "taxable": True,
    }


def merchant_authentication(name, trans_key):
    return {"name": name, "transactionKey": trans_key}


def send_request(url, body):
    headers = {"content-type": "application/json"}
    response = requests.post(url, data=json.dumps(body, cls=DecimalEncoder), headers=headers)
    return response


def handle_response(response):
    if response is not None:
        response = response.content.decode('utf-8-sig')
        response = json.loads(response)
        if 'errors' in response.get("transactionResponse", {}):
            response['errorMessage'] = str(response["transactionResponse"]["errors"][0]["errorText"])
        print_response_messages(response)
        if response.get("messages", {}).get("resultCode", {}) == "Error":
            response['errorMessage'] = str(response["messages"]["message"][0]["text"])
        return response
    else:
        logger.info('Null Response.')
        return {'errorMessage': 'Null Response.'}


def print_response_messages(response):
    if response['messages']['resultCode'] == "Ok":
        print_success_messages(response)
    else:
        print_error_messages(response)


def print_success_messages(response):
    if 'transId' in response.get('transactionResponse', {}) and 'responseCode' in response['transactionResponse']:
        logger.info(
            'Successfully created transaction with Transaction ID: %s' % response["transactionResponse"]['transId']
        )
        logger.info('Transaction Response Code: %s' % response["transactionResponse"]['responseCode'])

    if 'messages' in response.get("transactionResponse", {}):
        logger.info('Message Code: %s' % response["transactionResponse"]['messages'][0]['code'])
        logger.info('Description: %s' % response["transactionResponse"]['messages'][0]['description'])


def print_error_messages(response):
    if 'transactionResponse' in response and 'errors' in response["transactionResponse"]:
        logger.info('Error Code: %s' % str(response["transactionResponse"]["errors"][0]["errorCode"]))
        logger.info('Error message: %s' % response["transactionResponse"]["errors"][0]["errorText"])
    elif 'messages' in response:
        logger.info('Error Code: %s' % response["messages"]["message"][0]['code'])
        logger.info('Error message: %s' % response["messages"]["message"][0]['text'])


def get_settled_transactions(batch_id, live_name, live_trans_key, url):
    body = {
        "getTransactionListRequest": {
            "merchantAuthentication": merchant_authentication(live_name, live_trans_key),
            "batchId": batch_id,
            "sorting": {"orderBy": "submitTimeUTC", "orderDescending": "true"},
            "paging": {"limit": "600", "offset": "1"},
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def get_settled_batch_list(start_date, end_date, live_name, live_trans_key, url):
    body = {
        "getSettledBatchListRequest": {
            "merchantAuthentication": merchant_authentication(live_name, live_trans_key),
            "firstSettlementDate": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "lastSettlementDate": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def charge_customer_profile(order_details, customer_profile_id, payment_profile_id, live_name, live_trans_key, url):
    body = {
        "createTransactionRequest": {
            "merchantAuthentication": merchant_authentication(live_name, live_trans_key),
            "refId": order_details['display_order_id'],
            "transactionRequest": {
                "transactionType": "authCaptureTransaction",
                "amount": order_details['amount'],
                "profile": {
                    "customerProfileId": customer_profile_id,
                    "paymentProfile": {"paymentProfileId": payment_profile_id},
                },
                "order": {"invoiceNumber": order_details['display_order_id']},
            },
        }
    }
    response = send_request(url, body)
    return handle_response(response)


def get_customer_profile_transactions(customer_profile_id, payment_profile_id, live_name, live_trans_key, url):
    body = {
        "getTransactionListForCustomerRequest": {
            "merchantAuthentication": merchant_authentication(live_name, live_trans_key),
            "customerProfileId": customer_profile_id,
            "customerPaymentProfileId": payment_profile_id,
            "sorting": {"orderBy": "submitTimeUTC", "orderDescending": False},
            "paging": {"limit": "100", "offset": "1"},
        }
    }
    response = send_request(url, body)
    return handle_response(response)


def verify_card(order_details, live_name, live_trans_key, url):
    jsonRequest = {
        "createTransactionRequest": {
            "merchantAuthentication": merchant_authentication(live_name, live_trans_key),
            "transactionRequest": {
                "transactionType": "authOnlyTransaction",
                "amount": round(decimal.Decimal(order_details['total_paid']), 2),
                "payment": {
                    "creditCard": {
                        "cardNumber": order_details['cardNumber'],
                        "expirationDate": order_details['expirationDate'],
                        "cardCode": order_details['cardCode'],
                    }
                },
                "billTo": {
                    "firstName": order_details['first_name'],
                    "lastName": order_details['last_name'],
                    "address": order_details['avs_street'],
                    "city": order_details['city'],
                    "state": order_details['state'],
                    "zip": order_details['zip'],
                    "country": "USA",
                },
                "processingOptions": {"isSubsequentAuth": "true"},
                "authorizationIndicatorType": {"authorizationIndicator": "pre"},
            },
        }
    }
    response = send_request(url, jsonRequest)
    return handle_response(response)


def charge_credit_card(order_details, live_name, live_trans_key, url, country="USA"):
    logger.info(f"Amount to be sent to authorize: {round(decimal.Decimal(order_details['total_paid']), 2)}")
    jsonRequest = {
        "createTransactionRequest": {
            "merchantAuthentication": merchant_authentication(live_name, live_trans_key),
            "transactionRequest": {
                "transactionType": "authCaptureTransaction",
                "amount": round(decimal.Decimal(order_details['total_paid']), 2),
                "currencyCode": "USD" if country == "USA" else "CAD",
                "payment": {
                    "creditCard": {
                        "cardNumber": order_details['cardNumber'],
                        "expirationDate": order_details['expirationDate'],
                        "cardCode": order_details['cardCode'],
                    }
                },
                "order": {
                    "invoiceNumber": order_details['display_order_id'],
                    "description": "Shipping containers purchased",
                },
                "lineItems": {"lineItem": [create_line_item(item) for item in order_details['line_items']]},
                "tax": {"amount": order_details['tax'], "name": "Taxes", "description": "Total taxes for order"},
                "shipping": {
                    "amount": order_details['shipping_revenue'],
                    "name": "Shipping",
                    "description": "Shipping",
                },
                "customer": {"type": "individual", "email": order_details['email']},
                "billTo": {
                    "firstName": order_details['first_name'],
                    "lastName": order_details['last_name'],
                    "address": order_details['avs_street'],
                    "city": order_details['city'],
                    "state": order_details['state'],
                    "zip": order_details['zip'],
                    "country": country,
                },
                "shipTo": {
                    "firstName": order_details['shipping_details']['first_name'],
                    "lastName": order_details['shipping_details']['last_name'],
                    "address": order_details['shipping_details']['street_address'],
                    "city": order_details['shipping_details']['city'],
                    "state": order_details['shipping_details']['state'],
                    "zip": order_details['shipping_details']['zip'],
                    "country": country,
                },
                "transactionSettings": {"setting": {"settingName": "duplicateWindow", "settingValue": 0}},
            },
        }
    }
    response = send_request(url, jsonRequest)
    return handle_response(response)


def get_transaction_detail(trans_id, live_key, trans_key, url):
    body = {
        "getTransactionDetailsRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "transId": trans_id,
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def update_customer_payment_profile(
    customer_profile_id, customer_payment_profile_id, order_details, live_key, trans_key, url
):
    body = {
        "updateCustomerPaymentProfileRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "customerProfileId": customer_profile_id,
            "paymentProfile": {
                "billTo": {
                    "firstName": order_details['first_name'],
                    "lastName": order_details['last_name'],
                    "address": order_details['street_address'],
                    "city": order_details['city'],
                    "state": order_details['state'],
                    "zip": order_details['zip'],
                    "country": "USA",
                },
                "payment": {
                    "creditCard": {
                        "cardNumber": order_details['card_number'],
                        "expirationDate": order_details['expiration_date'],
                        "cardCode": order_details['card_code'],
                    }
                },
                "customerPaymentProfileId": customer_payment_profile_id,
            },
            "validationMode": "liveMode",
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def update_customer_payment_profile_bank_account(
    customer_profile_id, customer_payment_profile_id, order_details, live_key, trans_key, url
):
    body = {
        "updateCustomerPaymentProfileRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "customerProfileId": customer_profile_id,
            "paymentProfile": {
                "billTo": {
                    "firstName": order_details['first_name'],
                    "lastName": order_details['last_name'],
                    "address": order_details['street_address'],
                    "city": order_details['city'],
                    "state": order_details['state'],
                    "zip": order_details['zip'],
                    "country": "USA",
                },
                "payment": {
                    "bankAccount": {
                        "routingNumber": order_details['routingNumber'],
                        "accountNumber": order_details['accountNumber'],
                        "nameOnAccount": order_details['bankName'],
                    }
                },
                "customerPaymentProfileId": customer_payment_profile_id,
            },
            "validationMode": "liveMode",
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def delete_payment_profile(customer_profile_id, customer_payment_profile_id, live_key, trans_key, url):
    body = {
        "deleteCustomerPaymentProfileRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "customerProfileId": customer_profile_id,
            "customerPaymentProfileId": customer_payment_profile_id,
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def remove_customer_profile(customer_profile_id, live_key, trans_key, url):
    body = {
        "deleteCustomerProfileRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "customerProfileId": customer_profile_id,
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def create_customer_payment_profile_general(customer_details, customer_profile_id, live_key, trans_key, url):
    body = {
        "createCustomerPaymentProfileRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "customerProfileId": customer_profile_id,
            "paymentProfile": {
                "billTo": {
                    "firstName": customer_details['first_name'],
                    "lastName": customer_details['last_name'],
                    "address": customer_details['street_address'],
                    "city": customer_details['city'],
                    "state": customer_details['state'],
                    "zip": customer_details['zip'],
                    "country": "USA",
                },
                "payment": {
                    "bankAccount": {
                        "routingNumber": customer_details['routingNumber'],
                        "accountNumber": customer_details['accountNumber'],
                        "nameOnAccount": customer_details['first_name'] + " " + customer_details['last_name'],
                    }
                },
                "defaultPaymentProfile": False,
            },
            "validationMode": "testMode",
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def create_customer_payment_profile(customer_details, customer_profile_id, live_key, trans_key, url):
    body = {
        "createCustomerPaymentProfileRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "customerProfileId": customer_profile_id,
            "paymentProfile": {
                "billTo": {
                    "firstName": customer_details['first_name'],
                    "lastName": customer_details['last_name'],
                    "address": customer_details['street_address'],
                    "city": customer_details['city'],
                    "state": customer_details['state'],
                    "zip": customer_details['zip'],
                    "country": "USA",
                },
                "payment": {
                    "creditCard": {
                        "cardNumber": customer_details['card_number'],
                        "expirationDate": customer_details['expiration_date'],
                        "cardCode": customer_details['card_code'],
                    }
                },
                "defaultPaymentProfile": False,
            },
            "validationMode": "testMode",
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def create_customer_profile(customer_details, live_key, trans_key, url):
    body = {
        "createCustomerProfileRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "profile": {
                "merchantCustomerId": str(customer_details["id"])[:20],
                "email": customer_details['email'],
                "paymentProfiles": {
                    "customerType": "individual",
                    "billTo": {
                        "firstName": customer_details['first_name'],
                        "lastName": customer_details['last_name'],
                        "address": customer_details['street_address'],
                        "city": customer_details['city'],
                        "state": customer_details['state'],
                        "zip": customer_details['zip'],
                        "country": "USA",
                    },
                    "payment": {
                        "creditCard": {
                            "cardNumber": customer_details['card_number'],
                            "expirationDate": customer_details['expiration_date'],
                            "cardCode": customer_details['card_code'],
                        }
                    },
                },
                "shipToList": {
                    "firstName": customer_details['shipping_details']['first_name'],
                    "lastName": customer_details['shipping_details']['last_name'],
                    "address": customer_details['shipping_details']['street_address'],
                    "city": customer_details['shipping_details']['city'],
                    "state": customer_details['shipping_details']['state'],
                    "zip": customer_details['shipping_details']['zip'],
                    "country": "USA",
                },
            },
            "validationMode": "testMode",
        }
    }

    if 'bankName' in customer_details:
        body['createCustomerProfileRequest']['profile']['paymentProfiles']['payment'] = {}
        payment = body['createCustomerProfileRequest']['profile']['paymentProfiles']['payment']
        payment['bankAccount'] = {}
        payment['bankAccount']['routingNumber'] = customer_details['routingNumber']
        payment['bankAccount']['accountNumber'] = customer_details['accountNumber']
        payment['bankAccount']['nameOnAccount'] = customer_details['first_name'] + " " + customer_details['last_name']

    response = send_request(url, body)
    return handle_response(response)


def get_customer_profile(customer_profile_id, live_key, trans_key, url):
    body = {
        "getCustomerProfileRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "customerProfileId": customer_profile_id,
            "includeIssuerInfo": "true",
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def create_subscription_from_customer_profile(
    customer_profile_id, customer_payment_profile_id, order_details, live_key, trans_key, url
):
    body = {
        "ARBCreateSubscriptionRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "refId": order_details['display_order_id'],
            "subscription": {
                "name": "Sample subscription",
                "paymentSchedule": {
                    "interval": {"length": "1", "unit": "months"},
                    "startDate": order_details['start_date'],
                    "totalOccurrences": order_details['total_occurrences'],
                    "trialOccurrences": order_details['trial_period'],
                },
                "amount": order_details['amount'],
                "trialAmount": order_details['trial_amount'],
                "profile": {
                    "customerProfileId": customer_profile_id,
                    "customerPaymentProfileId": customer_payment_profile_id,
                },
            },
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def create_subscription(order_details, live_key, trans_key, url):
    body = {
        "ARBCreateSubscriptionRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "refId": order_details['display_order_id'],
            "subscription": {
                "name": f"Subscription for {order_details['full_name']}",
                "paymentSchedule": {
                    "interval": {"length": "1", "unit": "months"},
                    "startDate": order_details['start_date'],
                    "totalOccurrences": order_details['total_occurrences'],
                    "trialOccurrences": order_details['trial_period'],
                },
                "amount": order_details['amount'],
                "trialAmount": order_details['trial_amount'],
                "payment": {
                    "creditCard": {
                        "cardNumber": order_details['cardNumber'],
                        "expirationDate": order_details['expirationDate'],
                    }
                },
                "billTo": {
                    "firstName": order_details['first_name'],
                    "lastName": order_details['last_name'],
                    "address": order_details['street_address'],
                    "city": order_details['city'],
                    "state": order_details['state'],
                    "zip": order_details['zip'],
                    "country": "USA",
                },
                "shipTo": {
                    "firstName": order_details['shipping_details']['first_name'],
                    "lastName": order_details['shipping_details']['last_name'],
                    "address": order_details['shipping_details']['street_address'],
                    "city": order_details['shipping_details']['city'],
                    "state": order_details['shipping_details']['state'],
                    "zip": order_details['shipping_details']['zip'],
                    "country": "USA",
                },
            },
        }
    }
    response = send_request(url, body)
    return handle_response(response)


def get_subscription(subscription_id, live_key, trans_key, url):
    body = {
        "ARBGetSubscriptionRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "subscriptionId": subscription_id,
            "includeTransactions": True,
        }
    }
    response = send_request(url, body)
    return handle_response(response)


def cancel_subscription(subscription_id, display_order_id, live_key, trans_key, url):
    body = {
        "ARBCancelSubscriptionRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "refId": display_order_id,
            "subscriptionId": subscription_id,
        }
    }
    response = send_request(url, body)
    return handle_response(response)


def get_subscription_status(subscription_id, live_key, trans_key, url):
    body = {
        "ARBGetSubscriptionStatusRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "subscriptionId": subscription_id,
        }
    }
    response = send_request(url, body)
    return handle_response(response)


def update_subscription_schedule(payment_schedule, order_details, live_key, trans_key, url):
    body = {
        "ARBUpdateSubscriptionRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "refId": order_details['display_order_id'],
            "subscriptionId": order_details['subscription_id'],
            "subscription": {"paymentSchedule": payment_schedule},
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def update_subscription_customer_profile(order_details, live_key, trans_key, url):
    body = {
        "ARBUpdateSubscriptionRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "refId": order_details['display_order_id'],
            "subscriptionId": order_details['subscription_id'],
            "subscription": {
                "profile": {
                    "customerProfileId": order_details['customer_profile_id'],
                    "customerPaymentProfileId": order_details['customer_payment_profile_id'],
                }
            },
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def update_subscription_amount(order_details, live_key, trans_key, url):
    body = {
        "ARBUpdateSubscriptionRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "refId": order_details['display_order_id'],
            "subscriptionId": order_details['subscription_id'],
            "subscription": {
                "amount": order_details['amount'],
            },
        }
    }

    response = send_request(url, body)
    return handle_response(response)


def update_subscription(order_details, live_key, trans_key, url):
    body = {
        "ARBUpdateSubscriptionRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "refId": order_details['display_order_id'],
            "subscriptionId": order_details['subscription_id'],
            "subscription": {
                "name": f"Subscription for {order_details['full_name']}",
                "paymentSchedule": {
                    "interval": {"length": "1", "unit": "months"},
                    "startDate": order_details['start_date'],
                    "totalOccurrences": order_details['total_occurrences'],
                    "trialOccurrences": order_details['trial_period'],
                },
                "amount": order_details['amount'],
                "trialAmount": order_details['trial_amount'],
                "payment": {
                    "creditCard": {
                        "cardNumber": order_details['cardNumber'],
                        "expirationDate": order_details['expirationDate'],
                    }
                },
                "billTo": {
                    "firstName": order_details['first_name'],
                    "lastName": order_details['last_name'],
                    "address": order_details['street_address'],
                    "city": order_details['city'],
                    "state": order_details['state'],
                    "zip": order_details['zip'],
                    "country": "USA",
                },
                "shipTo": {
                    "firstName": order_details['shipping_details']['first_name'],
                    "lastName": order_details['shipping_details']['last_name'],
                    "address": order_details['shipping_details']['street_address'],
                    "city": order_details['shipping_details']['city'],
                    "state": order_details['shipping_details']['state'],
                    "zip": order_details['shipping_details']['zip'],
                    "country": "USA",
                },
            },
        }
    }
    response = send_request(url, body)
    return handle_response(response)


def get_subscription_list(live_key, trans_key, url):
    body = {
        "ARBGetSubscriptionListRequest": {
            "merchantAuthentication": merchant_authentication(live_key, trans_key),
            "searchType": "subscriptionActive",
            "sorting": {"orderBy": "id", "orderDescending": "false"},
            "paging": {"limit": "1000", "offset": "1"},
        }
    }
    response = send_request(url, body)
    return handle_response(response)


async def handle_create_authorize_payment_profile_id(
    existing_order: Order, payment_info: dict, authorize_int: dict, account_id: int, is_autopay: bool = False
) -> int:
    """
    returns: Just created customer profile id
    """
    customer_profile_id: int = existing_order.customer_profile_id

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=existing_order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    customer_details = {
        "id": existing_order.display_order_id,
        "email": customer_info.get("email", ""),
        "first_name": payment_info["first_name"],
        "last_name": payment_info["last_name"],
        "street_address": payment_info["avs_street"],
        "city": payment_info["city"],
        "state": payment_info["state"],
        "zip": payment_info["zip"],
        "shipping_details": {
            "first_name": customer_info.get("first_name", ""),
            "last_name": customer_info.get("last_name", ""),
            "street_address": existing_order.address.street_address,
            "city": existing_order.address.city,
            "state": existing_order.address.state,
            "zip": existing_order.address.zip,
        },
    }

    is_all_bank_info_provided: bool = (
        payment_info.get('bank_name') is not None
        and payment_info.get('routing_number') is not None
        and payment_info.get('account_number') is not None
    )

    if is_all_bank_info_provided:
        customer_details['bankName'] = payment_info.get('bank_name')
        customer_details['routingNumber'] = payment_info.get('routing_number')
        customer_details['accountNumber'] = payment_info.get('account_number')

    logger.info(f"{existing_order.display_order_id} charge_rental create_customer_profile")

    # create credit card payment profile
    response = create_customer_payment_profile_general(
        customer_details,
        customer_profile_id,
        authorize_int["api_login_id"],
        authorize_int["transaction_key"],
        url=authorize_int["url"],
    )

    if response["messages"]["resultCode"] == 'Ok':
        logger.info(f"{existing_order.display_order_id} charge_rental create_customer_profile success")
    else:
        logger.error(
            f"{existing_order.display_order_id} create_customer__payment_profile"
            + response["messages"]["message"][0]['text']
        )
        raise Exception(response["messages"]["message"][0]['text'])


async def handle_create_authorize_payment_profile_id_credit_card(
    existing_order: Order, payment_info: dict, authorize_int: dict, account_id: int, is_autopay: bool = False
) -> int:
    """
    returns: Just created customer profile id
    """
    customer_profile_id: int = existing_order.customer_profile_id

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=existing_order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    customer_details = {
        "id": existing_order.display_order_id,
        "email": customer_info.get("email", ""),
        "card_number": payment_info["cardNumber"],
        "expiration_date": payment_info["expirationDate"],
        "card_code": payment_info["cardCode"],
        "first_name": payment_info["first_name"],
        "last_name": payment_info["last_name"],
        "street_address": payment_info["avs_street"],
        "city": payment_info["city"],
        "state": payment_info["state"],
        "zip": payment_info["zip"],
        "shipping_details": {
            "first_name": customer_info.get("first_name", ""),
            "last_name": customer_info.get("last_name", ""),
            "street_address": existing_order.address.street_address,
            "city": existing_order.address.city,
            "state": existing_order.address.state,
            "zip": existing_order.address.zip,
        },
    }

    # create credit card payment profile
    response = create_customer_payment_profile(
        customer_details,
        customer_profile_id,
        authorize_int["api_login_id"],
        authorize_int["transaction_key"],
        url=authorize_int["url"],
    )

    if response["messages"]["resultCode"] == 'Ok':
        logger.info(f"{existing_order.display_order_id} charge_rental create_customer_profile success")
    else:
        logger.error(
            f"{existing_order.display_order_id} charge_rental create_customer_profile"
            + response["messages"]["message"][0]['text']
        )
        raise Exception(response["messages"]["message"][0]['text'])


async def handle_create_authorize_customer_profile_id(
    existing_order: Order, payment_info: dict, authorize_int: dict, account_id: int, is_autopay: bool = False
) -> int:
    """
    returns: Just created customer profile id
    """
    customer_profile_id: int
    customer_profile_response = {}

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=existing_order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    customer_details = {
        "id": existing_order.display_order_id,
        "email": customer_info.get("email", ""),
        "card_number": payment_info["cardNumber"],
        "expiration_date": payment_info["expirationDate"],
        "card_code": payment_info["cardCode"],
        "first_name": payment_info["first_name"],
        "last_name": payment_info["last_name"],
        "street_address": payment_info["avs_street"],
        "city": payment_info["city"],
        "state": payment_info["state"],
        "zip": payment_info["zip"],
        "shipping_details": {
            "first_name": customer_info.get("first_name", ""),
            "last_name": customer_info.get("last_name", ""),
            "street_address": existing_order.address.street_address,
            "city": existing_order.address.city,
            "state": existing_order.address.state,
            "zip": existing_order.address.zip,
        },
    }

    is_all_bank_info_provided: bool = (
        payment_info.get('bank_name') is not None
        and payment_info.get('routing_number') is not None
        and payment_info.get('account_number') is not None
    )

    if is_all_bank_info_provided:
        customer_details['bankName'] = payment_info.get('bank_name')
        customer_details['routingNumber'] = payment_info.get('routing_number')
        customer_details['accountNumber'] = payment_info.get('account_number')

    logger.info(f"{existing_order.display_order_id} charge_rental create_customer_profile")

    has_2_payment_methods = False
    if payment_info.get('cardNumber') and payment_info.get("bank_name"):
        has_2_payment_methods = True

    # if it has 2 payment methods, it creates a customer profile with ACH payment method
    # if it has 1 payment methods, it creates credit card of ACH customer profile with 1 payment method
    customer_profile_response = create_customer_profile(
        customer_details,
        authorize_int["api_login_id"],
        authorize_int["transaction_key"],
        url=authorize_int["url"],
    )

    if customer_profile_response["messages"]["resultCode"] == 'Ok':
        if has_2_payment_methods:
            customer_profile_id = int(customer_profile_response["customerProfileId"])

            # create credit card payment profile
            response = create_customer_payment_profile(
                customer_details,
                customer_profile_id,
                authorize_int["api_login_id"],
                authorize_int["transaction_key"],
                url=authorize_int["url"],
            )

            if response["messages"]["resultCode"] != 'Ok':
                await note_crud.create(
                    NoteInSchema(
                        title="Authorize error signing contract",
                        content=str(response["messages"]["message"][0]['text']),
                        author_id=existing_order.user.id,
                        order_id=existing_order.id,
                    )
                )

    if customer_profile_response["messages"]["resultCode"] == 'Ok':
        logger.info(f"{existing_order.display_order_id} charge_rental create_customer_profile success")
        customer_profile_id = int(customer_profile_response["customerProfileId"])
    elif 'duplicate' in customer_profile_response["messages"]["message"][0]['text']:
        # It only gets here if the previous request failed and a customer profile was already created.
        error_message = customer_profile_response["messages"]["message"][0]['text']
        customer_profile_id = extract_integers_from_string(error_message)[0]
        # customer_profile = get_customer_profile(
        #     customer_profile_id,
        #     authorize_int["api_login_id"],
        #     authorize_int["transaction_key"],
        #     url=authorize_int["url"],
        # )
    else:
        await note_crud.create(
            NoteInSchema(
                title="Authorize error signing contract",
                content=str(customer_profile_response["messages"]["message"][0]['text']),
                author_id=existing_order.user.id,
                order_id=existing_order.id,
            )
        )
        # Try credit card if ACH failed
        if has_2_payment_methods:
            del customer_details['bankName']
            customer_profile_response = create_customer_profile(
                customer_details,
                authorize_int["api_login_id"],
                authorize_int["transaction_key"],
                url=authorize_int["url"],
            )

            if customer_profile_response["messages"]["resultCode"] == 'Ok':
                logger.info(f"{existing_order.display_order_id} charge_rental create_customer_profile success")
                customer_profile_id = int(customer_profile_response["customerProfileId"])
            elif 'duplicate' in customer_profile_response["messages"]["message"][0]['text']:
                # It only gets here if the previous request failed and a customer profile was already created.
                error_message = customer_profile_response["messages"]["message"][0]['text']
                customer_profile_id = extract_integers_from_string(error_message)[0]
            else:
                await note_crud.create(
                    NoteInSchema(
                        title="Authorize error signing contract",
                        content=str(customer_profile_response["messages"]["message"][0]['text']),
                        author_id=existing_order.user.id,
                        order_id=existing_order.id,
                    )
                )
                logger.error(
                    f"{existing_order.display_order_id} charge_rental create_customer_profile"
                    + customer_profile_response["messages"]["message"][0]['text']
                )
                raise Exception(customer_profile_response["messages"]["message"][0]['text'])
        else:
            logger.error(
                f"{existing_order.display_order_id} charge_rental create_customer_profile"
                + customer_profile_response["messages"]["message"][0]['text']
            )
            raise Exception(customer_profile_response["messages"]["message"][0]['text'])

    order_update_dict: dict = {
        "account_id": existing_order.account_id,
        "user_id": existing_order.user.id,
        "customer_profile_id": customer_profile_id,
    }

    if is_autopay:
        if not payment_info.get('not_start_autopay', False):
            order_update_dict["is_autopay"] = is_autopay

    await order_crud.update(
        account_id,
        payment_info['order_id'],
        OrderInUpdate(**order_update_dict),
    )

    return customer_profile_id
