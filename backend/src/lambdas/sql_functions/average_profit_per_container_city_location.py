# Pip imports
from psycopg2 import sql

# Internal imports
from src.crud.order_crud import order_crud
from src.schemas.reports import FilterObject


async def get_average_profit_per_container_city_location(filters: FilterObject, psycopg2_connection=None):
    result = await order_crud.get_all_profits_by_state(filters.begin_date, filters.end_date, filters.account_id)
    return result
