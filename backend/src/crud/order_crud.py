# Python imports
from datetime import datetime, timedelta
from typing import Any, Dict, List, cast

# Pip imports
from loguru import logger
from tortoise.expressions import Q
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.partial_order_crud import CustomOrderDTO, map_order_to_line_item_order_dto
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.customer.order_customer import OrderCustomer
from src.database.models.orders.order import Order
from src.database.models.transaction_type import TransactionType
from src.schemas.orders import OrderIn, OrderInUpdate, OrderOut, OrderSearchFilters, PublicOrderOut, RankingOrderOut
from src.utils.convert_time import convert_from_mountain_to_utc
from src.utils.update_cache import prepare_order_cache_swap

from ._types import PAGINATION


class OrderCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OrderOut
        self.public_schema = PublicOrderOut
        self.rankings_schema = RankingOrderOut
        self.create_schema = OrderIn
        self.update_schema = OrderInUpdate
        self.db_model = Order
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=200,
        )

    async def get_one(self, item_id: str, is_public=False) -> Model:
        model = await self.db_model.filter(id=item_id).filter(is_archived=False).first()
        if model:
            if is_public:
                return await self.public_schema.from_tortoise_orm(model)
            else:
                return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_orders_by_account_and_date_range(self, account_id, start_date, end_date):
        return await self.db_model.filter(account_id=account_id, paid_at__gte=start_date, paid_at__lte=end_date).filter(
            is_archived=False
        )

    async def updated_contracts_sent(self, order_id: str) -> Model:
        model = await self.db_model.filter(id=order_id).filter(is_archived=False).first()
        if model:
            if model.pay_on_delivery_contract_sent_count is None:
                model.pay_on_delivery_contract_sent_count = 1
            else:
                model.pay_on_delivery_contract_sent_count = model.pay_on_delivery_contract_sent_count + 1
            await self.db_model.filter(id=order_id).filter(is_archived=False).update(
                pay_on_delivery_contract_sent_count=model.pay_on_delivery_contract_sent_count
            )
        else:
            raise NOT_FOUND
        return

    async def get_one_without_exception(self, item_id: str, is_public=False) -> Model:
        model = await self.db_model.filter(id=item_id).filter(is_archived=False).first()
        if model:
            if is_public:
                return await self.public_schema.from_tortoise_orm(model)
            else:
                return await self.schema.from_tortoise_orm(model)

        return None

    async def get_order_by_container_id(self, container_id):
        result = await self.db_model.filter(line_items__inventory_id=container_id).filter(is_archived=False)
        return result

    async def get_by_latest_id(self, item_id: int, is_public=False) -> Model:
        # current date subtracted by 2 days
        date = datetime.now() - timedelta(hours=100)
        model = (
            await self.db_model.filter(account_id=item_id)
            .filter(created_at__gte=date)
            .filter(is_archived=False)
            .order_by("-created_at")
            .first()
        )
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_one_by_inventory(self, inventory_id: str) -> Model:
        model = await self.db_model.filter(line_items__inventory_id=inventory_id).filter(is_archived=False).first()
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_by_inventory_ids(self, inventory_ids: List[str]) -> Model:
        query = self.db_model.filter(line_items__inventory_id__in=inventory_ids)
        query = query.filter(is_archived=False)
        query = query.order_by("-line_items__inventory__created_at")
        return await self.schema.from_queryset(query)

    async def get_by_inventory(
        self,
        status: str,
        order_type: str,
        account_id: int,
        pagination: PAGINATION,
    ) -> Model:
        skip, limit = pagination.get("skip"), pagination.get("limit")
        query = self.db_model.filter(account_id=account_id)
        if status.upper() == "DELIVERED":
            query = query.filter(status=status)
        else:
            query = query.filter(status__not=status)
        if order_type != 'ALL':
            query = query.filter(type=order_type)
        query = query.filter(line_items__inventory_id__not_isnull=True)
        query = query.filter(is_archived=False)
        query = query.order_by("-line_items__inventory__created_at")
        query = query.offset(cast(int, skip))
        if limit:
            query = query.limit(limit)

        logger.info(query.sql())

        return await self.schema.from_queryset(query)

    async def get_one_by_display_id(self, account_id: int, item_id: int) -> Model:
        model = (
            await self.db_model.filter(account_id=account_id)
            .filter(display_order_id=item_id)
            .filter(is_archived=False)
            .first()
        )
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_all_by_user_id(
        self,
        account_id,
        user_id,
    ) -> Dict[str, Any]:
        query = self.db_model.all().filter(account_id=account_id).filter(user_id=user_id).filter(is_archived=False)

        return await self.schema.from_queryset(query)

    async def get_all_by_single_customer_id(self, single_customer_id: str, account_id: int = None) -> List[Model]:
        query = (
            self.db_model.all()
            .filter(account_id=account_id)
            .filter(single_customer_id=single_customer_id)
            .filter(is_archived=False)
        )

        return await self.schema.from_queryset(query)

    async def get_all_by_email(self, email: str, account_id: int = None) -> List[Model]:
        if not account_id:
            order_customers = (
                await OrderCustomer.filter(email=email).filter(is_archived=False).prefetch_related("order")
            )
        else:
            order_customers = (
                await OrderCustomer.filter(account_id=account_id).filter(email=email).prefetch_related("order")
            )
        # Extract order ids from related orders

        order_ids = [order.id for order_customer in order_customers for order in order_customer.order]

        # Fetch Order instances with the extracted order ids
        orders = await Order.filter(id__in=order_ids, is_archived=False)

        return orders

    async def get_all_by_email_non_queryset(self, email: str, account_id: int = None) -> List[Model]:
        if not account_id:
            order_customers = (
                await OrderCustomer.filter(email=email).filter(is_archived=False).prefetch_related("order")
            )
        else:
            order_customers = (
                await OrderCustomer.filter(account_id=account_id).filter(email=email).prefetch_related("order")
            )
        # Extract order ids from related orders

        order_ids = [order.id for order_customer in order_customers for order in order_customer.order]

        # Fetch Order instances with the extracted order ids
        query = Order.filter(id__in=order_ids, is_archived=False)

        return await self.schema.from_queryset(query)

    async def update_without_schema_model(self, account_id: int, item_id: int, model: Model) -> Model:  # type: ignore
        model = model.dict(exclude_unset=True)
        if self.has_account_id():
            query = self.db_model.filter(account_id=account_id).filter(is_archived=False).filter(id=item_id)
        else:
            query = self.db_model.filter(id=item_id).filter(is_archived=False)
        await query.update(**model)
        return await self.schema.from_queryset_single(self.db_model.get(id=item_id))

    



    async def filter_rankings(
        self,
        account_id: int = None,
        user_ids=None,
        status=None,
        order_types=None,
        created_at=None,
        paid_at=None,
        signed_at=None,
        delivered_at=None,
        completed_at=None,
        start_date=None,
        end_date=None,
        pod_mode=True,
        pagination: PAGINATION = {},
    ) -> List[Model]:
        # skip, limit = pagination.get("skip"), pagination.get("limit")
        if start_date and end_date:
            # check type of start date and end date
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%m/%d/%y")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%m/%d/%y")

            #  set the time to midnight for start date
            # start_date = convert_from_mountain_to_utc(
            #    datetime_obj=start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            # )
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

            # set the time to 11:59:59 for end date
            # end_date = convert_from_mountain_to_utc(
            #    datetime_obj=end_date.replace(hour=23, minute=59, second=59, microsecond=0)
            # )
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
        q = self.db_model.filter(account_id=account_id)
        query_set = False
        if paid_at and signed_at:
            query_set = True
            q = q.filter(
                Q(paid_at__gte=start_date) & Q(paid_at__lte=end_date)
                | Q(signed_at__gte=start_date) & Q(signed_at__lte=end_date)
            )
        elif paid_at:
            query_set = True
            q = q.filter(paid_at__gte=start_date).filter(paid_at__lte=end_date)
        elif signed_at:
            query_set = True
            q = q.filter(signed_at__gte=start_date).filter(signed_at__lte=end_date)
        if delivered_at:
            query_set = True
            q = q.filter(delivered_at__gte=start_date).filter(delivered_at__lte=end_date)
        if user_ids:
            query_set = True
            q = q.filter(user_id__in=user_ids)
        if status:
            statuses = status.split(",")
            if 'To Deliver' in statuses:
                statuses.append("Paid")
                statuses.append("Pod")
                statuses.append("first_payment_received")
            query_set = True
            q = q.filter(status__in=statuses)
        if order_types:
            query_set = True
            q = q.filter(type__in=order_types.split(","))
        if not pod_mode:
            q = q.filter(signed_at__isnull=True)
        q = q.filter(is_archived=False)
        if not query_set:
            return []
        logger.info(q.sql())
        return await self.rankings_schema.from_queryset(q)
        # return await self.rankings_schema.from_queryset(q.all())

    async def set_schema_id(self, order_id, schema_id):
        return (
            await self.db_model.filter(id=order_id)
            .filter(is_archived=False)
            .update(customer_application_schema_id=schema_id)
        )

    async def get_all_profits_by_state(self, begin_date, end_date, account_id):
        query = (
            await self.db_model.filter(
                account_id=account_id,
                paid_at__gte=begin_date,
                paid_at__lte=end_date,
                status__in=['Delivered', 'Completed', 'Paid'],
            )
            .filter(is_archived=False)
            .all()
            .prefetch_related(
                "fees", "line_items", "fees__type", "line_items__inventory", "line_items__inventory__depot"
            )
            .select_related("address")
        )
        return query

    async def get_invoiced_orders_not_sent(self, account_id: int, user_id: str) -> List[Model]:
        query = self.db_model.filter(
            account_id=account_id,
            status__in=["Invoiced"],
            leadconnect_sent=False,
            user_id=user_id,
        ).filter(is_archived=False)
        return await self.schema.from_queryset(query)

    async def get_all_orders(self, begin_date, end_date, account_id, purchase_type):
        query = []

        if purchase_type == 'PURCHASE' or purchase_type == 'PURCHASE_ACCESSORY':

            query = (
                TransactionType.filter(
                    account_id=account_id,
                    transaction_effective_date__range=(
                        datetime.combine(begin_date, datetime.min.time()),
                        datetime.combine(end_date, datetime.max.time()),
                    ),
                )
                .all()
                .prefetch_related(
                    "order",
                    "order__fees",
                    "order__address",
                    "order__line_items",
                    "order__line_items__inventory",
                    "order__line_items__inventory_address__address",
                    "order__line_items__inventory_address",
                    "order__fees__type",
                    "order__order_tax",
                    "order__customer",
                    "order__single_customer",
                    "order__misc_cost",
                    "order__line_items__inventory",
                    "order__total_order_balance",
                    "order__order_tax",
                    "order__transaction_type_order",
                )
            )

            query = await query
            return {
                "transaction_types": [x for x in query if x.order and not x.order.is_archived],
                "purchase_type": purchase_type,
            }
        else:
            query = (
                TransactionType.filter(
                    account_id=account_id,
                    transaction_effective_date__range=(
                        datetime.combine(begin_date, datetime.min.time()),
                        datetime.combine(end_date, datetime.max.time()),
                    ),
                )
                .all()
                .prefetch_related(
                    "rent_period",
                    "rent_period__order",
                    "rent_period__order__address",
                    "rent_period__order__fees",
                    "rent_period__order__line_items",
                    "rent_period__order__line_items__inventory",
                    "rent_period__order__fees__type",
                    "rent_period__order__order_tax",
                    "rent_period__order__customer",
                    "rent_period__order__single_customer",
                    "rent_period__order__misc_cost",
                    "rent_period__order__line_items__inventory",
                    "rent_period__order__total_order_balance",
                    "rent_period__transaction_type_rent_period",
                    "rent_period__rent_period_taxes",
                    "rent_period__order__line_items__inventory_address__address",
                    "rent_period__order__line_items__inventory_address",
                    "credit_card_object",
                )
            )

            query = await query
            return {
                "transaction_types": [
                    x for x in query if x.rent_period and x.rent_period.order and not x.rent_period.order.is_archived
                ],
                "purchase_type": purchase_type,
            }

    async def orders_with_coupon_id(
        self,
        account_id: int = None,
        coupon_id: str = None,
        pagination: PAGINATION = {},
    ) -> Model:
        # skip, limit = pagination.get("skip"), pagination.get("limit")
        q = self.db_model.filter(account_id=account_id)
        return (
            await q.filter(coupon_code_order__coupon_id=coupon_id)
            .prefetch_related("coupon_code_order", "line_items")
            .all()
        )

    async def get_all_after_date_by_status(self, account_id: int, status: str, start_date) -> List[Model]:
        # Retrieve a queryset
        if status.lower() == "invoiced":
            queryset = (
                await self.db_model.filter(account_id=account_id)
                .filter(created_at__gte=start_date)
                .filter(status=status)
            )
        else:  # this will include paid, delivered, and completed
            queryset = (
                await self.db_model.filter(account_id=account_id)
                .filter(paid_at__gte=start_date)
                .filter(status__in=status.split(","))
            )
        return queryset

    async def update(self, account_id: int, item_id: int, model: Model) -> Model:  # type: ignore
        if isinstance(model, self.update_schema):
            model = model.dict(exclude_unset=True)
            if self.has_account_id():
                query = self.db_model.filter(account_id=account_id).filter(id=item_id)
            else:
                query = self.db_model.filter(id=item_id)

            old_order = await self.schema.from_queryset_single(self.db_model.get(id=item_id))
            await query.update(**model)
            new_order = await self.schema.from_queryset_single(self.db_model.get(id=item_id))

            await prepare_order_cache_swap(old_order, new_order, old_order.user.id, account_id)

            return new_order


order_crud = OrderCRUD()
