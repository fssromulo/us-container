# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union
from uuid import UUID
import pytz
from loguru import logger

# Pip imports
import pytz
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.order_address import OrderAddress
from src.database.models.orders.order import Order
from src.database.models.orders.purchase_types import PurchaseTypes
from src.database.models.orders_status import OrderStatus
from src.database.models.payment_options import PaymentOptions
from src.schemas.fee import UpdateFee
from src.schemas.line_items import CreateLineItem, UpdateLineItem
from src.schemas.misc_cost import UpdateMiscCost
from src.schemas.notes import UpdateNote


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


class CreateUpdateAddress(BaseModel):
    street_address: Optional[str]
    zip: Optional[str]
    state: Optional[str]
    city: Optional[str]
    email: Optional[str]
    county: Optional[str]


class PaymentOrder(BaseModel):
    payment_amount: Optional[float]


class UpdateOrder(BaseModel):
    display_order_id: Optional[str]
    address: Optional[CreateUpdateAddress]
    paid_at: Optional[datetime]
    completed_at: Optional[datetime]
    delivered_at: Optional[datetime]
    payment_type: Optional[PaymentOptions]
    remaining_balance: Optional[Decimal]
    sub_total_price: Optional[Decimal]
    total_price: Optional[Decimal]
    order_type: Optional[PurchaseTypes]
    status: Optional[str]
    is_discount_applied: Optional[bool]
    note: Optional[UpdateNote]
    user_id: Optional[str]
    line_items: Optional[List[UpdateLineItem]]
    misc_cost: Optional[List[UpdateMiscCost]]
    calculated_order_tax: Optional[Decimal]
    allow_external_payments: Optional[bool]
    fees: Optional[List[UpdateFee]]
    has_delivery_date_set: Optional[bool]
    customer_application_schema_id: Optional[str]
    amount_paid: Optional[Decimal]
    payment_strategy: Optional[str]
    payment_option: Optional[str]
    transaction_type_id: Optional[str]
    override_distribution: Optional[bool]
    fees_to_be_paid: Optional[Decimal]
    subtotal_to_be_paid: Optional[Decimal]
    tax_to_be_paid: Optional[Decimal]

    class Config:
        extra = 'allow'


class CreateOrder(BaseModel):
    remaining_balance: Optional[Decimal]
    address: Optional[CreateUpdateAddress]
    billing_address: Optional[CreateUpdateAddress]
    sub_total_price: Optional[Decimal]
    total_price: Optional[Decimal]
    type: Optional[PurchaseTypes]
    note: Optional[UpdateNote]
    attributes: Optional[Dict]
    line_items: Optional[List[CreateLineItem]]
    status: Optional[OrderStatus]
    delivered_at: Optional[datetime]
    ended_on: Optional[datetime]
    pick_up_paid: Optional[bool]
    paid_at: Optional[datetime]
    payment_type: Optional[PaymentOptions]
    tax: Optional[Decimal]
    rent_due_on_day: Optional[int]
    payment_notes: Optional[str]
    first_payment_strategy: Optional[str]
    campaign_url: Optional[str]
    referral_source: Optional[str]
    tax_exempt: Optional[bool]
    overridden_user_id: Optional[str]
    message_type: Optional[str]


OrderIn = pydantic_model_creator(
    Order,
    name="OrderIn",
    exclude=(
        "id",
        "created_at",
        "modified_at",
        "paid_at",
        "completed_at",
        "customer",
        "line_items",
        "account",
    ),
    exclude_readonly=True,
    config_class=Config,
)

OrderAddressIn = pydantic_model_creator(OrderAddress, name="OrderAddressIn", exclude_readonly=True, config_class=Config)

OrderAddressOut = pydantic_model_creator(OrderAddress, name="OrderAddressOut")

OrderInUpdate = pydantic_model_creator(
    cls=Order,
    name="OrderInUpdate",
    exclude=(
        "id",
        "created_at",
        "modified_at",
        "customer",
        "line_items",
        "account",
        "display_order_id",
        "customer_id",
        "address_id",
    ),
    exclude_readonly=True,
)

