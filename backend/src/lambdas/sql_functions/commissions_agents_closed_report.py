# Pip imports
from loguru import logger
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def contains_all(main_list, sub_list):
    return all(item in main_list for item in sub_list)


def get_commissions_agents_closed_report(filters: FilterObject, psycopg2_connection=None):

    query = (
        sql.SQL(
            """
WITH orders AS (
    SELECT *
    FROM "order"
    WHERE "account_id" = {account_id}
      AND "delivered_at" >= {begin_date}::date
      AND "delivered_at" <= {end_date}::date + INTERVAL '1 day'
    UNION ALL
    SELECT *
    FROM "order" o
    WHERE "account_id" = {account_id}
      AND "completed_at" >= {begin_date}::date
      AND "completed_at" <= {end_date}::date + INTERVAL '1 day'
      AND NOT EXISTS (
        SELECT 1
        FROM line_item li2
        WHERE li2.order_id = o.id
          AND li2.shipping_revenue != 0
      )
), managers AS (
    SELECT
        u.id as manager_id
    FROM users u
    LEFT JOIN assistant a
        ON u.id = a.assistant_id
    WHERE a.id is null
    GROUP BY u.id
), all_order_commission AS (
    SELECT order_commission.*
    FROM order_commission
    JOIN orders
        ON orders.display_order_id = order_commission.display_order_id
    where is_team_commission=False

), orders_full AS (
    SELECT
        u.first_name || ' ' || u.last_name as manager_name,
        o.managing_agent_id as manager_id,
        o.manager_commission_owed as total_commission
    FROM all_order_commission o
    JOIN users u
        ON o.managing_agent_id = u.id
    UNION ALL
    SELECT
        u.first_name || ' ' || u.last_name as manager_name,
        o.agent_id as manager_id,
        o.manager_commission_owed as total_commission
    FROM all_order_commission o
    JOIN users u
        ON o.agent_id = u.id
    WHERE o.managing_agent_id is null
    UNION ALL
    SELECT
        u.first_name || ' ' || u.last_name as manager_name,
        o.agent_id as manager_id,
        o.agent_commission_owed as total_commission
    FROM all_order_commission o
    JOIN users u
        ON o.agent_id = u.id
    where o.agent_commission_owed is not null
), orders_full_agg as (
SELECT
    manager_name as agent_name,
    manager_id as agent_id,
    sum(total_commission) as sum_agent_commission
FROM orders_full
GROUP BY manager_name, manager_id
ORDER BY sum_agent_commission DESC
) select * from orders_full_agg
                        """
        )
        .format(begin_date=sql.Literal(filters.begin_date), end_date=sql.Literal(filters.end_date), account_id=sql.Literal(filters.account_id))
        .as_string(psycopg2_connection)
    )
    logger.info(query)
    return query
