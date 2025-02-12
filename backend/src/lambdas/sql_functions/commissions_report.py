# Pip imports
from loguru import logger
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def contains_all(main_list, sub_list):
    return all(item in main_list for item in sub_list)


common_sql_commissions = """
, bank_fees as (
	SELECT
  o.display_order_id,
  sum(COALESCE(CASE WHEN ft.name = 'CREDIT_CARD' THEN f.fee_amount else 0 end, 0)) bank_fee
	FROM orders o
	LEFT JOIN fee f
	ON o.id=f.order_id
	LEFT JOIN fee_type ft
        ON f.type_id=ft.id
        GROUP BY o.display_order_id
),
sum_fees as (
	SELECT
            o.display_order_id,
	    sum(COALESCE(CASE WHEN ft.is_taxable = TRUE THEN f.fee_amount else 0 end, 0)) taxable_fees
	FROM orders o
	LEFT JOIN fee f
	ON o.id=f.order_id
	LEFT JOIN fee_type ft
        ON f.type_id=ft.id
        GROUP BY o.display_order_id
),
sum_fees_adjusts_profit as (
	SELECT
            o.display_order_id,
	    sum(COALESCE(CASE WHEN ft.adjusts_profit = TRUE THEN f.fee_amount else 0 end, 0)) adjusts_profit_fees
	FROM orders o
	LEFT JOIN fee f
	ON o.id=f.order_id
	LEFT JOIN fee_type ft
        ON f.type_id=ft.id
        GROUP BY o.display_order_id
)
, ranked_taxes AS (
   SELECT o.*, t.tax_amount,
          RANK() OVER (PARTITION BY o.id ORDER BY t.created_at DESC) as rn
   FROM orders o
   LEFT JOIN order_tax t ON t.order_id = o.id
),
total_price as (
	SELECT
            o.display_order_id,
		sum(COALESCE(li.shipping_revenue, 0) + COALESCE(li.revenue, 0)) + COALESCE(sf.taxable_fees, 0) + COALESCE(bf.bank_fee, 0) + COALESCE(rt.tax_amount, 0) as total_amount,
        sum(COALESCE(li.shipping_revenue, 0) + COALESCE(li.revenue, 0)) + COALESCE(sf.taxable_fees, 0)  as subtotal_amount
	FROM orders o
        INNER JOIN line_item li
        ON o.id=li.order_id
        LEFT JOIN sum_fees sf
        ON o.display_order_id = sf.display_order_id
        LEFT JOIN bank_fees bf
        ON o.display_order_id = bf.display_order_id
        LEFT JOIN ranked_taxes rt
        ON o.display_order_id=rt.display_order_id
        WHERE rt.rn = 1 or rt.rn is null
        GROUP BY o.display_order_id,  sf.taxable_fees, bf.bank_fee, rt.rn, rt.tax_amount
), estimated_profit as (
	SELECT
                o.display_order_id,
		sum(COALESCE(li.shipping_revenue, 0) + COALESCE(li.revenue, 0) - COALESCE(i.total_cost, li.product_cost, 0) - COALESCE(li.shipping_cost, 0)) as estimated_profit_val
	FROM orders o
        INNER JOIN line_item li
        ON o.id=li.order_id
        LEFT JOIN container_inventory i
        ON li.inventory_id=i.id
        GROUP BY o.display_order_id
), processing_cost as (
	SELECT
	o.display_order_id,
	CASE WHEN o.charge_per_line_item = TRUE and o.processing_flat_cost is not null and o.processing_flat_cost != 0 THEN o.processing_flat_cost * count(*)
WHEN o.charge_per_line_item = False and o.processing_flat_cost is not null and o.processing_flat_cost != 0 THEN o.processing_flat_cost  ELSE o.processing_percentage_cost * tp.total_amount END as processing_cost_val
	FROM orders o
        INNER JOIN line_item li
        ON o.id=li.order_id
        INNER JOIN total_price tp
        ON o.display_order_id = tp.display_order_id
   WHERE li.product_type = 'CONTAINER' OR li.product_type = 'SHIPPING_CONTAINER'
	GROUP BY o.display_order_id, o.processing_flat_cost, o.charge_per_line_item, o.display_order_id, processing_percentage_cost, tp.total_amount
), profit as(
	SELECT ep.display_order_id, ep.estimated_profit_val - pc.processing_cost_val + COALESCE(sp.adjusts_profit_fees, 0) as profit,
        o.user_id as agent_id,
        o.delivered_at,
        o.completed_at,
        o.paid_at,
        o.type,
        count(*) as num_line_items
         from estimated_profit ep
        LEFT JOIN processing_cost pc
        ON
        ep.display_order_id=pc.display_order_id
        JOIN orders o
        on ep.display_order_id=o.display_order_id
        JOIN line_item li
         ON o.id = li.order_id
        LEFT JOIN sum_fees_adjusts_profit sp
         ON sp.display_order_id=ep.display_order_id
        group by o.display_order_id, ep.display_order_id, ep.estimated_profit_val, pc.processing_cost_val,sp.adjusts_profit_fees,
        o.user_id,
        o.delivered_at,
        o.completed_at,
        o.paid_at,
        o.type
), agents_and_managers as (
	SELECT
	   a.assistant_id as user_id,
           a.manager_id as manager_id
	FROM  assistant a
        UNION ALL
        (
        SELECT
	   u.id as user_id,
           NULL as manager_id
        FROM users u
        LEFT JOIN assistant a
        ON u.id=a.assistant_id
        WHERE a.id is null
        GROUP BY u.id)
), commissions_rates_ordered AS (
        SELECT
           am.user_id,
           am.manager_id,
           cr.commission_percentage,
           cr.rental_total_flat_commission_rate,
           cr.flat_commission,
           RANK() OVER (PARTITION BY cr.user_id ORDER BY cr.commission_effective_date DESC) as rn
        FROM
           commission_rates cr
        INNER JOIN agents_and_managers am
        ON
           cr.user_id=COALESCE(am.manager_id, am.user_id)
), profit_commission AS (
	SELECT
                p.display_order_id,
                cro.user_id,
                cro.manager_id,
		CASE WHEN (p.type='PURCHASE' OR p.type='PURCHASE_ACCESSORY' OR p.TYPE='RENT_TO_OWN') and cro.commission_percentage != 0 THEN cro.commission_percentage * p.profit / 100 WHEN (p.type='PURCHASE' OR p.type='PURCHASE_ACCESSORY' OR p.TYPE='RENT_TO_OWN') and cro.flat_commission != 0 THEN cro.flat_commission * p.num_line_items
WHEN p.type='RENT' THEN cro.rental_total_flat_commission_rate * p.num_line_items ELSE 0 END as comission
	FROM
            profit p
        INNER JOIN
            commissions_rates_ordered cro
        ON
            p.agent_id=cro.user_id
        WHERE rn = 1
), ranked_commissions_dates AS (
  SELECT
    user_id,
    commission_effective_date as start_date,
    commission_percentage,
    flat_commission,
    rental_total_flat_commission_rate,
    LEAD(created_at) OVER (
      PARTITION BY user_id
      ORDER BY created_at
    ) as end_date
  FROM commission_rates
), ranked_commission_dates_2 AS (
SELECT
  user_id,
  start_date,
  COALESCE(end_date, '9999-12-31') as end_date,
  commission_percentage,
    flat_commission,
    rental_total_flat_commission_rate
FROM ranked_commissions_dates
), agent_commission AS (
   SELECT
       u.first_name || ' ' || u.last_name as agent_name,
       p.agent_id,
       p.display_order_id,
       CASE WHEN (p.type='PURCHASE' or p.type='PURCHASE_ACCESSORY' or p.type='RENT_TO_OWN') and rcd2.commission_percentage!=0 THEN p.profit * rcd2.commission_percentage/100
            WHEN ( (p.type='PURCHASE' or p.type='RENT_TO_OWN') and rcd2.flat_commission!=0) THEN p.num_line_items * rcd2.flat_commission
            WHEN (p.type = 'RENT' and rcd2.rental_total_flat_commission_rate != 0) THEN p.num_line_items * rcd2.rental_total_flat_commission_rate ELSE 0 END as agent_commission,
       RANK() OVER (
            PARTITION BY p.display_order_id
            ORDER BY p.agent_id, end_date DESC
        ) as rn
   FROM profit p
   INNER JOIN ranked_commission_dates_2 rcd2
   on p.agent_id=rcd2.user_id
   INNER JOIN users u
   ON
       u.id=p.agent_id
   WHERE
      ((p.type = 'PURCHASE' OR p.type='PURCHASE_ACCESSORY' OR p.type = 'RENT_TO_OWN') and p.paid_at BETWEEN rcd2.start_date and rcd2.end_date) OR
      (p.type = 'RENT' and p.delivered_at BETWEEN rcd2.start_date and rcd2.end_date)
   order by agent_commission desc

), agent_commission_dedup as (
  select
        *
  from agent_commission
  where rn = 1
), manager_commission2 AS (
   SELECT
       pc.manager_id as manager_id,
       u.first_name || ' ' || u.last_name as manager_name,
       u_agent.first_name || ' ' || u_agent.last_name as agent_name,
       pc.display_order_id,
       CASE WHEN pc.manager_id is null THEN pc.comission ELSE pc.comission - ac.agent_commission END as manager_commission,
       CASE WHEN pc.manager_id is null THEN 0 ELSE ac.agent_commission END as agent_commission,
       pc.comission as total_commission,
       tp.subtotal_amount,
       p.profit,
       ROW_NUMBER() OVER (
            PARTITION BY pc.display_order_id
            ORDER BY COALESCE(pc.manager_id, pc.user_id) DESC
        ) as rn,
        p.paid_at,
        p.delivered_at,
        p.completed_at
   FROM profit_commission pc
   INNER JOIN agent_commission_dedup ac
   on pc.display_order_id=ac.display_order_id
   INNER JOIN users u
   ON pc.manager_id=u.id
   INNER JOIN users u_agent
   ON ac.agent_id=u_agent.id
   INNER JOIN total_price tp
      on pc.display_order_id=tp.display_order_id
   INNER JOIN profit p
      on pc.display_order_id=p.display_order_id
),
manager_commission AS (
   SELECT
       COALESCE(pc.manager_id, pc.user_id) as manager_id,
       u_agent.id as agent_id,
       u.first_name || ' ' || u.last_name as manager_name,
       u_agent.first_name || ' ' || u_agent.last_name as agent_name,
       pc.display_order_id,
       CASE WHEN pc.manager_id is null THEN pc.comission ELSE pc.comission - ac.agent_commission END as manager_commission,
       CASE WHEN pc.manager_id is null THEN 0 ELSE ac.agent_commission END as agent_commission,
       pc.comission as total_commission,
       tp.subtotal_amount,
       tp.total_amount as total_price,
       p.profit,
       ROW_NUMBER() OVER (
            PARTITION BY pc.display_order_id
            ORDER BY COALESCE(pc.manager_id, pc.user_id) DESC
        ) as rn,
        p.paid_at,
        p.delivered_at,
        p.completed_at
   FROM profit_commission pc
   INNER JOIN agent_commission_dedup ac
   on pc.display_order_id=ac.display_order_id
   INNER JOIN users u
   ON COALESCE(pc.manager_id, pc.user_id)=u.id
   INNER JOIN users u_agent
   ON ac.agent_id=u_agent.id
   INNER JOIN total_price tp
      on pc.display_order_id=tp.display_order_id
   INNER JOIN profit p
      on pc.display_order_id=p.display_order_id
)
, manager_commission_dedup as (
  select
        *
  from manager_commission
  where rn = 1
),
 manager_commission_dedup2 as (
  select
        *
  from manager_commission2
  where rn = 1
)
, manager_commission_agg as (
  SELECT
     manager_name,
     manager_id,
     sum(subtotal_amount) as sum_total_amount,
     sum(total_commission) as sum_total_commission
  from manager_commission_dedup
  group by
     manager_name, manager_id
  order by sum_total_commission desc
), agent_commission_agg as (
  SELECT
     agent_id,
     agent_name,
     sum(agent_commission) as sum_agent_commission
  from agent_commission_dedup
  group by
     agent_id, agent_name
  UNION ALL
  SELECT
     manager_id,
     manager_name,
     sum(manager_commission) as sum_agent_commission
  from manager_commission_dedup2 m
  group by
     manager_id, manager_name
), agent_commission_agg_ordered as (
	select agent_id, agent_name, sum(sum_agent_commission) as sum_agent_commission from  agent_commission_agg
        group by agent_id, agent_name
        order by sum_agent_commission
        desc
)"""


