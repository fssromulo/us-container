# Pip imports
from loguru import logger
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def contains_all(main_list, sub_list):
    return all(item in main_list for item in sub_list)


common_sql_commissions = """
with orders as(
SELECT id, type, display_order_id, user_id, delivered_at, paid_at
FROM "order"
WHERE ("account_id" = {account_id} OR "account_id" = {account_id})
  AND "delivered_at" >= {begin_date}::date
  AND "delivered_at" <= {end_date}::date + INTERVAL '1 day'
UNION
SELECT id, type, display_order_id, user_id, delivered_at, paid_at
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
),
total_price as (
	SELECT
            o.display_order_id,
            o.user_id,
	    sum(COALESCE(li.shipping_revenue, 0) + COALESCE(li.revenue, 0)) as subtotal_amount,
            o.delivered_at,
            o.paid_at
	FROM orders o
        INNER JOIN line_item li
        ON o.id=li.order_id
	WHERE o.type='PURCHASE_ACCESSORY'
        GROUP BY o.display_order_id, o.user_id, o.delivered_at, o.paid_at
),
agents_and_managers AS (
    SELECT a.assistant_id as user_id,
           a.manager_id as manager_id
    FROM assistant a
    UNION ALL
    SELECT manager_id as user_id, NULL as manager_id FROM (
	SELECT
		a.assistant_id as user_id,
           	a.manager_id as manager_id,
	        ROW_NUMBER() OVER (PARTITION BY manager_id ORDER BY manager_id) AS rn
    	FROM assistant a
    ) as test
    where rn=1
    UNION ALL
    SELECT id as user_id, NULL as manager_id from users
    WHERE id not in (
        SELECT
            assistant_id from assistant
        UNION ALL
        SELECT manager_id from assistant
    )
),
 commission_accessories_name as (
SELECT
  subtotal_amount as subtotal_amount,
  0.1 * subtotal_amount as commission,
  u1.first_name || ' ' || u1.last_name as agent_name,
  u2.first_name || ' ' || u2.last_name as manager_name,
  u1.id as agent_id,
  u2.id as manager_id,
  tp.display_order_id,
  tp.paid_at,
  tp.delivered_at
from total_price tp
join agents_and_managers aam on aam.user_id=tp.user_id
join users u1 on u1.id=aam.user_id
left join users u2 on u2.id=aam.manager_id)
"""


def get_commissions_accessories_report(filters: FilterObject, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
                        {common_sql_commissions}
                        select agent_name, manager_name, agent_id, sum(commission) as total_commission, sum(subtotal_amount) as subtotal, paid_at, delivered_at
                        from commission_accessories_name
                        group by agent_name,manager_name, agent_id, paid_at, delivered_at
                        """.replace(
                "{common_sql_commissions}", common_sql_commissions
            )
        )
        .format(
            begin_date=sql.Literal(filters.begin_date),
            end_date=sql.Literal(filters.end_date),
            account_id=sql.Literal(filters.account_id),
        )
        .as_string(psycopg2_connection)
    )
    logger.info(query)
    return query


def get_commissions_individual_accessories_report(filters: FilterObject, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
                        {common_sql_commissions}
                        select * from commission_accessories_name where agent_id={user_id}
                        """.replace(
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