OrderInUpdateStrict = pydantic_model_creator(
    Order,
    name="OrderInUpdateStrict",
    exclude=(
        "id",
        "created_at",
        "modified_at",
        "customer",
        "line_items",
        "account",
        "display_order_id",
        "address_id",
    ),
    exclude_readonly=True,
)


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


OrderOut = pydantic_model_creator(
    cls=Order,
    name="OrderOut",
    exclude=(
        "account",
        "customer.account",
        "customer.account_id",
        "user.account",
        "user.team_member_of",
        "user.team_members",
    ),
    # config_class=Config,
    # exclude_readonly=True
)

ExportedOrderOut = pydantic_model_creator(
    Order,
    name="ExportedOrderOut",
    exclude=(
        "account",
        "customer.account",
        "customer.account_id",
        "user.account",
        "user.team_member_of",
        "user.team_members",
        "user.preferences",
        "user.rental_preferences",
        "user.transactions",
        "user.created_at",
        "user.modified_at",
        "user.assistant",
        "user.role_id",
        "user.is_active",
        "fees",
        "modified_at",
        "coming_from",
        "billing_address",
        "customer_application_schema",
        "leadconnect_sent",
        "first_payment_strategy",
        "primary_payment_method",
        "pod_sign_page_url",
        "is_archived",
        "delivery_address_same",
        "processing_flat_cost",
        "send_pdf_invoice",
        "subtotal_balance",
        "tax_balance",
        "account_id",
        "total_order_balance",
        "applications_overridden",
        "pay_on_delivery_contract_sent_count",
        "order_balance",
        "order_contract",
        "coupon_code_order",
        "allow_external_payments",
        "application_response",
        "attributes",
        "credit_card_fee",
        "current_rent_period",
        "customer_profile_id",
        "file_upload",
        "gateway_cost",
        "is_discount_applied",
        "is_pickup",
        "misc_cost",
        "order_tax",
        "override_application_process",
        "purchase_order_number",
        "purchased_order_job_id",
        "remaining_balance",
        "rent_due_on_day",
        "order_contract",
        "is_late_fee_applied",
        "calculated_total_tax_paid",
        "calculated_rent_order_tax",
        "calculated_paid_successfully_by_credit_card",
        "line_items.minimum_shipping_cost",
        "line_items.pickup_email_sent",
        "line_items.missed_delivery",
        "line_items.interest_owed",
        "line_items.total_rental_price",
        "line_items.monthly_owed",
        "line_items.attributes",
        "line_items.other_inventory",
        "line_items.file_upload",
        "line_items.other_product_name",
        "line_items.other_product_shipping_time",
        "line_items.inventory_address",
        "line_items.coupon_line_item_values",
        "line_items.deliveries",
        "line_items.rental_history",
        "line_items.abrev_title",
        "line_items.abbrev_title_w_container_number",
        "rent_periods.rent_period_balances",
        "rent_periods.rent_period_tax_balance",
        "rent_periods.rent_period_taxes",
        "campaign_url",
        "calculated_revenue_excluding_shipping",
        "calculated_discount",
        "calculated_container_delivery_addresses",
        "calculated_bank_fees",
        "charge_per_line_item",
        "processing_percentage_cost",
        "referral_source",
        "credit_card",
        "tax_exempt",
        "total_paid",
        "transaction_type_order",
        "note.author",
        "note.created_at",
        "note.customer",
        "note.depot_id",
        "note.driver",
        "note.inventory_id",
        "note.order_id",
        "note.rental_history",
        "note.vendor",
    ),
)

