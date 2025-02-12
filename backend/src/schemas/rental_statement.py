# Python imports
from typing import List, Optional, Dict,Any
from decimal import Decimal

# Pip imports
from pydantic import BaseModel


class BillTo(BaseModel):
    customer_name: Optional[str]
    bill_address: Optional[str]
    bill_city_state_zip: Optional[str]


class ContainerInfo(BaseModel):
    title: Optional[str]
    container_number: Optional[str]
    location: Optional[str]
    date_out: Optional[str]

class RentInfo(BaseModel):
    amount_due: Optional[str]
    start_date: Optional[str]
    paid_thru: Optional[str]
    date_out: Optional[str]


class RentHistory(BaseModel):
    date: Optional[str]
    description: Optional[str]
    amount: Optional[str]
    tax: Optional[str]
    status: Optional[str]
    filterable_date: Optional[str]


class RentalStatement(BaseModel):
    logo: Optional[str]
    title: Optional[str]
    account_name: Optional[str]
    customer_orders: Optional[str]
    account_street: Optional[str]
    account_city_state_zip: Optional[str]
    po_num: Optional[str]
    account_main_phone: Optional[str]
    po_job_id: Optional[str]
    current_balance: Optional[str]
    bill_to: Optional[BillTo]
    auto_pay_message: Optional[str]
    status: Optional[str]
    container_info: List[ContainerInfo] = []
    rent_info: Optional[RentInfo]
    rent_history: List[RentHistory] = []
    notes: Optional[str]
    customer_name: Optional[str]
    bill_address: Optional[str]
    bill_city_state_zip: Optional[str]
    last_card_digits: Optional[str]

class RentalStatementMultipleOrders(BaseModel):
    logo: str   
    title: str
    account_name: str
    account_street: str
    account_city_state_zip: str
    account_main_phone: str
    orders_details_list: List[Dict[Any, Any]]
    customer_name: str
    bill_address: str
    current_balance: Decimal
    global_status: str    