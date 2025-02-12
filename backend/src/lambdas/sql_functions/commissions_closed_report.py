# Pip imports
from loguru import logger
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def contains_all(main_list, sub_list):
    return all(item in main_list for item in sub_list)


def get_commissions_closed_report(filters: FilterObject, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
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
     o.managing_agent_id as manager_id,
     o.sub_total_price,
     o.total_commission
from all_order_commission o
JOIN users u on o.managing_agent_id=u.id
INNER JOIN managers m
ON m.manager_id=u.id
WHERE o.managing_agent_id is not null
UNION ALL
select
     u.first_name || ' ' || u.last_name as manager_name,
     o.agent_id as manager_id,
     o.sub_total_price,
     o.total_commission
from all_order_commission o
JOIN users u on o.agent_id=u.id
INNER JOIN managers m
ON m.manager_id=u.id
WHERE agent_id is not null)
select
    manager_name,
    manager_id,
    sum(sub_total_price) as sum_total_amount,
    sum(total_commission) as sum_total_commission
from orders_full
group by manager_name, manager_id
order by sum(total_commission) desc
                        """
        )
        .format(begin_date=sql.Literal(filters.begin_date), end_date=sql.Literal(filters.end_date), account_id=sql.Literal(filters.account_id))
        .as_string(psycopg2_connection)
    )
    logger.info(query)
    return query
