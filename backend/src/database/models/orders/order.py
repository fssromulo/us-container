# Python imports
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Union
from tortoise.fields.relational import ReverseRelation

# Pip imports
from loguru import logger
from tortoise import fields, models
from tortoise.exceptions import NoValuesFetched

# Internal imports
from src.database.models.order_tax import OrderTax
from src.database.models.orders.fee_type import FeeType
from src.database.models.orders.payment_options import PaymentOptions
from src.database.models.orders.purchase_types import PurchaseTypes
from src.database.models.rent_period import RentPeriod
from src.database.models.tax_balance import TaxBalance
from src.database.models.total_order_balance import TotalOrderBalance


class Order(models.Model):
    id = fields.UUIDField(pk=True)
    display_order_id = fields.CharField(unique=True, max_length=50, index=True)
    # change this on import to not auto add. Then change back after import.
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    paid_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    delivered_at = fields.DatetimeField(null=True)
    signed_at = fields.DatetimeField(null=True)
    payment_type = fields.CharEnumField(PaymentOptions, null=True)
    pay_on_delivery_contract_sent_count = fields.IntField(null=True)
    type = fields.CharEnumField(PurchaseTypes, null=True)
    status = fields.CharField(null=True, max_length=50, index=True)
    attributes = fields.JSONField(null=True)
    applications_overridden = fields.JSONField(null=True)
    coming_from = fields.TextField(null=True)
    is_discount_applied = fields.BooleanField(default=False)
    allow_external_payments = fields.BooleanField(default=True)
    credit_card_fee = fields.BooleanField(default=True)
    rent_due_on_day = fields.IntField(null=True)
    address = fields.OneToOneField("models.OrderAddress", related_name="order", index=True, null=True)
    billing_address = fields.ForeignKeyField("models.OrderAddress", related_name="order2", index=True, null=True)
    user = fields.ForeignKeyField("models.User", related_name="order", index=True, null=True)
    purchase_order_number = fields.TextField(null=True)
    purchased_order_job_id = fields.TextField(null=True)
    customer = fields.ForeignKeyField("models.OrderCustomer", related_name="order", null=True)
    account = fields.ForeignKeyField("models.Account", related_name="order", index=True)
    customer_profile_id = fields.TextField(null=True)
    override_application_process = fields.BooleanField(default=False)
    is_autopay = fields.BooleanField(default=False)
    is_late_fee_applied = fields.BooleanField(default=True)
    single_customer = fields.ForeignKeyField("models.Customer", related_name="order", index=True, null=True)
    customer_application_schema = fields.ForeignKeyField(
        "models.CustomerApplicationSchema", related_name="order", index=True, null=True
    )
    leadconnect_sent = fields.BooleanField(default=False)
    first_payment_strategy = fields.TextField(default="")
    campaign_url = fields.TextField(default="")
    referral_source = fields.TextField(default="")
    primary_payment_method = fields.TextField(default="")
    pod_sign_page_url = fields.TextField(null=True)
    is_archived = fields.BooleanField(default=False)
    tax_exempt = fields.BooleanField(default=False)
    delivery_address_same = fields.BooleanField(default=True)
    processing_flat_cost = fields.DecimalField(max_digits=7, decimal_places=3, null=True)
    processing_percentage_cost = fields.DecimalField(max_digits=7, decimal_places=3, null=True)
    charge_per_line_item = fields.BooleanField(null=True)
    send_pdf_invoice = fields.BooleanField(default=False)
    message_type = fields.CharField(max_length=1, null=True)

    class PydanticMeta:
        # Let's exclude the created timestamp
        exclude = [
            "user.sales_assistant",
            "user.manager",
            "user.team_lead",
            "user.team_member",
            "user.account",
            "user.commission",
            "user.preferences",
            "order_commission",
        ]
        computed = [
            "total_paid",
            "calculated_profit",
            "line_item_length",
            "line_item_number_containers",
            "is_pickup",
            "calculated_total_price",
            "calculated_sub_total_price",
            "calculated_remaining_order_balance",
            "calculated_misc_costs",
            "calculated_fees",
            "calculated_monthly_owed_total",
            "calculated_monthly_owed_total_wo_fees_or_tax",
            "calculated_shipping_revenue_total",
            "calculated_order_tax",
            "calculated_rent_order_tax",
            "calculated_fees_without_bank_fee",
            "calculated_monthly_subtotal",
            "current_rent_period",
            "calculated_bank_fees",
            "calculated_discount",
            "calculated_line_items_title",
            "calculated_abreviated_line_items_title",
            "calculated_container_cost",
            "calculated_shipping_cost",
            "calculated_paid_successfully_by_credit_card",
            "calculated_rent_balance",
            "calculated_current_overdue_rent_periods",
            "calculated_paid_thru",
            "calculated_total_rental_revenue",
            "calculated_vendor_names",
            "calculated_total_tax_paid",
            "calculated_container_numbers",
            "calculated_container_delivery_addresses",
            "calculated_down_payment",
            "calculated_contract_total",
            "has_accessories",
            "has_containers",
            "calculated_revenue_excluding_shipping",
            "calculated_paid_date_rental",
            "calculated_signed_date",
            "calculated_containers_sub_total_price",
            "calculated_order_tax_balance",
            "calculated_order_subtotal_balance",
            "calculated_sub_total_without_fees",
            "calculated_order_tax_rate",
            "calculated_order_fees_balance",
            "calculated_order_fees_taxable_balance",
            "calculated_current_rent_balance",
            "calculated_processing_cost",
            "calculated_line_items_title_with_type",
            "calculated_accessory_commission",
            "calculated_is_manager",
            "calculated_paid_in_full_date",
            "calculated_delivered_at",
        ]

    def calculated_revenue_excluding_shipping(self) -> Optional[Decimal]:
        try:
            return sum([line_item.revenue or 0 for line_item in self.line_items])
        except NoValuesFetched:
            return 0

    def calculated_contract_total(self) -> int:
        if not self.pay_on_delivery_contract_sent_count:
            return 0
        return self.pay_on_delivery_contract_sent_count

    def calculated_down_payment(self) -> Optional[Decimal]:
        try:
            if self.type == "RENT":
                unit_cost = self.rent_periods[0].amount_owed if len(self.rent_periods) > 0 else 0
                return (
                    sum([period.calculated_down_payment_fees() for period in self.rent_periods])
                    + Decimal(self.calculated_rent_order_tax())
                    + Decimal(unit_cost)
                )
            return Decimal(0.00)
        except NoValuesFetched:
            return Decimal(0.00)

    def calculated_total_rental_revenue(self) -> Optional[Decimal]:
        try:
            if self.rent_periods is not None:
                return sum([period.calculated_total_paid() for period in self.rent_periods])
        except NoValuesFetched:
            return 0

    def calculated_monthly_subtotal(self) -> Optional[Decimal]:
        try:
            if self.line_items is None:
                return 0
            total_monthly_owed = 0
            for line_item in self.line_items:
                if line_item.monthly_owed is None:
                    continue
                else:
                    total_monthly_owed += line_item.monthly_owed
            return total_monthly_owed
        except NoValuesFetched:
            return 0

    def calculated_monthly_owed_total(self) -> Optional[Decimal]:
        try:
            if self.line_items is None:
                return 0
            total_monthly_owed = 0
            for line_item in self.line_items:
                if line_item.monthly_owed is None:
                    continue
                else:
                    total_monthly_owed += line_item.monthly_owed
            return total_monthly_owed + self.calculated_fees() + self.calculated_order_tax()
        except NoValuesFetched:
            return 0

    def calculated_monthly_owed_total_wo_fees_or_tax(self) -> Optional[Decimal]:
        try:
            if self.line_items is None:
                return 0
            total_monthly_owed = 0
            for line_item in self.line_items:
                if line_item.monthly_owed is None:
                    continue
                else:
                    total_monthly_owed += line_item.monthly_owed
            return total_monthly_owed
        except NoValuesFetched:
            return 0

    def calculated_shipping_revenue_total(self) -> Optional[Decimal]:
        try:
            if self.line_items is not None:
                return sum([line_item.shipping_revenue or 0 for line_item in self.line_items])
        except NoValuesFetched:
            return 0

    def is_pickup(self) -> Optional[bool]:
        try:
            if self.line_items is not None:
                return any(
                    [
                        (line_item.shipping_revenue == 0 or line_item.shipping_revenue is None)
                        for line_item in self.line_items
                        if line_item.product_type != 'CONTAINER_ACCESSORY'
                    ]
                )
        except NoValuesFetched:
            return False

    def line_item_number_containers(self) -> Optional[Decimal]:
        try:
            containers = 0
            if self.line_items is not None:
                for line_item in self.line_items:
                    if line_item.product_type is None or line_item.product_type != "CONTAINER_ACCESSORY":
                        containers += 1
            return containers
        except NoValuesFetched:
            return 0

    def line_item_length(self) -> Optional[Decimal]:
        try:
            if self.line_items is not None:
                return len(self.line_items)
            return 0
        except NoValuesFetched:
            return 0

    def container_line_item_length(self) -> Optional[Decimal]:
        try:
            if self.line_items is not None:
                return len(
                    [
                        x
                        for x in self.line_items
                        if x.product_type == 'CONTAINER' or x.product_type == 'SHIPPING_CONTAINER'
                    ]
                )
            return 0
        except NoValuesFetched:
            return 0

    def calculated_order_tax(self) -> Optional[Decimal]:
        """
        This method is being used to take the most order tax record from the order_tax entity
        Returns: This returns None if there are not any order_taxes found
        """
        try:
            if self.tax_exempt:
                return 0
            total_tax: Decimal = 0
            if not self.order_tax:
                for li in self.line_items:
                    if li.tax:
                        total_tax += li.tax
                return total_tax  # If there is not a record, sum up the line items' tax
            # just finding the most recent record in this group
            most_recent_tax: OrderTax = max(self.order_tax, key=lambda x: x.created_at)

            total_tax = most_recent_tax.tax_amount
            return total_tax
        except NoValuesFetched:
            return 0

    def calculated_rent_order_tax(self) -> Optional[Decimal]:
        try:
            if self.type == 'RENT':
                down_payment_period = None
                for rent_period in self.rent_periods:
                    if rent_period.calculated_down_payment_fees() > Decimal(0.00):
                        down_payment_period = rent_period
                        break
                tax = 0
                if down_payment_period is not None:
                    for period_tax in down_payment_period.rent_period_taxes:
                        if period_tax.tax_amount > tax:
                            tax = period_tax.tax_amount
                return tax
            else:
                return 0
        except NoValuesFetched:
            return 0

    def calculated_total_tax_paid(self) -> Optional[Decimal]:
        try:
            total_tax_paid = Decimal(0)
            percent_tax = Decimal(0)

            if self.type == 'PURCHASE' or self.type == 'PURCHASE_ACCESSORY':
                percent_tax = self._calculate_purchase_tax_percent()
                total_tax_paid = self._calculate_total_tax_paid_for_transactions(
                    self.transaction_type_order, percent_tax, self.credit_card
                )

            elif self.type == 'RENT':
                for rent_period in self.rent_periods:
                    total_balance = rent_period.calculated_rent_period_total_balance()
                    total_tax = rent_period.calculated_rent_period_tax()

                    if total_balance == 0:
                        continue

                    percent_tax = total_tax / total_balance
                    total_tax_paid += self._calculate_total_tax_paid_for_transactions(
                        rent_period.transaction_type_rent_period, percent_tax
                    )

            return total_tax_paid
        except NoValuesFetched:
            return Decimal(0)

    def _calculate_purchase_tax_percent(self) -> Decimal:
        percent_tax = Decimal(0)
        if not self.order_tax:
            for li in self.line_items:
                single_line_item_price = self.calculate_single_line_item_price(li)
                if single_line_item_price != 0:
                    percent_tax = Decimal(li.tax if li.tax else 0) / Decimal(single_line_item_price)
        else:
            try:
                max_val = max(self.order_tax, key=lambda x: x.created_at)
                total_price = self.calculated_total_price()
                tax_amount = Decimal(max_val.tax_amount if max_val and max_val.tax_amount else 0)
                if total_price != 0 and Decimal(total_price) != tax_amount:
                    percent_tax = tax_amount / (Decimal(total_price) - tax_amount)
            except NoValuesFetched:
                percent_tax = Decimal(0)
        return percent_tax

    def _calculate_total_tax_paid_for_transactions(self, transactions, percent_tax, credit_card=[]) -> Decimal:
        total_tax_paid = Decimal(0)
        if transactions:
            for tt in transactions:
                total_tax_paid += Decimal(tt.amount if tt.amount else 0) / (1 + percent_tax) * percent_tax
        elif credit_card:
            for cc in credit_card:
                if (
                    cc.response_from_gateway.get('transactionResponse', {})
                    .get('messages', [{}])[0]
                    .get("description", "")
                    == "This transaction has been approved."
                ):
                    total_tax_paid += (
                        Decimal(cc.response_from_gateway.get("payment_amount", 0)) / (1 + percent_tax) * percent_tax
                    )
        return total_tax_paid

    # calculated field for grabbing the agent commission if they are a commission
    def calculated_misc_costs(self) -> Optional[Decimal]:
        """
        This method will find all of the related misc. costs to this order. Then it will sum all of those up
        and return it as the total amount of calculated misc costs.
        These costs are costs incurred to the company and not the client. So this wil only be used to
        negatively affect the profit.
        """
        try:
            misc_cost: Decimal = 0
            if self.misc_cost:
                misc_cost = sum(item.amount for item in self.misc_cost)
                return misc_cost
            else:
                return 0
        except NoValuesFetched:
            return 0

        # calculated field for grabbing the agent commission if they are a commission

    def calculated_fees(self) -> Optional[Decimal]:
        """
        This method will find all of the fees to this order. Then it will sum all of those up
        and return it as the total amount of fees.
        These fees are fees incurred by the company and to the client. So this wil only be used to
        positively affect the total price.
        """
        fee = 0
        try:
            if self.fees:
                fee = sum(item.fee_amount for item in self.fees)

            if self.type == 'RENT':
                for rent_period in self.rent_periods:
                    fee += rent_period.calculated_rent_period_fee_balance()

            return fee

        except NoValuesFetched:
            return 0

    def calculated_discount(self) -> Optional[Decimal]:
        try:
            if not hasattr(self, 'coupon_code_order') or not self.coupon_code_order:
                return Decimal(0)

            coupon_discounts = Decimal(0)

            if not hasattr(self, 'line_items') or not isinstance(self.line_items, list):
                return Decimal(0)

            for line_item in self.line_items:
                if not hasattr(line_item, 'revenue') or not hasattr(line_item, 'product_type'):
                    continue  # Skip this line item if essential attributes are missing

                for coupon_code_item in self.coupon_code_order:
                    if not hasattr(coupon_code_item, 'coupon'):
                        continue  # Skip if coupon attribute is missing

                    discount_amount = Decimal(0)

                    coupon = coupon_code_item.coupon
                    if (
                        not hasattr(coupon, 'minimum_discount_threshold')
                        or not hasattr(coupon, 'percentage')
                        or not hasattr(coupon, 'amount')
                        or not hasattr(coupon, 'category')
                    ):
                        continue  # Skip if any necessary coupon attributes are missing

                    if line_item.revenue >= coupon.minimum_discount_threshold:
                        if coupon.percentage:
                            discount_amount = Decimal(line_item.revenue) * (Decimal(coupon.percentage) / Decimal(100))
                        else:
                            discount_amount = Decimal(coupon.amount)

                        # Apply the discount based on product type and coupon category
                        if line_item.product_type == "CONTAINER_ACCESSORY":
                            # Accessory
                            if coupon.category in ['accessories_only', 'both']:
                                coupon_discounts += discount_amount
                        else:
                            # Container
                            if coupon.category == 'both' or coupon.category != 'accessories_only':
                                coupon_discounts += discount_amount

            return coupon_discounts
        except Exception:
            return Decimal(0)

    def calculated_taxable_fees_without_bank_fee(self) -> Optional[Decimal]:
        """
        This method will find all of the fees to this order that are not bank fees. Then it will sum all of those up
        and return it as the total amount of fees.
        These fees are fees incurred by the company and to the client. So this wil only be used to
        positively affect the total price.
        """
        try:
            if self.fees:
                fee = sum(
                    (
                        item.fee_amount
                        if hasattr(item, 'type')
                        and item.type
                        and hasattr(item.type, "name")
                        and item.type.name != FeeType.CREDIT_CARD
                        and item.type.is_taxable
                        else 0
                    )
                    for item in self.fees
                )
                return fee
            else:
                return 0
        except NoValuesFetched:
            return 0

    def calculated_fees_without_bank_fee(self) -> Optional[Decimal]:
        """
        This method will find all of the fees to this order that are not bank fees. Then it will sum all of those up
        and return it as the total amount of fees.
        These fees are fees incurred by the company and to the client. So this wil only be used to
        positively affect the total price.
        """
        try:
            if self.fees:
                fee = sum(
                    (
                        item.fee_amount
                        if hasattr(item, 'type')
                        and item.type
                        and hasattr(item.type, "name")
                        and item.type.name != FeeType.CREDIT_CARD
                        else 0
                    )
                    for item in self.fees
                )
                return fee
            else:
                return 0
        except NoValuesFetched:
            return 0

    def calculated_bank_fees(self) -> Optional[Decimal]:
        try:
            if self.fees:
                fee = sum(item.fee_amount if item.type.name == FeeType.CREDIT_CARD else 0 for item in self.fees)
                return fee
            else:
                return 0
        except Exception:
            return 0

    def calculated_sub_total_price(self) -> Optional[Decimal]:
        try:
            sub_total_price = sum([self.calculate_single_line_item_price(line_item) for line_item in self.line_items])
            return sub_total_price + self.calculated_taxable_fees_without_bank_fee()
        except NoValuesFetched:
            return 0

    # if line_item.product_type is None or line_item.product_type != "CONTAINER_ACCESSORY"
    def calculated_containers_sub_total_price(self) -> Optional[Decimal]:
        try:
            sub_total_price = sum(
                [
                    self.calculate_single_line_item_price(line_item)
                    if line_item.product_type is None or line_item.product_type != "CONTAINER_ACCESSORY"
                    else Decimal(0)
                    for line_item in self.line_items
                ]
            )
            return sub_total_price + self.calculated_taxable_fees_without_bank_fee()
        except NoValuesFetched:
            return 0

    def calculated_sub_total_without_fees(self) -> Optional[Decimal]:
        try:
            return sum([self.calculate_single_line_item_price(line_item) for line_item in self.line_items])
            # return sub_total_price + self.calculated_fees_without_bank_fee()
        except NoValuesFetched:
            return 0

    def calculate_single_line_item_price(self, li):
        total = 0
        if li.revenue is not None:
            total += li.revenue
        if li.shipping_revenue is not None:
            total += li.shipping_revenue
        return total

    def calculated_total_price(self) -> Optional[Decimal]:
        try:
            return self.calculated_sub_total_price() + self.calculated_bank_fees() + self.calculated_order_tax()
        except NoValuesFetched:
            return 0

    def total_paid(self) -> Optional[Decimal]:
        if self.type == 'RENT':
            # need to go through all periods and look at all the balances saved between each 0 balance
            # and add them all up
            # total_paid = Decimal(0)
            # for period in self.rent_periods:
            #     for balance in period.rent_period_balances:
            #         if balance.remaining_balance is not None and balance.remaining_balance > 0:
            #             total_paid += balance.remaining_balance
            return 0

        if self.calculated_remaining_order_balance() is not None:
            total_price = self.calculated_total_price()
            remaining_balance = self.calculated_remaining_order_balance()
            not_taxable_fees = self.calculated_fees_without_bank_fee() - self.calculated_taxable_fees_without_bank_fee()
            return total_price + not_taxable_fees - remaining_balance

    def calculated_processing_cost(self) -> Optional[Decimal]:
        try:
            if self.charge_per_line_item and self.processing_flat_cost and self.processing_flat_cost > 0:
                return self.processing_flat_cost * Decimal(self.container_line_item_length())
            elif not self.charge_per_line_item and self.processing_flat_cost and self.processing_flat_cost > 0:
                return self.processing_flat_cost
            elif self.processing_percentage_cost and self.processing_percentage_cost > 0:
                return self.calculated_total_price() * self.processing_percentage_cost
            else:
                return 0
        except NoValuesFetched:
            logger.info("No values fetched")
            return -1

    def calculated_profit(self) -> Optional[Decimal]:
        try:
            # if self.profit:
            #     return self.profit
            line_items = self.line_items
            if isinstance(self.line_items, ReverseRelation):
                line_items = self.line_items.related_objects

            if line_items is not None:
                fee_profit = 0

                fees = self.fees
                if isinstance(self.fees, ReverseRelation):
                    fees = self.fees.related_objects

                for fee in fees:
                    if hasattr(fee, 'fee_type') and hasattr(fee.type, 'adjusts_profit') and fee.type.adjusts_profit:
                        fee_profit += fee.fee_amount

                profit_without_gateway = sum([line_item.estimated_profit() for line_item in line_items])
                if not profit_without_gateway:
                    return 0

                profit_without_gateway += fee_profit

                processing_cost = self.calculated_processing_cost()

                return profit_without_gateway - self.calculated_misc_costs() - processing_cost
        except NoValuesFetched:
            return -1

    def calculated_paid_thru(self) -> Optional[str]:
        try:
            if self.type == 'RENT':
                last_rent_period = None

                rent_periods = self.rent_periods
                if isinstance(rent_periods, ReverseRelation):
                    rent_periods = rent_periods.related_objects
                for rp in rent_periods[::-1]:
                    if rp.calculated_rent_period_total_balance() == 0:
                        last_rent_period = rp
                        break

                return (
                    last_rent_period.end_date.strftime("%m/%d/%y")
                    if last_rent_period is not None and last_rent_period.end_date
                    else 'NOT APPLICABLE'
                )
            return "NOT APPLICABLE"
        except NoValuesFetched:
            return "NOT APPLICABLE"

    def find_last_transaction_paid(self):
        rent_periods = sorted(self.rent_periods, key=lambda x: x.start_date)
        for i, period in enumerate(rent_periods):
            if period.calculated_rent_period_total_balance() != 0:
                if i > 0:
                    return rent_periods[i - 1]
                else:
                    return None
        return None

    def calculated_current_rent_balance(self) -> Optional[Decimal]:
        try:
            if self.type == 'RENT':
                if self.calculated_paid_thru() == "NOT APPLICABLE" and self.rent_periods:
                    return Decimal(self.rent_periods[0].calculated_rent_period_total_balance())
                return Decimal(
                    sum(
                        [
                            period.calculated_rent_period_total_balance()
                            for period in self.rent_periods
                            if period.start_date is None or period.start_date < datetime.now(timezone.utc)
                        ]
                    )
                )

            return Decimal(0)
        except NoValuesFetched:
            return Decimal(0)

    def calculated_remaining_order_balance(self) -> Optional[Decimal]:
        """
        This method is being used to take the most recent balance record from the order_balance entity
        Returns: This returns None if there are not any order_balances found
        """
        try:
            if self.type == 'RENT':
                return Decimal(sum([period.calculated_rent_period_total_balance() for period in self.rent_periods]))

            remaining_balance: Decimal
            # just finding the most recent record in this group
            if not self.total_order_balance:
                return 0
            most_recent_balance: TotalOrderBalance = max(self.total_order_balance, key=lambda x: x.created_at)

            # We are now adding the calculated order tax to this
            remaining_balance = most_recent_balance.remaining_balance
            return remaining_balance if remaining_balance is not None else 0
        except NoValuesFetched:
            return 0

    def current_rent_period(self) -> Optional[dict]:
        try:
            rent_periods: Union[List[RentPeriod], None] = self.rent_periods
            # check to see if any rent periods are present
            if not rent_periods:
                return rent_periods

            current_rent_period: RentPeriod
            # next check to see if there is only one, signifying that it has a down payment,
            # but has not been paid yet
            if len(rent_periods) == 1:
                current_rent_period = rent_periods[0]
                return current_rent_period

            # if there are more than 1 periods, then we will display the current rent period
            today = datetime.now(timezone.utc)
            current_rent_periods: List[RentPeriod] = list(
                filter(
                    lambda period: (today >= period.start_date and today <= period.end_date)
                    or period.start_date is None,
                    rent_periods,
                )
            )
            if not current_rent_periods:
                return {}
            # current_rent_period = current_rent_periods[0]
            return current_rent_periods[0]
        except NoValuesFetched:
            return {}

    def has_containers(self) -> bool:
        try:
            for line_item in self.line_items:
                if line_item.product_type is None or line_item.product_type != "CONTAINER_ACCESSORY":
                    return True
            return False
        except NoValuesFetched:
            return False

    def has_accessories(self) -> bool:
        try:
            for line_item in self.line_items:
                if line_item.product_type is not None and line_item.product_type == "CONTAINER_ACCESSORY":
                    return True
            return False
        except NoValuesFetched:
            return False

    def calculated_abreviated_line_items_title(self) -> str:
        s = ''
        try:
            for line_item in self.line_items:
                s += f'{line_item.abrev_title()} | '
            return s[:-2]
        except NoValuesFetched:
            return "No line items on this order!!"

    def calculated_line_items_title(self) -> str:
        s = ''
        containers = {}
        try:
            if not self.line_items:
                return ""
            for line_item in self.line_items:
                if line_item.product_type is None or line_item.product_type != "CONTAINER_ACCESSORY":
                    if line_item.container_size is not None and line_item.condition is not None:
                        key = line_item.container_size + " Ft " + line_item.condition
                    else:
                        key = " Ft "
                    if key not in containers:
                        containers[key] = 1
                    else:
                        containers[key] += 1
                else:
                    key = line_item.other_product_name
                    if key not in containers:
                        containers[key] = 1
                    else:
                        containers[key] += 1
            for key in containers:
                s += f'({containers[key]}) {key} | '
            if s:
                return s[:-2]
            else:
                return s
        except NoValuesFetched:
            return "No line items on this order!!"

    def calculated_line_items_title_with_type(self) -> str:
        s = ''
        containers = {}
        try:
            if not self.line_items:
                return ""
            for line_item in self.line_items:
                if line_item.product_type is None or line_item.product_type != "CONTAINER_ACCESSORY":
                    if line_item.container_size is not None and line_item.condition is not None:
                        high_cube = (
                            "Standard"
                            if not line_item.attributes
                            else "High Cube"
                            if line_item.attributes.get("high_cube")
                            else "Standard"
                        )
                        double_door = (
                            ""
                            if not line_item.attributes
                            else "Double Doors"
                            if line_item.attributes.get("double_door")
                            else ""
                        )
                        type = f"{double_door} {high_cube}".strip()
                        product_type = (
                            ""
                            if not line_item.attributes
                            else ""
                            if not line_item.attributes.get("portable")
                            else "Portable"
                        )

                        key = line_item.container_size + " Ft " + line_item.condition + " " + type + " " + product_type
                    else:
                        key = " Ft "
                    if key not in containers:
                        containers[key] = 1
                    else:
                        containers[key] += 1
                else:
                    key = line_item.other_product_name
                    if key not in containers:
                        containers[key] = 1
                    else:
                        containers[key] += 1
            for key in containers:
                s += f'({containers[key]}) {key} | '
            if s:
                return s[:-2]
            else:
                return s
        except NoValuesFetched:
            return "No line items on this order!!"

    def calculated_vendor_names(self) -> str:
        s = ''
        containers = {}
        try:
            if not self.line_items:
                return ""
            for line_item in self.line_items:
                if (
                    line_item.inventory is not None
                    and hasattr(line_item.inventory, "vendor")
                    and line_item.inventory.vendor is not None
                    and hasattr(line_item.inventory.vendor, "name")
                ):
                    key = line_item.inventory.vendor.name
                    if key not in containers:
                        containers[key] = 1
                    else:
                        containers[key] += 1

            for key in containers:
                s += f'({containers[key]}) {key} | '
            if s:
                return s[:-2]
            else:
                return s
        except NoValuesFetched:
            return "No line items on this order!!"

    def calculated_container_numbers(self) -> str:
        s = ''
        containers = {}
        try:
            if not self.line_items:
                return ""
            for line_item in self.line_items:
                if (
                    line_item.inventory is not None
                    and hasattr(line_item.inventory, "container_number")
                    and line_item.inventory.container_number is not None
                ):
                    key = line_item.inventory.container_number
                    if key not in containers:
                        containers[key] = 1
                    else:
                        containers[key] += 1

            for key in containers:
                s += f'({containers[key]}) {key} | '
            if s:
                return s[:-2]
            else:
                return s
        except NoValuesFetched:
            return "No line items on this order!!"

    def calculated_container_delivery_addresses(self) -> str:
        s = ''
        addresses = {}
        try:
            if not self.line_items:
                return ""
            for line_item in self.line_items:
                if line_item.inventory_address:
                    if len(line_item.inventory_address) > 0:
                        first_address = line_item.inventory_address[0]
                        if (
                            first_address is not None
                            and hasattr(first_address, "full_address_computed")
                            and first_address.full_address_computed is not None
                        ):
                            key = first_address.full_address_computed()
                            if key not in addresses:
                                addresses[key] = 1
                            else:
                                addresses[key] += 1
                else:
                    if self.address and self.address is not None:
                        key = self.address.full_address()
                        addresses[key] = 1

            for key in addresses:
                if addresses[key] == 1:
                    s += f'{key} | '
                else:
                    s += f'({addresses[key]}) {key} | '
            if s:
                return s[:-2]
            else:
                return s
        except NoValuesFetched:
            return "No line items on this order!!"

    def calculated_container_cost(self) -> float:
        s = 0
        try:
            for line_item in self.line_items:
                s += line_item.container_cost()
        except NoValuesFetched:
            return 0

        return s

    def calculated_shipping_cost(self) -> float:
        s = 0
        try:
            for line_item in self.line_items:
                s += 0 if line_item.shipping_cost is None else line_item.shipping_cost
        except NoValuesFetched:
            return 0

        return s

    def calculated_rent_balance(self) -> float:
        s = 0
        try:
            today = datetime.now(timezone.utc)
            current_and_overdue_rent_periods: List[RentPeriod] = [
                rent_period
                for rent_period in self.rent_periods
                if rent_period.start_date is None
                or rent_period.end_date is None
                or rent_period.start_date <= today
                and today <= rent_period.end_date
                or today >= rent_period.end_date
            ]

            for rent_period in current_and_overdue_rent_periods:
                s += rent_period.calculated_rent_period_total_balance()
        except NoValuesFetched:
            return 0

        return s

    def calculated_current_overdue_rent_periods(self):
        s = []
        try:
            today = datetime.now(timezone.utc)
            s = [
                rent_period
                for rent_period in self.rent_periods
                if rent_period.start_date is None
                or rent_period.end_date is None
                or rent_period.start_date <= today
                and today <= rent_period.end_date
                or today >= rent_period.end_date
            ]
        except NoValuesFetched:
            return s

        return s

    def calculated_paid_successfully_by_credit_card(self) -> bool:
        s = 0
        try:
            for credit_card in self.credit_card.related_objects:
                if (
                    credit_card.response_from_gateway
                    and credit_card.response_from_gateway.get('transactionResponse', {}).get('responseCode') == '1'
                ):
                    payment_amount = Decimal(credit_card.response_from_gateway.get('payment_amount', 0))

                    if self.rent_periods.related_objects:
                        for rent_period in self.rent_periods.related_objects:
                            s = Decimal(rent_period.amount_owed) + Decimal(rent_period.calculated_rent_period_tax())
                            for fee in rent_period.rent_period_fees:
                                s += Decimal(fee.fee_amount)

                            if abs(payment_amount - s) < 2:
                                return True

                        # TODO: multiple rent periods paid at the same time, backtracking?
                    else:
                        s = self.calculated_total_price()
                        if payment_amount >= s:
                            return True

                        # TODO: multiple partial ammounts, backtracking?
        except NoValuesFetched:
            return False

        return False

    def calculated_paid_date_rental(self) -> Optional[datetime]:
        try:
            if (
                self.type == 'RENT'
                and len(self.rent_periods) > 0
                and len(self.rent_periods[0].transaction_type_rent_period) > 0
            ):
                return self.rent_periods[0].transaction_type_rent_period[-1].created_at
            else:
                return self.paid_at

        except NoValuesFetched:
            return self.paid_at

    def calculated_signed_date(self) -> Optional[datetime]:
        try:
            if len(self.order_contract) > 0:
                for order_contract in self.order_contract:
                    if order_contract.status == "contract-signed" and not order_contract.meta_data.get("data", {}).get(
                        "contract", {}
                    ).get("title", "").lower().endswith("pay on delivery contract"):
                        return order_contract.modified_at
            else:
                return None

        except NoValuesFetched:
            return None

    def calculated_paid_in_full_date(self) -> Optional[datetime]:
        try:
            if self.transaction_type_order:
                most_recent_transaction = max(self.transaction_type_order, key=lambda x: x.transaction_effective_date)
                if self.calculated_remaining_order_balance() == 0:
                    return most_recent_transaction.transaction_effective_date
            return None
        except NoValuesFetched:
            return None
        except Exception:
            return None

    def calculated_order_tax_balance(self) -> Optional[Decimal]:
        try:
            if not self.tax_balance:
                return 0

            remaining_balance: Decimal
            # just finding the most recent record in this group
            most_recent_balance: TaxBalance = max(self.tax_balance, key=lambda x: x.created_at)

            remaining_balance = most_recent_balance.balance
            return remaining_balance
        except NoValuesFetched:
            return 0

    def calculated_order_subtotal_balance(self) -> Optional[Decimal]:
        try:
            if not self.subtotal_balance:
                return 0

            remaining_balance: Decimal
            # just finding the most recent record in this group
            most_recent_balance = max(self.subtotal_balance, key=lambda x: x.created_at)

            remaining_balance = most_recent_balance.balance
            return remaining_balance
        except NoValuesFetched:
            return 0

    def calculated_order_fees_taxable_balance(self) -> Optional[Decimal]:
        try:
            if not self.fees:
                return 0
            remaining_balance = Decimal(0)
            for fee in self.fees:
                if fee.calculated_is_taxable():
                    remaining_balance += Decimal(fee.calculated_remaining_balance())
            return remaining_balance
        except NoValuesFetched:
            return 0

    def calculated_order_fees_balance(self) -> Optional[Decimal]:
        try:
            if not self.order_fee_balance:
                return 0

            fee_ids = set()
            for ofb in self.order_fee_balance:
                fee_ids.add(ofb.fee.id)

            sum_balances = 0
            for fee_id in fee_ids:
                most_recent_balance = max(
                    [x for x in self.order_fee_balance if x.fee.id == fee_id], key=lambda x: x.created_at
                )
                sum_balances += most_recent_balance.remaining_balance

            return sum_balances
        except Exception:
            return 0

    def calculated_order_tax_rate(self) -> Optional[Decimal]:
        try:
            if not self.tax_balance:
                return 0

            oldest_balance: TaxBalance = min(self.tax_balance, key=lambda x: x.created_at)

            tax_rate = oldest_balance.tax_rate
            return tax_rate
        except NoValuesFetched:
            return 0

    def calculated_is_manager(self) -> Optional[bool]:
        try:
            if hasattr(self.user, 'assistant') and self.user.assistant is not None:
                return False
            else:
                return True
        except NoValuesFetched:
            return False

    def calculated_delivered_at(self) -> Optional[datetime]:
        if self.type == "RENT":
            try:
                rent_periods = sorted(self.rent_periods, key=lambda x: x.start_date)
                if (len(rent_periods)) == 0:
                    return None
                return rent_periods[0].start_date
            except NoValuesFetched:
                return None
        return self.delivered_at

    def calculated_accessory_commission(self) -> Optional[Decimal]:
        try:
            if not self.type != 'PURCHASE_ACCESSORY':
                return 0
            if hasattr(self.user, "commission"):
                commissions_rates = self.user.commission

                sorted_items = sorted(commissions_rates, key=lambda x: x.commission_effective_date)

                intervals = []
                for i in range(len(sorted_items)):
                    start_date = sorted_items[i].commission_effective_date
                    end_date = (
                        sorted_items[i + 1].commission_effective_date - timedelta(days=1)
                        if i < len(sorted_items) - 1
                        else datetime(9999, 12, 31)
                    )
                    rate = sorted_items[i].accessory_commission_rate

                    intervals.append({'start_date': start_date, 'end_date': end_date, 'rate': rate})

                subtotal = 0
                for item in self.line_items:
                    subtotal = item.revenue + item.shipping_revenue

                for i in intervals:
                    if i['start_date'] <= self.delivered_at and i['end_date'] > self.delivered_at:
                        return i['rate'] * subtotal
            else:
                return 0

        except NoValuesFetched:
            return 0

    # def calculated_total_rental_paid_excluding_shipping(self) -> Optional[Decimal]:
    #     rent_periods: Union[List[RentPeriod], None] = self.rent_periods
    #     if rent_periods is None:
    #         return Decimal(0)
    #     return sum([rent_period.calculated_rent_period_total_balance() for rent_period in rent_periods])

    class Meta:
        table = "order"

    def __str__(self):
        return f"{self.display_order_id}"


# @post_save(Order)
# async def signal_post_save(
#     sender: "Type[Order]",
#     instance: Order,
#     created: bool,
#     using_db: "Optional[BaseDBAsyncClient]",
#     update_fields: List[str],
# ) -> None:
#     logger.info(sender, instance, using_db, created, update_fields)

#     OrderOut = pydantic_model_creator(
#         cls=Order,
#         name="OrderOut",
#         exclude=(
#             "account",
#             "customer.account",
#             "customer.account_id",
#             "user.account",
#             "user.team_member_of",
#             "user.team_members",
#         )
#     )
#     if created:
#        order_out = await OrderOut.from_tortoise_orm(instance)
#        await send_event(instance.account_id, instance.id, make_json_serializable(order_out.dict()), "order")
