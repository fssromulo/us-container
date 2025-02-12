# Python imports
import json
from datetime import date, datetime
from decimal import Decimal

# Pip imports
import requests
from loguru import logger
from pydantic import BaseModel  # type: ignore

# Internal imports
from src.schemas.orders import Receipt
from src.schemas.rental_statement import RentalStatement, RentalStatementMultipleOrders


def _format_number_as_currency(number):
    """Format number as currency"""
    if number is None:
        return f"${0:,.2f}"
    return f"${number:,.2f}"


# Custom JSON Encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle Pydantic models
        if isinstance(obj, BaseModel):
            return obj.dict()  # Convert Pydantic model to dictionary

        # Handle Decimal objects
        if isinstance(obj, Decimal):
            return float(obj)

        # Handle datetime and date objects
        if isinstance(obj, (datetime, date)):
            return obj.strftime("%m/%d/%y")

        # Default behavior
        return super().default(obj)

class PdfGeneratorRentalStatementMultipleOrders:
    BASE_URL = "https://api.docugenerate.com/v1"
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(
        self,
        api_key=None,
        statement=None,
    ):
        """Object constructor for PdfGeneratorPurchaseInvoice"""
        self.statement: RentalStatementMultipleOrders = statement
        self.api_key = api_key

    def _to_dict(self):
        """
        Parsing the object as JSON string
        """
        object_dict = self.statement.__dict__.copy()
        object_dict['api_key'] = self.api_key
        return object_dict

    async def download(self):
        """Send the request and return the content"""
        param_dict = self._to_dict()
        headers = {
            'Authorization': f"{self.api_key}",
            'Content-Type': 'application/json',
        }

        name = f"{self.statement.account_name}_{self.statement.title}"

        request_data = {
            "template_id": "OE1NKFx1QYU6Ju6kjUUZ",
            "data": param_dict,
            "name": name,
            "output_format": ".pdf",
            "output_quality": 100,
            "single_file": True,
            "page_break": True,
        }
        logger.info(param_dict)

        # Use the custom encoder when converting to JSON
        string_data = json.dumps(request_data, cls=CustomJSONEncoder)
        response = requests.post(f"{self.BASE_URL}/document", data=string_data, headers=headers)
        json_response = response.json()
        return json_response.get("document_uri")


class PdfGeneratorRentalStatement:
    BASE_URL = "https://api.docugenerate.com/v1"
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(
        self,
        api_key=None,
        statement=None,
    ):
        """Object constructor for PdfGeneratorPurchaseInvoice"""
        self.statement: RentalStatement = statement
        self.api_key = api_key

    def _to_dict(self):
        """
        Parsing the object as JSON string
        """
        object_dict = self.statement.__dict__.copy()
        object_dict['api_key'] = self.api_key
        return object_dict

    async def download(self):
        """Send the request and return the content"""
        param_dict = self._to_dict()
        headers = {
            'Authorization': f"{self.api_key}",
            'Content-Type': 'application/json',
        }

        name = f"{self.statement.account_name}_{self.statement.title}"

        request_data = {
            "template_id": "91ZCsrx8QboLeqEkpZAN",
            "data": param_dict,
            "name": name,
            "output_format": ".pdf",
            "output_quality": 100,
            "single_file": True,
            "page_break": True,
        }
        logger.info(param_dict)

        # Use the custom encoder when converting to JSON
        string_data = json.dumps(request_data, cls=CustomJSONEncoder)
        response = requests.post(f"{self.BASE_URL}/document", data=string_data, headers=headers)
        json_response = response.json()
        return json_response.get("document_uri")


