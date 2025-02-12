# Pip imports
from loguru import logger
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.commissions_report import common_sql_commissions, select_order_by_delivered_and_completed
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def contains_all(main_list, sub_list):
    return all(item in main_list for item in sub_list)


def get_commissions_individual_report(filters: FilterObject, psycopg2_connection=None):

    query = (
        sql.SQL(
            """
{select_order_by_delivered_and_completed}{common_sql_commissions}
select * from manager_commission_dedup where manager_id={user_id} order by agent_commission desc
                        """.replace(
                "{select_order_by_delivered_and_completed}", select_order_by_delivered_and_completed
            ).replace(
                "{common_sql_commissions}", common_sql_commissions
            )
        )
        .format(
            begin_date=sql.Literal(filters.begin_date),
            end_date=sql.Literal(filters.end_date),
            user_id=sql.Literal(filters.user_id),
        )
        .as_string(psycopg2_connection)
    )
    logger.info(query)
    return query


def get_commissions_agents_individual_report(filters: FilterObject, psycopg2_connection=None):

    query = (
        sql.SQL(
            """
{select_order_by_delivered_and_completed}{common_sql_commissions}
select manager_id, agent_id, manager_name, agent_name, display_order_id, CASE WHEN agent_id != manager_id and agent_id={user_id} THEN 0 ELSE manager_commission END as manager_commission,
 agent_commission,
CASE WHEN agent_id != manager_id and agent_id={user_id} THEN 0 ELSE total_commission END as total_commission,subtotal_amount,profit,paid_at,delivered_at
 from manager_commission_dedup where manager_id={user_id} or agent_id={user_id} order by agent_commission desc
                        """.replace(
                "{select_order_by_delivered_and_completed}", select_order_by_delivered_and_completed
            ).replace(
                "{common_sql_commissions}", common_sql_commissions
            )
        )
        .format(
            begin_date=sql.Literal(filters.begin_date),
            end_date=sql.Literal(filters.end_date),
            user_id=sql.Literal(filters.user_id),
            account_id=sql.Literal(filters.account_id),
        )
        .as_string(psycopg2_connection)
    )
    logger.info(query)
    return query
