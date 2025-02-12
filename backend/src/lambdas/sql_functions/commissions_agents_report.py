# Pip imports
from loguru import logger
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.commissions_report import common_sql_commissions, select_order_by_delivered_and_completed
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def contains_all(main_list, sub_list):
    return all(item in main_list for item in sub_list)


def get_commissions_agents_report(filters: FilterObject, psycopg2_connection=None):

    query = (
        sql.SQL(
            """
{select_order_by_delivered_and_completed}{common_sql_commissions}
select * from agent_commission_agg_ordered
                        """.replace(
                "{select_order_by_delivered_and_completed}", select_order_by_delivered_and_completed
            ).replace(
                "{common_sql_commissions}", common_sql_commissions
            )
        )
        .format(begin_date=sql.Literal(filters.begin_date), end_date=sql.Literal(filters.end_date))
        .as_string(psycopg2_connection)
    )
    logger.info(query)
    return query
