# Python imports
from decimal import Decimal
from typing import Any, Dict, List, Optional

# Pip imports
from loguru import logger
from tortoise import fields, models
from tortoise.exceptions import NoValuesFetched
from tortoise.queryset import QuerySet

# Internal imports
from src.database.models.rent_period_balance import RentPeriodBalance
from src.database.models.rent_period_fee_balance import RentPeriodFeeBalance
from src.database.models.rent_period_tax import RentPeriodTax
from src.database.models.rent_period_tax_balance import RentPeriodTaxBalance
from src.database.models.rent_period_total_balance import RentPeriodTotalBalance


class RentPeriod(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    start_date = fields.DatetimeField(null=True)
    end_date = fields.DatetimeField(null=True)
    amount_owed = fields.DecimalField(max_digits=10, decimal_places=2)
    order = fields.ForeignKeyField("models.Order", related_name="rent_periods", index=True)
    pdf_url = fields.TextField(null=True)

    class PydanticMeta:
        exclude = ["order.account", "order"]
        computed = [
            "calculated_rent_period_fee_balance",
            "calculated_rent_period_balance",
            "calculated_rent_period_tax",
            "calculated_rent_period_total_balance",
            "calculated_rent_period_sub_total_balance_excluding_taxable_fees",
            "calculated_rent_period_tax_without_downpayment",
            "calculated_rent_period_tax_per_item",
            "calculated_total_paid",
            "calculated_down_payment_fees",
            "calculated_rent_period_tax_balance",
            "calculated_rent_period_fees",
            "calculated_rent_period_display_dates",
            "calculated_total_amount",
            "calculated_rent_period_balance_with_tax",
            "calculated_rent_period_fee_balance_with_tax",
        ]

    def calculated_total_amount(self) -> Optional[Decimal]:
        try:
            return self.amount_owed + self.calculated_rent_period_fees() + self.calculated_rent_period_tax()
        except NoValuesFetched:
            return 0

    def calculated_rent_period_tax_balance(self) -> Optional[Decimal]:
        try:
            if not self.rent_period_tax_balance:
                return 0

            remaining_balance: Decimal
            # just finding the most recent record in this group
            most_recent_balance: RentPeriodFeeBalance = max(self.rent_period_tax_balance, key=lambda x: x.created_at)

            remaining_balance = most_recent_balance.balance
            return remaining_balance
        except NoValuesFetched:
            return 0

    def calculated_rent_period_display_dates(self) -> Optional[str]:
        try:
            if self.start_date and self.end_date:
                return f"{self.start_date.strftime('%m/%d/%y')} - {self.end_date.strftime('%m/%d/%y')}"
            else:
                return None
        except NoValuesFetched:
            return None

    def calculated_rent_period_fees(self) -> Optional[Decimal]:
        try:
            return sum([x.fee_amount for x in self.rent_period_fees])
        except NoValuesFetched:
            return 0

    def calculated_rent_period_fee_balance(self) -> Optional[Decimal]:
        try:
            if not self.rent_period_fee_balances:
                return 0

            remaining_balance: Decimal
            # just finding the most recent record in this group
            most_recent_balance: RentPeriodFeeBalance = max(self.rent_period_fee_balances, key=lambda x: x.created_at)

            remaining_balance = most_recent_balance.remaining_balance
            return remaining_balance
        except NoValuesFetched:
            return 0

    def calculated_rent_period_balance(self) -> Optional[Decimal]:
        try:
            if not self.rent_period_balances:
                return 0
            remaining_balance: Decimal
            # just finding the most recent record in this group
            most_recent_balance: RentPeriodBalance = max(self.rent_period_balances, key=lambda x: x.created_at)

            remaining_balance = most_recent_balance.remaining_balance
            return remaining_balance
        except NoValuesFetched:
            return 0

    def calculated_total_paid(self) -> Optional[Decimal]:
        try:
            if not self.rent_period_total_balances:
                return Decimal(0)

            total_paid = Decimal(0)
            previous_balance = self.rent_period_total_balances[0].remaining_balance

            for balance in self.rent_period_total_balances[1:]:
                if balance.remaining_balance < previous_balance:
                    total_paid += previous_balance - balance.remaining_balance
                previous_balance = balance.remaining_balance

            return total_paid
        except NoValuesFetched:
            return Decimal(0)

    def calculated_rent_period_tax(self) -> Optional[Decimal]:
        try:
            if not self.rent_period_taxes:
                return 0
            tax_amount: Decimal
            # just finding the most recent record in this group
            most_recent_tax: RentPeriodTax = max(self.rent_period_taxes, key=lambda x: x.created_at)

            tax_amount = most_recent_tax.tax_amount
            return tax_amount
        except NoValuesFetched:
            return 0

    def calculated_down_payment_fees(self) -> Optional[Decimal]:
        downpayment = Decimal(0.00)
        try:
            for rent_fee in self.rent_period_fees:
                if rent_fee.fee_type == "PICK_UP" or rent_fee.fee_type is None or rent_fee.fee_type == "DROP_OFF":
                    downpayment += rent_fee.fee_amount
        except NoValuesFetched:
            return 0
        return downpayment

    def calculated_rent_period_tax_without_downpayment(self) -> Optional[Decimal]:
        try:
            if not self.rent_period_taxes:
                return 0
            downpayment = 0
            for rent_fee in self.rent_period_fees:
                if isinstance(rent_fee.type, QuerySet):
                    continue
                if rent_fee.type.name == "DROP_OFF" or rent_fee.type.name == "PICK_UP":
                    downpayment += rent_fee.fee_amount

            tax_amount: Decimal
            # just finding the most recent record in this group
            most_recent_tax: RentPeriodTax = max(self.rent_period_taxes, key=lambda x: x.created_at)

            if not downpayment:
                tax_amount = most_recent_tax.tax_amount
            else:
                tax_amount = (
                    Decimal(most_recent_tax.tax_amount)
                    * Decimal(self.amount_owed)
                    / Decimal(self.amount_owed + downpayment)
                )
            return tax_amount
        except NoValuesFetched:
            return 0

    def calculated_rent_period_balance_with_tax(self) -> Optional[Decimal]:
        tax_amount = self.calculated_rent_period_tax()
        res = self.calculated_rent_period_sub_total_balance_excluding_taxable_fees()
        if res == 0:
            return 0
        tax_rate = tax_amount / res

        return self.calculated_rent_period_balance() * (1 + tax_rate)

    def calculated_rent_period_fee_balance_with_tax(self) -> Optional[Decimal]:
        tax_amount = self.calculated_rent_period_tax()
        res = self.calculated_rent_period_sub_total_balance_excluding_taxable_fees()
        if res == 0:
            return 0
        tax_rate = tax_amount / res
        taxable_fee_balance = 0
        for rent_fee in self.rent_period_fees:
            if hasattr(rent_fee, 'type') and hasattr(rent_fee.type, 'is_taxable') and rent_fee.type.is_taxable:
                taxable_fee_balance += rent_fee.fee_amount

        not_taxable_fee_balance = 0
        for rent_fee in self.rent_period_fees:
            if hasattr(rent_fee, 'type') and hasattr(rent_fee.type, 'is_taxable') and not rent_fee.type.is_taxable:
                not_taxable_fee_balance += rent_fee.fee_amount

        return taxable_fee_balance * (1 + tax_rate) + not_taxable_fee_balance

    def calculated_rent_period_tax_per_item(self) -> Optional[List[Dict[str, Any]]]:
        try:
            if self.calculated_rent_period_fee_balance() > 0:
                tax_amount = self.calculated_rent_period_tax()
                calculated_rent_period_balance = self.calculated_rent_period_balance()

                # Validate calculated_rent_period_balance
                if calculated_rent_period_balance <= 0:
                    return [{"fee_tax": 0, "fee_id": None}]

                # Validate tax_amount
                if tax_amount is None or tax_amount < 0:
                    return [{"fee_tax": 0, "fee_id": None}]

                # Ensure rent_period_fees is valid
                if not self.rent_period_fees:
                    return [{"fee_tax": 0, "fee_id": None}]

                # get tax rate
                res = self.calculated_rent_period_sub_total_balance_excluding_taxable_fees()
                if res == 0:
                    return 0
                tax_rate = tax_amount / res

                fee_taxes = []
                for rent_fee in self.rent_period_fees:
                    if rent_fee.type.is_taxable:
                        if rent_fee.fee_amount is None or rent_fee.fee_amount < 0:
                            raise ValueError("Fee amount must be a non-negative number.")

                        d = {
                            "fee_tax": tax_rate * rent_fee.fee_amount,
                            "fee_id": rent_fee.id,
                        }
                        fee_taxes.append(d)

                return fee_taxes

            return [{"fee_tax": 0, "fee_id": None}]
        except Exception as e:
            logger.error(f"Error calculating rent period tax per item: {e}")
            return [{"fee_tax": 0, "fee_id": None}]

    def calculated_rent_period_total_balance(self) -> Optional[Decimal]:
        try:
            most_recent_tax_balance: RentPeriodTaxBalance = (
                max(self.rent_period_tax_balance, key=lambda x: x.created_at) if self.rent_period_tax_balance else 0
            )

            most_recent_rent_balance: RentPeriodBalance = (
                max(self.rent_period_balances, key=lambda x: x.created_at) if self.rent_period_balances else 0
            )

            most_recent_rent_fee_balance: RentPeriodFeeBalance = (
                max(self.rent_period_fee_balances, key=lambda x: x.created_at) if self.rent_period_fee_balances else 0
            )

            # return most_recent_tax_balance.balance + most_recent_rent_balance.remaining_balance + most_recent_rent_fee_balance.remaining_balance
            # check each prop to see what type it is and then add the value
            total_balance = 0
            if isinstance(most_recent_tax_balance, RentPeriodTaxBalance):
                total_balance += most_recent_tax_balance.balance
            if isinstance(most_recent_rent_balance, RentPeriodBalance):
                total_balance += most_recent_rent_balance.remaining_balance
            if isinstance(most_recent_rent_fee_balance, RentPeriodFeeBalance):
                total_balance += most_recent_rent_fee_balance.remaining_balance

            if total_balance <= 0.005:
                return 0
            return total_balance

        except NoValuesFetched:
            return 0

    def calculated_rent_period_sub_total_balance_excluding_taxable_fees(self) -> Optional[Decimal]:
        try:
            if not self.rent_period_total_balances:
                return 0
            remaining_balance: Decimal
            # just finding the most recent record in this group
            most_recent_balance: RentPeriodTotalBalance = max(
                self.rent_period_total_balances, key=lambda x: x.created_at
            )

            remaining_balance = most_recent_balance.remaining_balance

            # subtract tax amount
            tax_amount = self.calculated_rent_period_tax() or 0
            remaining_balance -= tax_amount

            # subtract taxable fees
            for rent_fee in self.rent_period_fees:
                if hasattr(rent_fee, 'type') and hasattr(rent_fee.type, 'is_taxable') and not rent_fee.type.is_taxable:
                    remaining_balance -= rent_fee.fee_amount

            return remaining_balance
        except NoValuesFetched:
            return 0

    class Meta:
        table = "rent_period"

    def __str__(self):
        return f"{self.start_date} - {self.end_date}: {self.amount_owed}"
