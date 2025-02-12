# Python imports
from datetime import datetime

# Internal imports
from src.crud.order_card_info_crud import order_credit_card_crud
from src.schemas.reports import FilterObject


async def get_credit_cards_summary(filters: FilterObject):
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    result = await order_credit_card_crud.get_all_between_dates_including_order(
        filters.account_id,
        datetime.strptime(filters.begin_date, date_format),
        datetime.strptime(filters.end_date, date_format),
        filters.purchase_type,
    )
    return result
