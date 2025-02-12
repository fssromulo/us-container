# Python imports
from datetime import datetime
from typing import Any, Dict, List, cast

# Pip imports
from loguru import logger
from tortoise.expressions import Q
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.orders.order import Order
from src.schemas.orders import CustomOrderDTO, LineItemOrderDTO, OrderOut, OrderSearchFilters, PartialOrderOut, dfc
from src.utils.convert_time import convert_from_mountain_to_utc

from ._types import PAGINATION


def map_order_to_line_item_order_dto(order: CustomOrderDTO):
    order_dict = order.dict()
    if order.customer:
        customer_dict = order.customer.dict()
    else:
        customer_dict = {}

    if order.address:
        address_dict = order.address.dict()
    else:
        address_dict = {}
    return_list = []

    for line_item in order.line_items:
        line_item_order_dto = LineItemOrderDTO()
        # add order level fields
        line_item_order_dto.display_delivered_at = (
            dfc(order_dict.get('delivered_at')) if order_dict.get('delivered_at') else None
        )
        line_item_order_dto.order_delivered_at = order_dict.get('delivered_at')
        line_item_order_dto.display_delivered_at = (
            dfc(order_dict.get('delivered_at')) if order_dict.get('delivered_at') else None
        )
        line_item_order_dto.display_completed_at = (
            dfc(order_dict.get('completed_at')) if order_dict.get('completed_at') else None
        )
        line_item_order_dto.order_completed_at = order_dict.get('completed_at')
        line_item_order_dto.display_paid_at = dfc(order_dict.get('paid_at')) if order_dict.get('paid_at') else None
        line_item_order_dto.order_calculated_paid_date_rental = (
            dfc(order_dict['calculated_paid_date_rental'])
            if order_dict['calculated_paid_date_rental']
            else line_item_order_dto.display_paid_at
        )
        line_item_order_dto.order_paid_at = order_dict.get('paid_at')
        line_item_order_dto.order_calculated_paid_in_full_date = order_dict['paid_at']
        line_item_order_dto.display_signed_at = (
            dfc(order_dict.get('signed_at')) if order_dict.get('signed_at') else None
        )
        line_item_order_dto.order_signed_at = line_item_order_dto.display_signed_at
        line_item_order_dto.order_created_at = order_dict.get('created_at')
        line_item_order_dto.display_created_at = dfc(order_dict.get('created_at'))
        line_item_order_dto.order_address = address_dict
        line_item_order_dto.order_agent = order_dict.get('user', {}).get('full_name')
        line_item_order_dto.order_is_autopay = order_dict.get('is_autopay')
        line_item_order_dto.order_payment_type = order_dict.get('payment_type')
        line_item_order_dto.order_estimated_profit = order_dict.get('estimated_profit')
        line_item_order_dto.order_calculated_order_tax = order_dict.get('calculated_order_tax')
        line_item_order_dto.order_calculated_total_price = order_dict.get('calculated_total_price')
        line_item_order_dto.order_calculated_monthly_subtotal = order_dict.get('calculated_monthly_subtotal')
        line_item_order_dto.order_calculated_rent_balance = order_dict.get('calculated_rent_balance')
        line_item_order_dto.order_note = list(map(lambda x: str(x), order_dict.get("note")))
        line_item_order_dto.order_display_order_id = order_dict.get('display_order_id')
        line_item_order_dto.order_has_accessories = (
            len([x for x in order.line_items if x.product_type == 'CONTAINER_ACCESSORY']) != 0
        )
        line_item_order_dto.order_has_containers = (
            len(
                [x for x in order.line_items if x.product_type == 'SHIPPING_CONTAINER' or x.product_type == 'CONTAINER']
            )
            != 0
        )

        line_item_order_dto.order_type = order_dict.get('type')
        # add customer level fields
        line_item_order_dto.customer_full_name = customer_dict.get('full_name')
        line_item_order_dto.customer_company_name = customer_dict.get('company_name')
        line_item_order_dto.customer_phone = customer_dict.get('phone')
        line_item_order_dto.customer_email = customer_dict.get('email')
        line_item_order_dto.order_single_customer = order_dict.get('single_customer')

        # add address level fields
        # line_item_order_dto.address = address_dict

        # potential driver level fields
        line_item_order_dto.line_item_potential_driver_id = (
            line_item.potential_driver.id if line_item.potential_driver else None
        )
        line_item_order_dto.line_item_inventory_id = line_item.inventory.id if line_item.inventory else None
        line_item_order_dto.line_item_inventory_container_release_number = (
            line_item.inventory.container_release_number if line_item.inventory else None
        )
        line_item_order_dto.line_item_inventory = line_item.inventory if line_item.inventory else None

        line_item_order_dto.line_item_id = line_item.id
        line_item_order_dto.line_item_scheduled_date = dfc(line_item.scheduled_date)
        line_item_order_dto.line_item_potential_date = dfc(line_item.potential_date)
        line_item_order_dto.line_item_driver = line_item.driver.company_name if line_item.driver else None
        line_item_order_dto.line_item_title = line_item.title
        line_item_order_dto.line_item_location = line_item.location
        line_item_order_dto.line_item_revenue = line_item.revenue
        line_item_order_dto.line_item_shipping_revenue = line_item.shipping_revenue
        line_item_order_dto.line_item_shipping_cost = line_item.shipping_cost
        line_item_order_dto.line_item_good_to_go = line_item.good_to_go
        line_item_order_dto.line_item_welcome_call = line_item.welcome_call
        line_item_order_dto.line_item_door_orientation = line_item.door_orientation
        line_item_order_dto.line_item_estimated_profit = line_item.estimated_profit
        line_item_order_dto.line_item_product_type = line_item.product_type
        line_item_order_dto.line_item_product_city = line_item.product_city
        return_list.append(line_item_order_dto.dict())
    return return_list