PartialOrderOut = pydantic_model_creator(
    Order,
    name="PartialOrderOut",
    exclude=(
        "account",
        "customer.account",
        "customer.account_id",
        "user.account",
        "user.team_member_of",
        "user.team_members",
        "user.preferences",
        "user.rental_preferences",
        "user.transactions",
        "user.created_at",
        "user.modified_at",
        "user.assistant",
        "user.role_id",
        "user.is_active",
        "fees",
        "modified_at",
        "coming_from",
        "billing_address",
        "customer_application_schema",
        "leadconnect_sent",
        "first_payment_strategy",
        "primary_payment_method",
        "pod_sign_page_url",
        "is_archived",
        "delivery_address_same",
        "processing_flat_cost",
        "send_pdf_invoice",
        "subtotal_balance",
        "tax_balance",
        "account_id",
        "total_order_balance",
        "applications_overridden",
        "pay_on_delivery_contract_sent_count",
        "order_balance",
        "order_contract",
        "coupon_code_order",
        "allow_external_payments",
        "application_response",
        "attributes",
        "credit_card_fee",
        "current_rent_period",
        "customer_profile_id",
        "file_upload",
        "gateway_cost",
        "is_discount_applied",
        "is_pickup",
        "misc_cost",
        "order_tax",
        "override_application_process",
        "purchase_order_number",
        "purchased_order_job_id",
        "remaining_balance",
        "rent_due_on_day",
        "order_contract",
        "is_late_fee_applied",
        "calculated_total_tax_paid",
        "calculated_rent_order_tax",
        "calculated_paid_successfully_by_credit_card",
        "line_items.minimum_shipping_cost",
        "line_items.pickup_email_sent",
        "line_items.missed_delivery",
        "line_items.interest_owed",
        "line_items.total_rental_price",
        "line_items.monthly_owed",
        "line_items.attributes",
        "line_items.other_inventory",
        "line_items.file_upload",
        "line_items.other_product_name",
        "line_items.other_product_shipping_time",
        "line_items.inventory_address",
        "line_items.coupon_line_item_values",
        "line_items.deliveries",
        "line_items.rental_history",
        "line_items.abrev_title",
        "line_items.abbrev_title_w_container_number",
        "rent_periods.rent_period_balances",
        "rent_periods.rent_period_tax_balance",
        "rent_periods.rent_period_taxes",
        "campaign_url",
        "calculated_revenue_excluding_shipping",
        "calculated_discount",
        "calculated_container_delivery_addresses",
        "calculated_bank_fees",
        "charge_per_line_item",
        "processing_percentage_cost",
        "referral_source",
        "credit_card",
        "tax_exempt",
        "total_paid",
        "transaction_type_order",
        "note.author",
        "note.created_at",
        "note.customer",
        "note.depot_id",
        "note.driver",
        "note.inventory_id",
        "note.order_id",
        "note.rental_history",
        "note.vendor",
    ),
)


# :param meta_override: A PydanticMeta class to override model's values.
class PydanticMeta:
    exclude = [
        "user.sales_assistant",
        "user.manager",
        "user.team_lead",
        "user.team_member",
        "user.account",
        "user.commission",
        "order_commission",
        "misc_cost",
        "charge_gateway_cost",
        "account",
        "customer.account",
        "customer.account_id",
        "user.account",
        "user.team_member_of",
        "user.team_members",
        "line_items.driver",
        "line_items.potential_driver",
    ]
    computed = [
        "total_paid",
        "line_item_length",
        "is_pickup",
        "calculated_total_price",
        "calculated_sub_total_price",
        "calculated_remaining_order_balance",
        "calculated_fees",
        "calculated_monthly_owed_total",
        "calculated_shipping_revenue_total",
        "calculated_order_tax",
        "calculated_rent_order_tax",
        "calculated_fees_without_bank_fee",
        "calculated_monthly_subtotal",
        "current_rent_period",
        "calculated_bank_fees",
        "calculated_discount",
        "calculated_line_items_title",
        "calculated_paid_successfully_by_credit_card",
        "calculated_rent_balance",
        "calculated_current_overdue_rent_periods",
        "calculated_paid_thru",
        "calculated_total_rental_revenue",
        "calculated_total_tax_paid",
        "calculated_container_numbers",
        "calculated_down_payment",
        "calculated_contract_total",
        "calculated_revenue_excluding_shipping",
        "calculated_line_items_title_with_type",
    ]


