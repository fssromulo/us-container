# Python imports
import decimal
import json
import urllib.parse

# Pip imports
import requests
from loguru import logger


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)


class GwApi:
    def __init__(self):
        self.login = {}
        self.order = {}
        self.billing = {}
        self.shipping = {}
        self.responses = {}

    def set_login(self, security_key):
        self.login['security_key'] = security_key

    def set_order(self, orderid, orderdescription, tax, shipping, ponumber, ipaddress):
        self.order['orderid'] = orderid
        self.order['orderdescription'] = orderdescription
        self.order['shipping'] = '{0:.2f}'.format(float(shipping))
        self.order['ipaddress'] = ipaddress
        self.order['tax'] = '{0:.2f}'.format(float(tax))
        self.order['ponumber'] = ponumber

    def set_billing(
        self, firstname, lastname, company, address1, address2, city, state, zip, country, phone, fax, email, website
    ):
        self.billing['firstname'] = firstname
        self.billing['lastname'] = lastname
        self.billing['company'] = company
        self.billing['address1'] = address1
        self.billing['address2'] = address2
        self.billing['city'] = city
        self.billing['state'] = state
        self.billing['zip'] = zip
        self.billing['country'] = country
        self.billing['phone'] = phone
        self.billing['fax'] = fax
        self.billing['email'] = email
        self.billing['website'] = website

    def set_shipping(self, firstname, lastname, company, address1, address2, city, state, zipcode, country, email):
        self.shipping['shipping_firstname'] = firstname
        self.shipping['shipping_lastname'] = lastname
        self.shipping['shipping_company'] = company
        self.shipping['shipping_address1'] = address1
        self.shipping['shipping_address2'] = address2
        self.shipping['shipping_city'] = city
        self.shipping['shipping_state'] = state
        self.shipping['shipping_zip'] = zipcode
        self.shipping['shipping_country'] = country
        self.shipping['shipping_email'] = email

    def do_sale(self, amount, ccnumber, ccexp, cvv=''):
        query = {
            'security_key': self.login['security_key'],
            'ccnumber': ccnumber,
            'ccexp': ccexp,
            'amount': '{0:.2f}'.format(float(amount)),
            'type': 'sale',
        }
        if cvv:
            query['cvv'] = cvv

        query.update(self.order)
        query.update(self.billing)
        query.update(self.shipping)

        encoded_query = urllib.parse.urlencode(query)
        return self.do_post(encoded_query)

    def do_post(self, query):
        url = "https://noomerik.transactiongateway.com/api/transact.php"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=query, headers=headers, timeout=30)
        response_data = urllib.parse.parse_qs(response.text)
        for key, value in response_data.items():
            self.responses[key] = value[0]
        return response_data


def charge_credit_card(order_details, live_trans_key):
    logger.info(f"Amount to be sent to noomerik: {round(decimal.Decimal(order_details['total_paid']), 2)}")
    gw = GwApi()

    gw.set_login(live_trans_key)
    gw.set_billing(
        order_details['first_name'],
        order_details['last_name'],
        "",
        order_details['avs_street'],
        "",
        order_details['city'],
        order_details['state'],
        order_details['zip'],
        "US",
        "",
        "",
        order_details['email'],
        "",
    )
    gw.set_shipping(
        order_details['first_name'],
        order_details['last_name'],
        "",
        order_details['shipping_details']['street_address'],
        "",
        order_details['shipping_details']['city'],
        order_details['shipping_details']['state'],
        order_details['shipping_details']['zip'],
        "US",
        order_details['email'],
    )
    gw.set_order(
        order_details['display_order_id'],
        "Shipping containers purchased",
        order_details['tax'],
        order_details['shipping_revenue'],
        "",
        "",
    )
    response = gw.do_sale(
        round(decimal.Decimal(order_details['total_paid']), 2),
        order_details['cardNumber'],
        order_details['expirationDate'],
        order_details['cardCode'],
    )
    logger.info(f"Response from noomerik: {response}")

    if response['response_code'][0] == '100':
        response['success'] = True
        response["transactionResponse"] = {"messages": [{"description": "This transaction has been approved."}]}
    else:
        response['errorMessage'] = response['responsetext'][0]
        response["transactionResponse"] = {"messages": [{"description": response['errorMessage']}]}

    return response