class PdfGeneratorRentalReceipt:
    BASE_URL = "https://api.docugenerate.com/v1"
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(
        self,
        api_key=None,
        logo=None,
        title="Invoice",
        receipt=None,
    ):
        """Object constructor for PdfGeneratorPurchaseInvoice"""
        self.receipt: Receipt = receipt
        self.api_key = api_key
        self.logo = logo
        self.title = title

    def _to_dict(self):
        """
        Parsing the object as JSON string
        """
        object_dict = self.receipt.__dict__.copy()
        object_dict['api_key'] = self.api_key
        object_dict['logo'] = self.logo
        object_dict['title'] = self.title
        return object_dict

    async def download(self):
        """Send the request and return the content"""
        param_dict = self._to_dict()
        headers = {
            'Authorization': f"{self.api_key}",
            'Content-Type': 'application/json',
        }

        name = f"{self.receipt.customer_name}_{self.title}"

        request_data = {
            "template_id": "Rz4bGg09eIU2oDucNglA",
            "data": param_dict,
            "name": name,
            "output_format": ".pdf",
            "output_quality": 100,
            "single_file": True,
            "page_break": True,
        }
        logger.info(param_dict)

        # Use the custom encoder when converting to JSON
        string_data = json.dumps(request_data, cls=CustomJSONEncoder)
        response = requests.post(f"{self.BASE_URL}/document", data=string_data, headers=headers)
        json_response = response.json()
        return json_response.get("document_uri")


class PdfGeneratorPurchaseInvoice:
    BASE_URL = "https://api.docugenerate.com/v1"
    DATE_FORMAT = "%m/%d/%y"

    def __init__(
        self,
        api_key=None,
        logo=None,
        title="Invoice",
        order_id=None,
        created_on=None,
        due_date=None,
        po_num=None,
        po_job_id=None,
        balance_due=None,
        company_name=None,
        company_street=None,
        company_city_state_zip=None,
        company_phone=None,
        customer_name=None,
        customer_billing_street=None,
        customer_billing_city_state_zip=None,
        delivery_address=None,
        sub_total=None,
        tax=None,
        total=None,
        total_paid=None,
        transactions_present=False,
        transactions=None,
        main_notes=None,
        additional_notes=None,
        items=None,
    ):
        """Object constructor for PdfGeneratorPurchaseInvoice"""
        self.api_key = api_key
        self.logo = logo
        self.title = title
        self.order_id = order_id
        self.created_on = datetime.fromisoformat(str(created_on)) if created_on else None
        self.due_date = datetime.fromisoformat(str(due_date)) if due_date else None
        self.po_num = po_num
        self.po_job_id = po_job_id
        self.balance_due = _format_number_as_currency(balance_due)
        self.company_name = company_name
        self.company_street = company_street
        self.company_city_state_zip = company_city_state_zip
        self.company_phone = company_phone
        self.customer_name = customer_name
        self.customer_billing_street = customer_billing_street
        self.customer_billing_city_state_zip = customer_billing_city_state_zip
        self.delivery_address = delivery_address
        self.sub_total = _format_number_as_currency(sub_total)
        self.tax = _format_number_as_currency(tax)
        self.total = _format_number_as_currency(total)
        self.total_paid = _format_number_as_currency(total_paid)
        self.transactions_present = transactions_present
        self.transactions = [Transaction(**transaction) for transaction in transactions] if transactions else []
        self.main_notes = main_notes
        self.additional_notes = additional_notes
        self.items = [Item(**item) for item in items] if items else []

    def _to_dict(self):
        """
        Parsing the object as JSON string
        """
        object_dict = self.__dict__.copy()

        # Handling date formatting
        object_dict['created_on'] = self.created_on.strftime(self.DATE_FORMAT) if self.created_on else None
        object_dict['due_date'] = self.due_date.strftime(self.DATE_FORMAT) if self.due_date else None

        # Convert items and transactions to dict
        object_dict['items'] = [item.__dict__ for item in self.items]
        object_dict['transactions'] = [transaction.__dict__ for transaction in self.transactions]

        return object_dict

    def add_item(self, name=None, quantity=0, unit_cost=0.0, description=None):
        """Add item to the invoice"""
        self.items.append(Item(name=name, quantity=quantity, unit_cost=unit_cost, description=description))

    async def download(self):
        """Send the request and return the content"""
        param_dict = self._to_dict()
        headers = {
            'Authorization': f"{self.api_key}",
            'Content-Type': 'application/json',
        }

        name = f"{self.order_id}_{self.title}"

        request_data = {
            "template_id": "Bk3wgrHMdrKFjDrFY13f",
            "data": param_dict,
            "name": name,
            "output_format": ".pdf",
            "output_quality": 100,
            "single_file": True,
            "page_break": True,
        }
        logger.info(param_dict)

        # Use the custom encoder when converting to JSON
        string_data = json.dumps(request_data, cls=CustomJSONEncoder)
        response = requests.post(f"{self.BASE_URL}/document", data=string_data, headers=headers, timeout=10)
        logger.info(response.status_code)
        json_response = response.json()
        logger.info(json_response)
        return json_response.get("document_uri")