meta = PydanticMeta()

PublicOrderOut = pydantic_model_creator(
    Order,
    name="PublicOrderOut",
    meta_override=meta,
)


class RankingsCommissionsOverride:
    exclude = [
        "account",
        "customer.account",
        "customer.account_id",
        "user.account",
        "user.team_member_of",
        "user.team_members",
        "user.assistant",
        "user.sales_assistant",
        "payment_type",
        "coming_from",
        "customer",
        "rent_periods",
        "type",
        "single_customer",
        "customer_application_schema",
        "leadconnect_sent",
        "application_response",
        "fees",
        "file_upload",
        "misc_cost",
        "order_contract",
        "transaction_type_order",
        "line_item_length",
        "order_tax",
        "coupon_code_order",
        "order_fee_balance",
        "billing_address",
        "completed_at",
        "delivered_at",
        "pay_on_delivery_contract_sent_count",
        "credit_card_fee",
        "customer_profile_id",
        "first_payment_strategy",
        "primary_payment_method",
        "referral_source",
        "tax_balance",
        "subtotal_balance",
        "total_order_balance",
        "pod_sign_page_url",
        "current_rent_period",
        "customer_application_schema_id",
        "billing_address_id",
    ]
    computed = [
        "line_item_number_containers",
        "calculated_order_subtotal_balance",
        "calculated_total_price",
        "calculated_containers_sub_total_price",
    ]


RankingOrderOut = pydantic_model_creator(
    Order,
    name="RankingOrderOut",
    meta_override=RankingsCommissionsOverride(),
)


class FeeTransaction(BaseModel):
    date: Optional[str]
    description: Optional[str]
    amount: Optional[str]
    status: Optional[str]
    tax: Optional[str]
    start_date: Optional[str]
    line_type: Optional[str]
    created_at: Optional[str]
    name: Optional[str]


class OrderTransaction(BaseModel):
    date: Optional[str]
    description: Optional[str]
    amount: Optional[str]
    status: Optional[str]
    tax: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    line_type: Optional[str]
    fees: Optional[dict]
    concatenated_fees: Optional[dict]
    transaction_type_rent_period: Optional[dict]


class OrderDetail(BaseModel):
    last_card_digits: Optional[str]
    auto_pay: Optional[str]
    status: Optional[str]
    late_fee_date: Optional[str]
    amount_due: Optional[str]
    container_type: Optional[str]
    display_order_id: Optional[str]
    start_date: Optional[str]


class ReceiptMainTableItem(BaseModel):
    date: Optional[str]
    display_order_id: Optional[str]
    description: Optional[str]
    unit: Optional[str]
    subtotal: Optional[str]
    total_tax_paid: Optional[str]
    total_paid: Optional[str]
    payment_type: Optional[str]


class ReceiptVerticalTable(BaseModel):
    taxed_subtotal: Optional[str]
    tax_exempt_subtotal: Optional[str]
    tax_paid: Optional[str]
    total_paid: Optional[str]


class ReceiptBottomTableItem(BaseModel):
    display_order_id: Optional[str]
    type: Optional[str]
    balance: Optional[Decimal]
    paid_thru: Optional[str]


class Receipt(BaseModel):
    customer_name: Optional[str]
    company_name: Optional[str]
    address: Optional[str]
    city_state_zip: Optional[str]
    customer_orders: Optional[str]
    current_balance: Optional[str]
    payment_date: Optional[str]
    notes: Optional[str]
    delivery_address: Optional[str]
    main_table: Optional[List[ReceiptMainTableItem]]
    vertical_table: Optional[ReceiptVerticalTable]
    bottom_table: Optional[List[ReceiptBottomTableItem]]
    show_bottom_table: Optional[bool]
    payment_type: Optional[str]


