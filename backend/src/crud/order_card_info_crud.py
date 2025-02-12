# Python imports
from datetime import date, datetime
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.order_credit_card import OrderCreditCard
from src.schemas.order_credit_card import OrderCreditCardInSchema, OrderCreditCardOutSchema


class OrderCreditCardCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OrderCreditCardOutSchema
        self.create_schema = OrderCreditCardInSchema
        self.db_model = OrderCreditCard
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
        )

    async def get_all_between_dates(self, account_id: int, date_start: date, date_end: date) -> List[Model]:
        if self.has_account_id():
            query = self.db_model.filter(
                account_id=account_id,
                created_at__range=(
                    datetime.combine(date_start, datetime.min.time()),
                    datetime.combine(date_end, datetime.max.time()),
                ),
            ).order_by("-created_at")
        else:
            query = self.db_model.filter(
                created_at__range=(
                    datetime.combine(date_start, datetime.min.time()),
                    datetime.combine(date_end, datetime.max.time()),
                )
            ).order_by("-created_at")
        return await self.schema.from_queryset(query)

    async def get_by_id(self, id: str):
        return await self.db_model.filter(id=id).first()

    async def get_all_between_dates_including_order(
        self, account_id: int, date_start: date, date_end: date, purchase_type: str
    ) -> List[Model]:
        query = (
            await OrderCreditCard.filter(
                created_at__range=(
                    datetime.combine(date_start, datetime.min.time()),
                    datetime.combine(date_end, datetime.max.time()),
                )
            )
            .all()
            .prefetch_related(
                "order",
                "order__fees",
                "order__line_items",
                "order__line_items__inventory",
                "order__fees__type",
                "order__order_tax",
                "order__customer",
                "order__single_customer",
                "order__misc_cost",
                "order__line_items__inventory",
                "order__total_order_balance",
                "order__order_tax",
                "order__transaction_type_order",
                "order__credit_card",
                "order__rent_periods",
            )
            .order_by("-created_at")
        )
        query = list(filter(lambda x: x.order.account_id == account_id, query))

        query = list(filter(lambda x: response_approved(x.response_from_gateway), query))

        return {"order_credit_cards": query, "purchase_type": purchase_type}


def response_approved(x):
    if (
        x.get('transactionResponse', {}).get('messages', [{}])[0].get("description", "")
        == "This transaction has been approved."
    ):
        return True
    return False


order_credit_card_crud = OrderCreditCardCrud()