select_order_by_delivered_and_completed = """
 with orders as(
SELECT user_id,delivered_at,completed_at,paid_at,type,display_order_id,id,charge_per_line_item,processing_flat_cost,processing_percentage_cost
FROM "order"
WHERE ("account_id" = {account_id} OR "account_id" = {account_id})
  AND "delivered_at" >= {begin_date}::date
  AND "delivered_at" <= {end_date}::date + INTERVAL '1 day'
  AND type != 'PURCHASE_ACCESSORY'
UNION ALL
SELECT  user_id,delivered_at,completed_at,paid_at,type,display_order_id,id,charge_per_line_item,processing_flat_cost,processing_percentage_cost
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
  AND type != 'PURCHASE_ACCESSORY'
)
"""


def get_commissions_report(filters: FilterObject, psycopg2_connection=None):
    regular_order_sql_where_clause = sql.SQL("")
    rental_order_sql_where_clause = sql.SQL("")
    accessory_sql_where_clause = sql.SQL("")

    query = (
        sql.SQL(
            """
{select_order_by_delivered_and_completed}{common_sql_commissions}
select * from manager_commission_agg
                        """.replace(
                "{select_order_by_delivered_and_completed}", select_order_by_delivered_and_completed
            ).replace(
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


def get_commissions_report_full(filters: FilterObject, psycopg2_connection=None):

    query = (
        sql.SQL(
            """
            {select_order_by_delivered_and_completed}{common_sql_commissions}
            select manager_id,
            agent_id,
            manager_name,
            agent_name,
            display_order_id,
            manager_commission,
            agent_commission,
            total_commission,
            subtotal_amount,
            profit,
            paid_at,
            delivered_at,
            completed_at,
            total_price
            from manager_commission_dedup order by agent_commission desc
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
    return query