class OrderSearchFilters(BaseModel):
    statuses: Optional[str]
    order_types: Optional[str]
    searched_user_ids: Optional[list[str]]
    regions: Optional[str]
    pickup_regions: Optional[str]
    container_sizes: Optional[str]
    container_types: Optional[str]
    display_order_id: Optional[str]
    container_number: Optional[str]
    container_release_number: Optional[str]
    customer_name: Optional[str]
    customer_email: Optional[str]
    customer_phone: Optional[str]
    driver_id: Optional[str]
    not_driver_id: Optional[str]
    good_to_go: Optional[str]
    not_good_to_go: Optional[str]
    welcome_call: Optional[str]
    not_welcome_call: Optional[str]
    created_at: Optional[str]
    paid_at: Optional[str]
    signed_at: Optional[str]
    delivered_at: Optional[str]
    completed_at: Optional[str]
    container_id: Optional[str]
    not_container_id: Optional[str]
    pickup: Optional[str]
    not_pickup: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    emulated_user_id: Optional[str]
    scheduled_date: Optional[str]
    not_schedule_date: Optional[str]
    potential_date: Optional[str]
    not_potential_date: Optional[str]
    potential_driver: Optional[str]
    not_potential_driver: Optional[str]
    location: Optional[str]
    tracking_number: Optional[str]
    container_condition: Optional[str]
    product_type: Optional[str]
    customer_company_name: Optional[str]
    is_rush: Optional[bool]
    not_rush: Optional[bool]


def dfc(date_obj):
    if not date_obj:
        return None
    # Convert to Mountain Time
    mt_timezone = pytz.timezone('America/Denver')
    if date_obj.tzinfo is None:
        # Assume UTC if no timezone is specified
        date_obj = pytz.utc.localize(date_obj)
    mt_date = date_obj.astimezone(mt_timezone)

    # Format date as M/D/YY
    return mt_date.strftime("%-m/%-d/%y")


class CustomUserDTO(BaseModel):
    id: UUID
    full_name: str

    class Config:
        orm_mode = True


class OrderAddressDTO(BaseModel):
    id: UUID
    street_address: Optional[str]
    zip: Optional[str]
    state: Optional[str]
    city: Optional[str]
    county: Optional[str]
    full_address: Optional[str]

    class Config:
        orm_mode = True


class CustomVendorDTO(BaseModel):
    id: UUID
    name: Optional[str]
    primary_phone: Optional[str]
    primary_email: Optional[str]


class CustomDepotDTO(BaseModel):
    id: UUID
    name: Optional[str]
    full_address: Optional[str]
    primary_phone: Optional[str]
    primary_email: Optional[str]

    class Config:
        orm_mode = True

class CustomInventoryDTO(BaseModel):
    id: Union[UUID, str]
    container_number: Optional[str]
    container_release_number: Optional[str]
    inventory_total_cost: Optional[float]
    depot: Optional[CustomDepotDTO]
    vendor: Optional[CustomVendorDTO]

    class Config:
        orm_mode = True


class CustomerDriverDTO(BaseModel):
    id: UUID
    company_name: Optional[str]

    class Config:
        orm_mode = True


class LineItem(BaseModel):
    id: UUID
    scheduled_date: Optional[datetime]
    potential_date: Optional[datetime]
    driver: Optional[CustomerDriverDTO]
    potential_driver: Optional[CustomerDriverDTO]
    title: Optional[str]
    location: str
    inventory: Optional[CustomInventoryDTO]
    revenue: Optional[float]
    shipping_revenue: float
    shipping_cost: Optional[float]
    calculated_potential_driver_charge: Optional[float]
    potential_doller_per_mile: Optional[float]
    potential_miles: Optional[float]
    good_to_go: Optional[str]
    welcome_call: Optional[str]
    door_orientation: Optional[str]
    estimated_profit: Optional[float]
    product_type: Optional[str]
    product_city: Optional[str]

    class Config:
        orm_mode = True


