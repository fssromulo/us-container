# ...
# Python imports
from typing import List, Optional

# Pip imports
from tortoise.models import Model
from datetime import datetime
from decimal import Decimal

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.rent_period import RentPeriod
from src.database.models.rent_period_balance import RentPeriodBalance
from src.crud.rent_period_balance_crud import rent_period_balance_crud
from src.schemas.rent_period import RentPeriodIn, RentPeriodOut
from src.schemas.rent_period_balance import RentPeriodBalanceIn
from src.schemas.rent_period_total_balance import RentPeriodTotalBalanceIn
from src.crud.rent_period_total_balance_crud import rent_period_total_balance_crud
from src.crud.rent_period_tax_balance_crud import rent_period_tax_balance_crud, RentPeriodTaxBalance, RentPeriodTaxBalanceIn
from src.crud.tax_crud import tax_crud
from src.crud.order_crud import order_crud
from src.crud.rent_period_tax_crud import RentPeriodTax, rent_period_tax_crud, RentPeriodTaxIn


class RentPeriodCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = RentPeriodOut
        self.create_schema = RentPeriodIn
        self.update_schema = RentPeriodIn
        self.db_model = RentPeriod

    async def get_one(self, rent_period_id: str) -> Model:
        model = await self.db_model.filter(id=rent_period_id).first()

        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_one_without_exception(self, rent_period_id: str) -> Optional[Model]:
        model = await self.db_model.filter(id=rent_period_id).first()

        if model:
            return await RentPeriodOut.from_tortoise_orm(model)
        return None

    async def delete_one(self, rent_period_id: str):
        await self.db_model.filter(id=rent_period_id).delete()

    async def remove_all_from(self, order_id:str, move_out_date: datetime, monthly_owed: Decimal = 0.00, move_out_type: str = "Single"):
        model = await self.db_model.filter(order_id=order_id).order_by("-created_at").first()
        model_start = await self.db_model.filter(order_id=order_id).order_by("created_at").first()
        if move_out_type == 'All':
            return await self.db_model.filter(order_id=order_id, start_date__gt=move_out_date).delete()
        else:
            if model.amount_owed <= monthly_owed and model_start.amount_owed <= monthly_owed:
                return await self.db_model.filter(order_id=order_id, start_date__gt=move_out_date).delete()
            else :
                order = await order_crud.get_one(order_id)
                
                tax_states = [li.inventory.container_inventory_address.state for li in order.line_items if li.inventory and li.inventory.container_inventory_address]
                if not tax_states:
                    tax_states = [order.customer.state]


                if tax_states:
                    tax_rate = await tax_crud.get_tax_rate(order.account_id, tax_states[0])
                else:
                    tax_rate = 0.0
                rent_periods_query_set = self.db_model.filter(order_id=order_id, start_date__gt=move_out_date).all()
                rent_periods = await self.schema.from_queryset(rent_periods_query_set)

                period_update: List[RentPeriod] = []
                period_balance: List[RentPeriodBalanceIn] = []
                tax_balance: List[RentPeriodTaxBalance] = []
                tax: List[RentPeriodTax] = []
                period_total_balance: List[RentPeriodTotalBalanceIn] = []
                for period in rent_periods:
                    amount_owed = period.amount_owed - monthly_owed
                    if(amount_owed < 0):
                        amount_owed = 0
                    period_update.append(RentPeriod(amount_owed=amount_owed))
                    # This should reflect in the period balance as well
                    period_balance.append(RentPeriodBalanceIn(
                        remaining_balance=period.calculated_rent_period_balance - amount_owed, rent_period_id=period.id
                    ))
                    period_total_balance.append(RentPeriodTotalBalanceIn(
                        remaining_balance=period.calculated_rent_period_total_balance  - (amount_owed + tax_rate * amount_owed), rent_period_id=period.id
                    ))
                    tax_balance.append(RentPeriodTaxBalanceIn(balance=period.calculated_rent_period_tax_balance -tax_rate*amount_owed, tax_rate=0,rent_period_id=period.id))
                    tax.append(RentPeriodTaxIn(tax_amount=period.calculated_rent_period_tax  - tax_rate * amount_owed,rent_period_id=period.id))
                res = None
                if len(period_update) > 0:
                    res = await self.db_model.bulk_update(period_update, ['amount_owed'], len(period_update))
                    await rent_period_balance_crud.bulk_create(period_balance, len(period_balance))
                    await rent_period_total_balance_crud.bulk_create(period_total_balance, len(period_total_balance))
                    await rent_period_tax_balance_crud.bulk_create(tax_balance, len(tax_balance))
                    await rent_period_tax_crud.bulk_create(tax, len(tax))

                return res

    async def delete_moved_out(self, order_id:str, move_out_date: datetime):
        # Delete all moved out
        return await self.db_model.filter(order_id=order_id, start_date__gt=move_out_date, amount_owed=Decimal('0.00')).delete()

# class RentPeriodBalance(models.Model):
#     id = fields.UUIDField(pk=True)
#     created_at = fields.DatetimeField(auto_now_add=True)
#     modified_at = fields.DatetimeField(auto_now=True)
#     remaining_balance = fields.DecimalField(max_digits=10, decimal_places=2)
#     rent_period = fields.ForeignKeyField("models.RentPeriod", related_name="rent_period_balances", index=True)

    async def get_all_by_order_id(self, order_id: str):
        query = self.db_model.filter(order_id=order_id).order_by("start_date")
        return await self.schema.from_queryset(query)

    async def update(self, rent_period_id: str, model: Model) -> Model:
        if isinstance(model, self.update_schema):
            model = model.dict(exclude_unset=True)
            query = self.db_model.filter(id=rent_period_id)
            await query.update(**model)
            return await self.schema.from_queryset_single(self.db_model.get(id=rent_period_id))


rent_period_crud = RentPeriodCRUD()
