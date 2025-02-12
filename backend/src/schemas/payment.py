# Python imports
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

# Pip imports
from pydantic import BaseModel

# Internal imports
from src.schemas.orders import CreateOrder


class CreditCardObj(BaseModel):
    first_name: str
    last_name: str
    zip: str
    avs_street: str
    city: str
    state: str
    cardNumber: Optional[str]
    expirationDate: Optional[str]
    cardCode: Optional[str]
    merchant_name: Optional[str]
    type: Optional[str]
    order_id: Optional[str]
    bank_name: Optional[str]
    account_number: Optional[str]
    routing_number: Optional[str]


class Payment(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    zip: Optional[str]
    avs_street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    cardNumber: Optional[str]
    expirationDate: Optional[str]
    cardCode: Optional[str]
    total_paid: Decimal
    order_id: Optional[str]
    display_order_id: Optional[str]
    convenience_fee_total: Decimal
    merchant_name: Optional[str]
    type: Optional[str]
    rent_due_on_day: Optional[int]
    rent_period_ids: Optional[List[str]]
    rent_period_paid_amt: Optional[Decimal]
    rent_period_tax_paid_amt: Optional[Decimal]
    rent_period_fee_paid_amt: Optional[Decimal]
    pay_with_customer_profile: Optional[bool]
    not_start_autopay: Optional[bool]
    autopay_day: Optional[int]
    card_pointe_token: Optional[str]
    transaction_created_at: Optional[str]

class QuickSalePayObj(BaseModel):
    credit_card: Optional[Payment]
    other_amt: Optional[Decimal]


class QuickSaleFee(BaseModel):
    fee: Optional[Decimal]
    fee_type: Optional[str]


class QuickSaleMiscCost(BaseModel):
    misc: Optional[Decimal]
    misc_type: Optional[str]


class QuickSaleLineItem(BaseModel):
    price: Optional[Decimal]
    shipping: Optional[Decimal]
    shipping_cost: Optional[Decimal]
    inventory_id: Optional[str]
    tax: Optional[str]
    attributes: Optional[dict]
    condition: Optional[str]
    container_size: Optional[str]
    product_state: Optional[str]
    product_id: Optional[str]
    door_orientation: Optional[str]
    product_city: Optional[str]


class QuickRentLineItem(BaseModel):
    price: Optional[Decimal]
    shipping: Optional[Decimal]
    pickup: Optional[Decimal]
    monthly_owed: Optional[Decimal]
    shipping_cost: Optional[Decimal]
    inventory_id: Optional[str]
    tax: Optional[str]
    attributes: Optional[dict]
    condition: Optional[str]
    container_size: Optional[str]
    product_city: Optional[str]
    product_state: Optional[str]
    product_id: Optional[str]
    door_orientation: Optional[str]


class QuickSalePayment(BaseModel):
    customer_id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    company_name: Optional[str]
    zip: Optional[str]
    street_address: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    state: Optional[str]
    county: Optional[str]
    billing_zip: Optional[str]
    billing_street_address: Optional[str]
    billing_city: Optional[str]
    billing_state: Optional[str]
    billing_county: Optional[str]
    total_paid: Optional[Decimal]
    convenience_fee_total: Optional[Decimal]
    type: Optional[str]
    line_items: List[QuickSaleLineItem]
    order: Optional[CreateOrder]
    payment: Optional[QuickSalePayObj]
    misc_costs: List[QuickSaleMiscCost]
    fees: List[QuickSaleFee]
    create_unpaid_order: Optional[bool]
    tax_exempt: bool
    single_customer_id: Optional[str]


class QuickRent(BaseModel):
    customer_id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    company_name: Optional[str]
    zip: Optional[str]
    street_address: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    state: Optional[str]
    county: Optional[str]
    billing_zip: Optional[str]
    billing_street_address: Optional[str]
    billing_city: Optional[str]
    billing_state: Optional[str]
    billing_county: Optional[str]
    total_paid: Optional[Decimal]
    convenience_fee_total: Optional[Decimal]
    type: Optional[str]
    line_items: List[QuickRentLineItem]
    order: Optional[CreateOrder]
    payment: Optional[QuickSalePayObj]
    misc_costs: List[QuickSaleMiscCost]
    fees: List[QuickSaleFee]
    started_on: Optional[str]
    ended_on: Optional[str]
    tax_exempt: bool
    note: Optional[str]
    single_customer_id: Optional[str]


class OtherPayment(BaseModel):
    order_id: str
    lump_sum_amount: Optional[Decimal]  # This will be populated if it is just a lump sum payment
    purchase_pay_amt: Optional[Decimal]
    rent_period_paid_amt: Optional[Decimal]
    rent_period_fee_paid_amt: Optional[Decimal]
    rent_period_tax_paid_amt: Optional[Decimal]
    rent_period_ids: Optional[List[str]]  # This will only be added if it is paying down a single rent period
    rent_due_on_day: Optional[int]
    has_ach: Optional[bool]
    use_ach_on_file: Optional[bool]
    start_date: Optional[datetime]
    past_periods_amt: Optional[
        Decimal
    ]  # This will be populated if it is a quick rental and the start period is in the past
    payment_option: Optional[
        str
    ]  # This will be populated if we have payment option set and can be only Total Balance (When we are paying of the total balance) Or Fees (When we are paying of fees)
    payment_type: Optional[str]
    notes: Optional[str]
    transaction_created_at: Optional[str]


class DeleteCustomerProfile(BaseModel):
    order_id: str


class DeleteCustomerPaymentProfile(BaseModel):
    order_id: str
    type: str