class CustomerDTO(BaseModel):
    full_name: str
    company_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]

    class Config:
        orm_mode = True

class CustomerContactsDTO(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]

    class Config:
        orm_mode = True

class SingleCustomerDTO(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    company_name: Optional[str]
    customer_contacts: List[CustomerContactsDTO]

    class Config:
        orm_mode = True


class CustomNote(BaseModel):
    id: UUID


class CustomOrderDTO(BaseModel):
    id: UUID
    display_order_id: str
    type: str
    created_at: datetime
    calculated_paid_in_full_date: Optional[datetime]
    calculated_paid_date_rental: Optional[datetime]
    paid_at: Optional[datetime]
    signed_at: Optional[datetime]
    calculated_signed_date: Optional[datetime]
    completed_at: Optional[datetime]
    delivered_at: Optional[datetime]
    address: Optional[OrderAddressDTO]
    customer: Optional[CustomerDTO]
    single_customer: Optional[SingleCustomerDTO]
    line_items: List[LineItem]
    user: Optional[CustomUserDTO]
    is_autopay: bool
    payment_type: Optional[str]
    estimated_profit: Optional[float]
    calculated_order_tax: float
    calculated_total_price: float
    calculated_monthly_subtotal: float
    calculated_rent_balance: float
    note: List[CustomNote]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj):

        # Convert the line_items relationship before creating the DTO
        obj_data = {
            "id": obj.id,
            "display_order_id": obj.display_order_id,
            "type": obj.type,
            "created_at": obj.created_at,
            "calculated_paid_in_full_date": obj.calculated_paid_in_full_date(),
            "calculated_paid_date_rental": obj.calculated_paid_date_rental(),
            "paid_at": obj.paid_at,
            "signed_at": obj.signed_at,
            "calculated_signed_date": obj.calculated_signed_date(),
            "completed_at": obj.completed_at,
            "delivered_at": obj.delivered_at,
            "payment_type": obj.payment_type,
            "calculated_total_price": float(obj.calculated_total_price()),
            "line_items": obj.line_items.related_objects
            if hasattr(obj.line_items, 'related_objects')
            else obj.line_items,
            "address": obj.address,
            "customer": obj.customer,
            "user": obj.user,
            "is_autopay": obj.is_autopay,
            "note": obj.note.related_objects if hasattr(obj.note, 'related_objects') else obj.note,
        }

        if obj.single_customer:
            single_customer = {
                "first_name": obj.single_customer.first_name,
                "last_name": obj.single_customer.last_name,
                "company_name": obj.single_customer.company_name,
                "customer_contacts": []
            }

            for cc in obj.single_customer.customer_contacts.related_objects:
                single_customer['customer_contacts'].append({
                    "first_name": cc.first_name,
                    "last_name": cc.last_name,
                    "email": cc.email,
                    "phone": cc.phone
                })

            obj_data['single_customer'] = single_customer

        if obj_data['address']:
            obj_data['address'].full_address = (
                obj.address.full_address()
                if not isinstance(obj.address.full_address, str)
                else obj.address.full_address
            )

        if obj_data['customer']:
            obj_data['customer'].full_name = (
                obj.customer.full_name() if not isinstance(obj.customer.full_name, str) else obj.customer.full_name
            )
        for x in obj_data['line_items']:
            if not isinstance(x.title, str):
                setattr(x, 'title', x.title())

            if callable(x.location):
                setattr(x, 'location', x.location())

            if callable(x.calculated_potential_driver_charge):
                res = x.calculated_potential_driver_charge()
                setattr(x, "calculated_potential_driver_charge", float(res) if res else None)

            if callable(x.estimated_profit):
                setattr(x, "estimated_profit", float(x.estimated_profit()))

            if x.inventory and x.inventory.depot and not isinstance(x.inventory.depot.full_address, str):
                x.inventory.depot.full_address = x.inventory.depot.full_address()

        if obj.user and not isinstance(obj.user.full_name, str):
            obj_data['user'].full_name = obj.user.full_name()

        obj_data['calculated_order_tax'] = float(obj.calculated_order_tax())
        obj_data['calculated_total_price'] = float(obj.calculated_total_price())
        obj_data['calculated_monthly_subtotal'] = float(obj.calculated_monthly_subtotal())
        obj_data['calculated_rent_balance'] = float(obj.calculated_rent_balance())
        return cls.parse_obj(obj_data)