class PdfGeneratorRentalInvoice:
    BASE_URL = "https://api.docugenerate.com/v1"
    DATE_FORMAT = "%m/%d/%y"

    def __init__(
        self,
        api_key=None,
        logo=None,
        title="Invoice",
        order_id=None,
        created_on=None,
        due_date=None,
        po_num=None,
        po_job_id=None,
        balance_due=None,
        company_name=None,
        company_street=None,
        company_city_state_zip=None,
        company_phone=None,
        customer_name=None,
        customer_billing_street=None,
        customer_billing_city_state_zip=None,
        delivery_address=None,
        sub_total=None,
        tax=None,
        total=None,
        total_paid=None,
        main_notes=None,
        additional_notes=None,
        current_due=None,
        line_items=None,
        visible_columns=None,
        column_title=None,
        subtotals=None,
        paid_on_txt=None,
        order_dates=None,
    ):
        """Object constructor for PdfGeneratorPurchaseInvoice"""
        self.api_key = api_key
        self.logo = logo
        self.title = title
        self.order_id = order_id
        self.created_on = datetime.fromisoformat(str(created_on)) if created_on else None
        self.due_date = datetime.fromisoformat(str(due_date)) if due_date else None
        self.po_num = po_num
        self.po_job_id = po_job_id
        self.balance_due = _format_number_as_currency(balance_due)
        self.company_name = company_name
        self.company_street = company_street
        self.company_city_state_zip = company_city_state_zip
        self.company_phone = company_phone
        self.customer_name = customer_name
        self.customer_billing_street = customer_billing_street
        self.customer_billing_city_state_zip = customer_billing_city_state_zip
        self.delivery_address = delivery_address
        self.sub_total = _format_number_as_currency(sub_total)
        self.tax = _format_number_as_currency(tax)
        self.total = _format_number_as_currency(total)
        self.total_paid = _format_number_as_currency(total_paid)
        self.main_notes = main_notes
        self.additional_notes = additional_notes
        self.current_due = current_due
        self.line_items = line_items
        self.column_title = column_title
        self.visible_columns = visible_columns
        self.subtotals = subtotals
        self.paid_on_txt = paid_on_txt
        self.order_dates = order_dates

    def _to_dict(self):
        """
        Parsing the object as JSON string
        """
        object_dict = self.__dict__.copy()

        # Handling date formatting
        object_dict['created_on'] = self.created_on.strftime(self.DATE_FORMAT) if self.created_on else None
        object_dict['due_date'] = self.due_date.strftime(self.DATE_FORMAT) if self.due_date else None

        return object_dict

    async def download(self):
        """Send the request and return the content"""
        param_dict = self._to_dict()
        headers = {
            'Authorization': f"{self.api_key}",
            'Content-Type': 'application/json',
        }

        name = f"{self.order_id}_{self.title}"

        request_data = {
            "template_id": "T9sVRQm2ZzcOk2Twp06I",
            "data": param_dict,
            "name": name,
            "output_format": ".pdf",
            "output_quality": 100,
            "single_file": True,
            "page_break": True,
        }
        logger.info(param_dict)

        # Use the custom encoder when converting to JSON
        string_data = json.dumps(request_data, cls=CustomJSONEncoder)
        response = requests.post(f"{self.BASE_URL}/document", data=string_data, headers=headers, timeout=10)
        logger.info(response.status_code)
        json_response = response.json()
        logger.info(json_response)
        return json_response.get("document_uri", "")


class Item:
    """Item object for an invoice"""

    def __init__(self, name, quantity, unit_cost, description=""):
        """Object constructor"""
        self.name = name
        self.quantity = quantity
        self.price = _format_number_as_currency(unit_cost)
        self.amount = _format_number_as_currency(unit_cost)


class Transaction:
    """Transaction object for payments"""

    def __init__(self, name, date, notes, amount):
        """Object constructor for Transaction"""
        self.name = name
        self.date = datetime.fromisoformat(str(date)) if date else None
        self.notes = notes
        self.amount = _format_number_as_currency(amount)
