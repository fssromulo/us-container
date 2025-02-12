# Pip imports
from loguru import logger
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


common_sql = """
with orders as(
SELECT *
FROM "order"
WHERE ("account_id" = {account_id} OR "account_id" = {account_id})
  AND "delivered_at" >= {begin_date}::date
  AND "delivered_at" <= {end_date}::date + INTERVAL '1 day'
UNION ALL
SELECT *
FROM "order" o
WHERE ("account_id" = {account_id} OR "account_id" = {account_id})
  AND "completed_at" >= {begin_date}::date
  AND "completed_at" <= {end_date}::date + INTERVAL '1 day'
AND NOT EXISTS (
    SELECT 1
    FROM line_item li2
    WHERE li2.order_id = o.id
    AND li2.shipping_revenue != 0
  )
), managers as (
        SELECT
	   u.id as manager_id
        FROM users u
        LEFT JOIN assistant a
        ON u.id=a.assistant_id
        WHERE a.id is null
        GROUP BY u.id
), all_order_commission as (
SELECT order_commission.* FROM order_commission
JOIN orders
on orders.display_order_id=order_commission.display_order_id
where is_team_commission=False
), orders_full as (
select
     u.first_name || ' ' || u.last_name as manager_name,
     u2.first_name || ' ' || u2.last_name as agent_name,
     o.managing_agent_id as manager_id,
     o.agent_id as agent_id,
     o.display_order_id,
     o.paid_at,
     o.delivered_at,
     o.profit,
     o.total_commission,
     o.agent_commission_owed as agent_commission,
     o.manager_commission_owed as manager_commission,
     o.sub_total_price as subtotal_amount
from all_order_commission o
JOIN users u on o.managing_agent_id=u.id
JOIN users u2 on o.agent_id=u2.id
INNER JOIN managers m
ON m.manager_id=u.id
WHERE o.managing_agent_id is not null
UNION
select
     u.first_name || ' ' || u.last_name as manager_name,
     u2.first_name || ' ' || u2.last_name as agent_name,
     o.agent_id as manager_id,
     o.agent_id as agent_id,
     o.display_order_id,
          o.paid_at,
     o.delivered_at,
     o.profit,
     o.total_commission,
     o.agent_commission_owed as agent_commission,
     o.manager_commission_owed as manager_commission,
     o.sub_total_price as subtotal_amount
from all_order_commission o
JOIN users u on o.agent_id=u.id
JOIN users u2 on o.agent_id=u2.id
INNER JOIN managers m
ON m.manager_id=u.id
WHERE agent_id is not null)"""


def contains_all(main_list, sub_list):
    return all(item in main_list for item in sub_list)


def get_commissions_closed_individual_report(filters: FilterObject, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
{common_sql}
select
    *
FROM orders_full where manager_id={user_id}
                        """.replace(
                "{common_sql}", common_sql
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


def get_commissions_closed_agents_individual_report(filters: FilterObject, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
{common_sql}
select manager_id, agent_id, manager_name, agent_name, display_order_id, CASE WHEN agent_id != manager_id and agent_id={user_id} THEN 0 ELSE manager_commission END as manager_commission,
 agent_commission,
CASE WHEN agent_id != manager_id and agent_id={user_id} THEN 0 ELSE total_commission END as total_commission,subtotal_amount,profit,paid_at,delivered_at
FROM orders_full where manager_id={user_id} or agent_id={user_id}
                        """.replace(
                "{common_sql}", common_sql
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