class LineItemOrderDTO(BaseModel):
    display_delivered_at: Optional[str] = None
    display_completed_at: Optional[str] = None
    display_paid_at: Optional[str] = None
    display_signed_at: Optional[str] = None
    order_delivered_at: Optional[datetime] = None
    order_completed_at: Optional[datetime] = None
    order_paid_at: Optional[datetime] = None
    order_signed_at: Optional[datetime] = None
    customer_full_name: Optional[str] = None
    customer_company_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    order_id: Optional[UUID] = None
    order_display_order_id: Optional[str] = None
    order_type: Optional[str] = None
    display_created_at: Optional[str] = None
    order_created_at: Optional[datetime] = None
    display_created_at: Optional[datetime] = None
    order_calculated_paid_in_full_date: Optional[datetime] = None
    order_calculated_paid_date_rental: Optional[str] = None
    display_signed_at: Optional[datetime] = None
    order_signed_at: Optional[datetime] = None
    order_calculated_signed_date: Optional[datetime] = None
    display_completed_at: Optional[datetime] = None
    order_completed_at: Optional[datetime] = None
    display_delivered_at: Optional[datetime] = None
    order_delivered_at: Optional[datetime] = None
    order_address: Optional[OrderAddressDTO] = None
    order_customer_full_name: Optional[str] = None
    order_customer_company_name: Optional[str] = None
    order_customer_phone: Optional[str] = None
    order_customer_email: Optional[str] = None
    order_agent: Optional[str] = None
    order_is_autopay: Optional[bool] = None
    order_payment_type: Optional[str] = None
    order_estimated_profit: Optional[float] = None
    order_calculated_order_tax: Optional[float] = None
    order_calculated_total_price: Optional[float] = None
    order_calculated_monthly_subtotal: Optional[float] = None
    order_calculated_rent_balance: Optional[float] = None
    order_note: List[str] = None
    order_single_customer: Optional[SingleCustomerDTO]
    line_item_id: Optional[UUID] = None
    line_item_scheduled_date: Optional[datetime] = None
    line_item_org_scheduled_date: Optional[datetime] = None
    line_item_potential_date: Optional[datetime] = None
    line_item_driver: Optional[str] = None
    line_item_potential_driver_id: Optional[UUID] = None
    line_item_title: Optional[str] = None
    line_item_location: Optional[str] = None
    line_item_inventory_id: Optional[UUID] = None
    line_item_inventory_container_release_number: Optional[str] = None
    line_item_inventory: Optional[CustomInventoryDTO] = None
    line_item_revenue: Optional[float] = None
    line_item_shipping_revenue: Optional[float] = None
    line_item_shipping_cost: Optional[float] = None
    line_item_calculated_potential_driver_charge: Optional[float] = None
    line_item_potential_doller_per_mile: Optional[float] = None
    line_item_potential_miles: Optional[float] = None
    line_item_good_to_go: Optional[str] = None
    line_item_welcome_call: Optional[str] = None
    line_item_door_orientation: Optional[str] = None
    line_item_estimated_profit: Optional[float] = None
    line_item_product_type: Optional[str]
    line_item_product_city: Optional[str]
    order_has_accessories: Optional[bool]
    order_has_containers: Optional[bool]

class UpdateRentPeriodDates(BaseModel):
    start_date: datetime
    end_date: datetime

class RentalStatementDataRequest(BaseModel):
    partial: bool
    partialRentalStatementDates: List[datetime]