async def get_by_status_type(
    crud,
    account_id: int,
    status: str,
    order_type: str,
    user_ids: List[str],
    pagination: PAGINATION,
) -> Dict[str, Any]:
    skip, limit = pagination.get("skip"), 1000
    logger.info(status)
    order_by_date = "created_at"
    if status.upper() == "PAID":
        order_by_date = "paid_at"
    if status.upper() == "DELIVERED":
        order_by_date = "delivered_at"
    if status.upper() == "INVOICED":
        order_by_date = "created_at"
    if status.upper() == "COMPLETED":
        order_by_date = "completed_at"
    if status == 'First_Payment_Received':
        status = "first_payment_received"

    if status.upper() == "TO_DELIVER" and (order_type.lower() == "all" or order_type.lower() == "purchase"):
        order_by_date = "paid_at"

    logger.info(f"Order by by {order_by_date}")
    if status == 'first_payment_received':
        exploded_statuses = []
    else:
        exploded_statuses = status.split('_')

    # grab all of the orders by account_id
    query = crud.db_model.all().filter(account_id=account_id)

    # filter only for the given status(es)
    if len(exploded_statuses) > 1:
        status = " ".join(exploded_statuses)

    if status.upper() == "TO DELIVER":
        # The "To Deliver" status is computed status, one that is not found in the db, but
        # will compile all the Paid and Current statuses that have not been delivered yet
        if order_type.lower() == "all":
            query = query.filter(status__in=["Paid", "first_payment_received", "Pod"]).filter(delivered_at=None)
        elif order_type.lower() == 'rent':
            query = query.filter(status__in=["first_payment_received"]).filter(delivered_at=None)
        elif order_type.lower() == "purchase":
            query = query.filter(status__in=["Paid", "Pod", "Pod"]).filter(delivered_at=None)
        else:
            query = query.filter(status__in=["Paid", "first_payment_received", "Pod"]).filter(delivered_at=None)
    elif status.upper() == "ON RENT":
        if order_type.lower() == 'rent':
            query = query.filter(status__in=["Delinquent", "Delivered"]).filter(type="RENT")
        elif order_type.lower() == 'all':
            query = query.filter(status__in=["Delinquent", "Delivered"]).filter(type="RENT")
        else:
            return {
                "orders": [],
                "count": 0,
            }

    elif status.upper() == 'FULFILLED':
        query = query.filter(status__in=["Delivered", "Completed", "Driver Paid", "Delinquent"])
    elif status.upper() == "ALL ACTIVE":
        # The "To Deliver" status is computed status, one that is not found in the db, but
        # will compile all the Paid and Current statuses that have not been delivered yet
        query = query.filter(status__in=["Delinquent", "first_payment_received"]).filter(delivered_at=None)
    else:
        query = query.filter(status=status)

    query = query.filter(is_archived=False)

    if order_type.lower() != "all":
        query = query.filter(type=order_type)

    # grabbing any relevant additional filters
    if status.upper() == "COMPLETED":
        query = query.filter(completed_at__isnull=False)

    if user_ids:
        query = query.filter(user_id__in=user_ids)

    # order them by the appropriate date
    query = query.order_by(f"-{order_by_date}")

    # paginate them accordingly
    query = query.offset(cast(int, skip))

    count = await query.count()

    # then limit them based off of if one is passed
    if limit:
        query = query.limit(limit)

    query = query.prefetch_related("order_contract")

    return query, count


class PartialOrderCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = PartialOrderOut
        self.db_model = Order
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
        )

    async def search_orders_dto_mapping(
        self,
        account_id: int = None,
        order_ids: List[str] = None,
        display_order_ids: List[str] = None,
        city_region_map=None,
        city_pickup_region_map=None,
        pagination: PAGINATION = {},
        pod_mode=True,
        filters=None,
    ) -> Model:
        query = await self.search_orders_query(
            account_id=account_id,
            order_ids=order_ids,
            display_order_ids=display_order_ids,
            city_region_map=city_region_map,
            city_pickup_region_map=city_pickup_region_map,
            pod_mode=pod_mode,
            pagination=pagination,
            filters=filters,
        )

        if not query:
            return []

        query = query.prefetch_related(
            "line_items",
            "line_items__inventory",
            "address",
            "customer",
            "user",
            "line_items__driver",
            "line_items__potential_driver",
            "line_items__inventory__depot",
            "line_items__inventory__vendor",
            "single_customer",
            "single_customer__customer_contacts",
            "order_tax"
        )

        results = await query
        res: List[CustomOrderDTO] = [CustomOrderDTO.from_orm(order) for order in results]

        # Create a dictionary to store unique orders by `display_order_id`
        unique_orders = {}
        for order in res:
            if order.display_order_id not in unique_orders:
                unique_orders[order.display_order_id] = order

        # Retrieve only the unique orders
        res = list(unique_orders.values())

        mapped_result_list = []
        for order in res:
            mapped_result_list.extend(map_order_to_line_item_order_dto(order))

        return mapped_result_list

    async def search_orders(
        self,
        account_id: int = None,
        order_ids: List[str] = None,
        display_order_ids: List[str] = None,
        user_ids=None,
        regions=None,
        pickup_regions=None,
        status=None,
        order_types=None,
        display_order_id=None,
        created_at=None,
        paid_at=None,
        signed_at=None,
        delivered_at=None,
        completed_at=None,
        start_date=None,
        end_date=None,
        container_number=None,
        container_release_number=None,
        pickup=None,
        not_pickup=None,
        driver_id=None,
        container_sizes=None,
        not_driver_id=None,
        is_rush=False,
        not_rush=False,
        good_to_go=None,
        not_good_to_go=None,
        welcome_call=None,
        not_welcome_call=None,
        container_id=None,
        not_container_id=None,
        scheduled_date=None,
        not_schedule_date=None,
        potential_date=None,
        not_potential_date=None,
        potential_driver=None,
        not_potential_driver=None,
        city_region_map=None,
        city_pickup_region_map=None,
        location=None,
        tracking_number=None,
        container_types=None,
        container_condition=None,
        product_type=None,
        pod_mode=True,
        pagination: PAGINATION = {},
    ) -> Model:
        filters = OrderSearchFilters(
            statuses=status,
            order_types=order_types,
            searched_user_ids=user_ids,
            regions=regions,
            pickup_regions=pickup_regions,
            container_sizes=container_sizes,
            container_types=container_types,
            display_order_id=display_order_id,
            container_number=container_number,
            container_release_number=container_release_number,
            customer_name=None,
            customer_email=None,
            customer_phone=None,
            driver_id=driver_id,
            not_driver_id=not_driver_id,
            good_to_go=good_to_go,
            not_good_to_go=not_good_to_go,
            welcome_call=welcome_call,
            not_welcome_call=not_welcome_call,
            created_at=created_at,
            paid_at=paid_at,
            signed_at=signed_at,
            delivered_at=delivered_at,
            completed_at=completed_at,
            container_id=container_id,
            not_container_id=not_container_id,
            pickup=pickup,
            not_pickup=not_pickup,
            start_date=start_date,
            end_date=end_date,
            emulated_user_id=None,
            scheduled_date=scheduled_date,
            not_schedule_date=not_schedule_date,
            potential_date=potential_date,
            not_potential_date=not_potential_date,
            potential_driver=potential_driver,
            not_potential_driver=not_potential_driver,
            location=location,
            tracking_number=tracking_number,
            container_condition=container_condition,
            product_type=product_type,
            customer_company_name=None,
            is_rush=is_rush,
            not_rush=not_rush,
        )

        query = await self.search_orders_query(
            account_id=account_id,
            order_ids=order_ids,
            display_order_ids=display_order_ids,
            pod_mode=pod_mode,
            pagination=pagination,
            city_region_map=city_region_map,
            city_pickup_region_map=city_pickup_region_map,
            filters=filters,
        )

        return await OrderOut.from_queryset(query)

    async def search_orders_query(
        self,
        account_id=None,
        order_ids=None,
        display_order_ids=None,
        city_region_map=None,
        city_pickup_region_map=None,
        pod_mode=None,
        pagination={},
        filters: OrderSearchFilters = None,
    ) -> Model:
        if pagination:
            skip, limit = pagination.get("skip"), pagination.get("limit")

        if filters.start_date and filters.end_date:
            if isinstance(filters.start_date, str):
                start_date = datetime.strptime(filters.start_date, "%m/%d/%y")
            if isinstance(filters.end_date, str):
                end_date = datetime.strptime(filters.end_date, "%m/%d/%y")

            start_date = convert_from_mountain_to_utc(
                datetime_obj=start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            )
            end_date = convert_from_mountain_to_utc(
                datetime_obj=end_date.replace(hour=23, minute=59, second=59, microsecond=0)
            )

        q = self.db_model.filter(account_id=account_id)
        query_set = False

        if order_ids:
            query_set = True
            q = q.filter(id__in=order_ids)
        if display_order_ids:
            query_set = True
            q = q.filter(display_order_id__in=display_order_ids)
        if filters.created_at:
            query_set = True
            q = q.filter(created_at__gte=start_date).filter(created_at__lte=end_date)
        if filters.paid_at and filters.signed_at:
            query_set = True
            q = q.filter(
                Q(paid_at__gte=start_date) & Q(paid_at__lte=end_date)
                | Q(signed_at__gte=start_date) & Q(signed_at__lte=end_date)
            )
        elif filters.paid_at:
            query_set = True
            q = q.filter(paid_at__gte=start_date).filter(paid_at__lte=end_date)
        elif filters.signed_at:
            query_set = True
            q = q.filter(signed_at__gte=start_date).filter(signed_at__lte=end_date)
        if filters.delivered_at:
            query_set = True
            q = q.filter(delivered_at__gte=start_date).filter(delivered_at__lte=end_date)
        if filters.completed_at:
            query_set = True
            q = q.filter(completed_at__gte=start_date).filter(completed_at__lte=end_date)
        if filters.searched_user_ids:
            query_set = True
            q = q.filter(user_id__in=filters.searched_user_ids)
        if filters.container_number:
            query_set = True
            q = q.filter(line_items__inventory__container_number__icontains=filters.container_number)
        if filters.container_release_number:
            query_set = True
            q = q.filter(line_items__inventory__container_release_number__icontains=filters.container_release_number)
        if filters.statuses:
            statuses = filters.statuses.split(",")
            if 'To Deliver' in statuses:
                statuses.append("Paid")
                statuses.append("Pod")
                statuses.append("first_payment_received")
            query_set = True
            q = q.filter(status__in=statuses)
        if filters.order_types:
            query_set = True
            q = q.filter(type__in=filters.order_types.split(","))
        if filters.display_order_id:
            query_set = True
            q = q.filter(display_order_id=filters.display_order_id)
        if filters.is_rush:
            query_set = True
            q = q.filter(fees__fee_type='RUSH')
        if filters.not_rush:
            query_set = True
            q = q.filter(fees__fee_type__not='RUSH')

        # Line item filters
        if filters.pickup:
            query_set = True
            q = q.filter(line_items__shipping_revenue=0)
        if filters.not_pickup:
            query_set = True
            q = q.filter(line_items__shipping_revenue__gt=0)
        if filters.driver_id:
            query_set = True
            q = q.filter(line_items__driver_id__not_isnull=True)
        if filters.product_type and filters.product_type != "" and filters.product_type == 'SHIPPING_CONTAINER':
            query_set = True
            q = q.filter(
                Q(line_items__product_type__isnull=True) | Q(line_items__product_type__not="CONTAINER_ACCESSORY")
            )
        if filters.product_type and filters.product_type != "" and filters.product_type == 'CONTAINER_ACCESSORY':
            query_set = True
            q = q.filter(line_items__product_type__not_isnull=True)
            q = q.filter(line_items__product_type='CONTAINER_ACCESSORY')
        if filters.not_driver_id:
            query_set = True
            q = q.filter(line_items__driver_id__isnull=True)
        if filters.container_sizes:
            query_set = True
            q = q.filter(line_items__container_size__in=filters.container_sizes.split(","))
        if filters.container_types:
            query_set = True
            container_type_dict = {
                "standard": "standard" in filters.container_types,
                "high_cube": "high_cube" in filters.container_types,
                "double_door": "double_door" in filters.container_types,
                "portable": "portable" in filters.container_types,
            }
            container_type_dict = {key: value for key, value in container_type_dict.items() if value}
            q = q.filter(line_items__attributes__contains=container_type_dict)
        if filters.container_condition:
            query_set = True
            q = q.filter(line_items__condition=filters.container_condition)
        if filters.good_to_go:
            query_set = True
            q = q.filter(line_items__good_to_go__in=filters.good_to_go.split(","))
        if filters.welcome_call:
            query_set = True
            q = q.filter(line_items__welcome_call__in=filters.welcome_call.split(","))
        if filters.container_id:
            query_set = True
            q = q.filter(line_items__inventory_id__not_isnull=True)
        if filters.not_container_id:
            query_set = True
            q = q.filter(line_items__inventory_id__isnull=True)
        if filters.regions:
            query_set = True
            cities = []
            for region in filters.regions.split(","):
                cities.extend(city_region_map[region.upper()])
            q = q.filter(line_items__product_city__in=cities)
        if filters.pickup_regions:
            query_set = True
            cities = []
            for pickup_region in filters.pickup_regions.split(","):
                cities.extend(city_pickup_region_map[pickup_region.upper()])
            q = q.filter(line_items__product_city__in=cities)
        if filters.location:
            query_set = True
            location = filters.location.split(",")
            q = q.filter(line_items__product_city__in=location)
        if filters.tracking_number:
            query_set = True
            q = q.filter(line_items__other_inventory__tracking_number=filters.tracking_number)
        if filters.scheduled_date and filters.scheduled_date != "null":
            query_set = True
            q = q.filter(line_items__scheduled_date__not_isnull=True)
        if filters.not_schedule_date and filters.not_schedule_date != "null":
            query_set = True
            q = q.filter(line_items__scheduled_date__isnull=True)
        if filters.potential_date and filters.potential_date != "null":
            query_set = True
            q = q.filter(line_items__potential_date__not_isnull=True)
        if filters.not_potential_date and filters.not_potential_date != "null":
            query_set = True
            q = q.filter(line_items__potential_date__isnull=True)
        if filters.potential_driver and filters.potential_driver != "null":
            query_set = True
            q = q.filter(line_items__potential_driver_id__not_isnull=True)
        if filters.not_potential_driver and filters.not_potential_driver != "null":
            query_set = True
            q = q.filter(line_items__potential_driver_id__isnull=True)

        if not pod_mode:
            q = q.filter(signed_at__isnull=True)

        q = q.filter(Q(is_archived=False) | Q(is_archived__isnull=True))

        if not query_set:
            return []

        if pagination:
            q = q.offset(cast(int, skip))

        if filters.created_at:
            q = q.order_by("-created_at")
        elif filters.paid_at:
            q = q.order_by("-paid_at")
        elif filters.signed_at:
            q = q.order_by("-signed_at")
        elif filters.delivered_at:
            q = q.order_by("-delivered_at")
        elif filters.completed_at:
            q = q.order_by("-completed_at")
        else:
            q = q.order_by("-created_at")

        if pagination:
            q = q.limit(limit)

        logger.info(q.sql())
        return q

    async def get_one_line_items(self, item_id, account_id):
        if self.has_account_id():
            query = self.db_model.filter(account_id=account_id).filter(id=item_id).first()
        else:
            query = self.db_model.get(id=item_id)
        query = query.prefetch_related(
            "line_items",
            "line_items__inventory",
            "address",
            "customer",
            "user",
            "line_items__driver",
            "line_items__potential_driver",
            "line_items__inventory__depot",
            "line_items__inventory__vendor",
            "note",
            "single_customer",
            "single_customer__customer_contacts",
        )

        results = [await query]
        res: List[CustomOrderDTO] = [CustomOrderDTO.from_orm(order) for order in results if order is not None]
        mapped_result_list = []
        for order in res:
            mapped_result_list.extend(map_order_to_line_item_order_dto(order))

        return mapped_result_list

    async def get_all_by_single_customer(self, single_customer_id):
        query = self.db_model.filter(single_customer_id=single_customer_id)
        query = query.prefetch_related(
            "line_items",
            "line_items__inventory",
            "address",
            "customer",
            "user",
            "line_items__driver",
            "line_items__potential_driver",
            "line_items__inventory__depot",
            "line_items__inventory__vendor",
            "note",
        )

        results = await query
        res: List[CustomOrderDTO] = [CustomOrderDTO.from_orm(order) for order in results]
        mapped_result_list = []
        for order in res:
            mapped_result_list.extend(map_order_to_line_item_order_dto(order))

        return mapped_result_list

    async def get_by_status_type(
        self,
        account_id: int,
        status: str,
        order_type: str,
        user_ids: List[str],
        pagination: PAGINATION,
        get_all: bool = False,
    ) -> Dict[str, Any]:
        query, count = await get_by_status_type(self, account_id, status, order_type, user_ids, pagination)

        query = query.prefetch_related(
            "line_items",
            "line_items__inventory",
            "address",
            "customer",
            "user",
            "line_items__driver",
            "line_items__potential_driver",
            "line_items__inventory__depot",
            "line_items__inventory__vendor",
            "note",
            "single_customer",
            "single_customer__customer_contacts",
        )

        logger.info(query.sql() + f" count: {count}")
        results = await query
        res: List[CustomOrderDTO] = [CustomOrderDTO.from_orm(order) for order in results]
        mapped_result_list = []
        for order in res:
            mapped_result_list.extend(map_order_to_line_item_order_dto(order))

        return {
            "orders": mapped_result_list,
            "count": count,
        }


partial_order_crud = PartialOrderCRUD()
