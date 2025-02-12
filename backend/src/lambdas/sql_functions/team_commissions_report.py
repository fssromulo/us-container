# Pip imports
from loguru import logger
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def contains_all(main_list, sub_list):
    return all(item in main_list for item in sub_list)


common_sql_commissions = """
WITH orders AS (
SELECT user_id, delivered_at, paid_at, type, display_order_id, id,
           charge_per_line_item, processing_flat_cost, processing_percentage_cost
    FROM "order"
    WHERE "account_id" = {account_id}
      AND "delivered_at" >= {begin_date}::date
      AND "delivered_at" <= {end_date}::date + INTERVAL '1 day'

    UNION ALL

    SELECT user_id, delivered_at, paid_at, type, display_order_id, id,
           charge_per_line_item, processing_flat_cost, processing_percentage_cost
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
qualifying_orders as (
	 SELECT user_id, delivered_at, paid_at, type, display_order_id, id,
           charge_per_line_item, processing_flat_cost, processing_percentage_cost
    FROM "order" o
    WHERE "account_id" = {account_id}
      AND "paid_at" >= {begin_date}::date
      AND "paid_at" <= {end_date}::date + INTERVAL '1 day'
      and status in ('Paid', 'Delivered', 'Completed', 'Partially Paid')
),

bank_fees AS (
    SELECT o.display_order_id,
           sum(COALESCE(CASE WHEN ft.name = 'CREDIT_CARD' THEN f.fee_amount ELSE 0 END, 0)) bank_fee
    FROM orders o
    LEFT JOIN fee f ON o.id = f.order_id
    LEFT JOIN fee_type ft ON f.type_id = ft.id
    GROUP BY o.display_order_id
),

sum_fees AS (
    SELECT o.display_order_id,
           sum(COALESCE(CASE WHEN ft.is_taxable = TRUE THEN f.fee_amount ELSE 0 END, 0)) taxable_fees
    FROM orders o
    LEFT JOIN fee f ON o.id = f.order_id
    LEFT JOIN fee_type ft ON f.type_id = ft.id
    GROUP BY o.display_order_id
),

ranked_taxes AS (
    SELECT o.*, t.tax_amount,
           RANK() OVER (PARTITION BY o.id ORDER BY t.created_at DESC) as rn
    FROM orders o
    LEFT JOIN order_tax t ON t.order_id = o.id
),

total_price AS (
    SELECT o.display_order_id,
           sum(COALESCE(li.shipping_revenue, 0) + COALESCE(li.revenue, 0)) +
           COALESCE(sf.taxable_fees, 0) + COALESCE(bf.bank_fee, 0) +
           COALESCE(rt.tax_amount, 0) as total_amount,
           sum(COALESCE(li.shipping_revenue, 0) + COALESCE(li.revenue, 0)) +
           COALESCE(sf.taxable_fees, 0) as subtotal_amount
    FROM orders o
    INNER JOIN line_item li ON o.id = li.order_id
    LEFT JOIN sum_fees sf ON o.display_order_id = sf.display_order_id
    LEFT JOIN bank_fees bf ON o.display_order_id = bf.display_order_id
    LEFT JOIN ranked_taxes rt ON o.display_order_id = rt.display_order_id
    WHERE rt.rn = 1 or rt.rn is null
    GROUP BY o.display_order_id, sf.taxable_fees, bf.bank_fee, rt.rn, rt.tax_amount
),
bank_fees_qualifying_orders AS (
    SELECT o.display_order_id,
           sum(COALESCE(CASE WHEN ft.name = 'CREDIT_CARD' THEN f.fee_amount ELSE 0 END, 0)) bank_fee
    FROM qualifying_orders o
    LEFT JOIN fee f ON o.id = f.order_id
    LEFT JOIN fee_type ft ON f.type_id = ft.id
    GROUP BY o.display_order_id
),

sum_fees_qualifying_orders AS (
    SELECT o.display_order_id,
           sum(COALESCE(CASE WHEN ft.is_taxable = TRUE THEN f.fee_amount ELSE 0 END, 0)) taxable_fees
    FROM qualifying_orders o
    LEFT JOIN fee f ON o.id = f.order_id
    LEFT JOIN fee_type ft ON f.type_id = ft.id
    GROUP BY o.display_order_id
),

ranked_taxes_qualifying_orders AS (
    SELECT o.*, t.tax_amount,
           RANK() OVER (PARTITION BY o.id ORDER BY t.created_at DESC) as rn
    FROM qualifying_orders o
    LEFT JOIN order_tax t ON t.order_id = o.id
),

total_price_qualifying_orders AS (
    SELECT o.display_order_id,
           o.user_id as agent_id,
           sum(COALESCE(li.shipping_revenue, 0) + COALESCE(li.revenue, 0)) +
           COALESCE(sf.taxable_fees, 0) + COALESCE(bf.bank_fee, 0) +
           COALESCE(rt.tax_amount, 0) as total_amount,
           sum(COALESCE(li.shipping_revenue, 0) + COALESCE(li.revenue, 0)) +
           COALESCE(sf.taxable_fees, 0) as subtotal_amount
    FROM qualifying_orders o
    INNER JOIN line_item li ON o.id = li.order_id
    LEFT JOIN sum_fees_qualifying_orders sf ON o.display_order_id = sf.display_order_id
    LEFT JOIN bank_fees_qualifying_orders bf ON o.display_order_id = bf.display_order_id
    LEFT JOIN ranked_taxes_qualifying_orders rt ON o.display_order_id = rt.display_order_id
    WHERE rt.rn = 1 or rt.rn is null
    GROUP BY o.display_order_id, sf.taxable_fees, bf.bank_fee, rt.rn, rt.tax_amount, o.user_id
),
estimated_profit AS (
    SELECT o.display_order_id,
           sum(COALESCE(li.shipping_revenue, 0) + COALESCE(li.revenue, 0) -
               COALESCE(i.total_cost, li.product_cost, 0) - COALESCE(li.shipping_cost, 0)) as estimated_profit_val
    FROM orders o
    INNER JOIN line_item li ON o.id = li.order_id
    LEFT JOIN container_inventory i ON li.inventory_id = i.id
    GROUP BY o.display_order_id
),

processing_cost AS (
    SELECT o.display_order_id,
           CASE
               WHEN o.charge_per_line_item = TRUE AND o.processing_flat_cost IS NOT NULL
                    AND o.processing_flat_cost != 0
               THEN o.processing_flat_cost * count(*)
               WHEN o.charge_per_line_item = FALSE AND o.processing_flat_cost IS NOT NULL
                    AND o.processing_flat_cost != 0
               THEN o.processing_flat_cost
               ELSE o.processing_percentage_cost * tp.total_amount
           END as processing_cost_val
    FROM orders o
    INNER JOIN line_item li ON o.id = li.order_id
    INNER JOIN total_price tp ON o.display_order_id = tp.display_order_id
    WHERE li.product_type = 'CONTAINER' OR li.product_type = 'SHIPPING_CONTAINER'
    GROUP BY o.display_order_id, o.processing_flat_cost, o.charge_per_line_item,
             o.processing_percentage_cost, tp.total_amount
),
agents_and_managers AS (
    SELECT a.assistant_id as user_id,
           a.manager_id as manager_id
    FROM assistant a
    UNION ALL
    SELECT manager_id as user_id, NULL as manager_id FROM (
	SELECT a.assistant_id as user_id,
           a.manager_id as manager_id,
	         ROW_NUMBER() OVER (PARTITION BY manager_id ORDER BY manager_id) AS rn
    FROM assistant a) as test
    where rn=1
),
profit AS (
    SELECT ep.display_order_id,
           ep.estimated_profit_val - pc.processing_cost_val as profit,
           o.user_id as agent_id,
           aam.manager_id as manager_id,
           o.delivered_at,
           o.paid_at,
           o.type,
           count(*) as num_line_items
    FROM estimated_profit ep
    LEFT JOIN processing_cost pc ON ep.display_order_id = pc.display_order_id
    JOIN orders o ON ep.display_order_id = o.display_order_id
    JOIN line_item li ON o.id = li.order_id
    join agents_and_managers aam on o.user_id=aam.user_id
    GROUP BY o.display_order_id, ep.display_order_id, ep.estimated_profit_val,
             pc.processing_cost_val, o.user_id, o.delivered_at, o.paid_at, o.type,aam.manager_id
),



commissions_rates_ordered AS (
    SELECT am.user_id,
           am.manager_id,
           cr.commission_percentage,
           cr.rental_total_flat_commission_rate,
           cr.flat_commission,
           RANK() OVER (PARTITION BY cr.user_id ORDER BY cr.commission_effective_date DESC) as rn
    FROM commission_rates cr
    INNER JOIN agents_and_managers am
    ON cr.user_id = COALESCE(am.manager_id, am.user_id)
),

profit_commission AS (
    SELECT p.display_order_id,
           cro.user_id,
           cro.manager_id,
           CASE
               WHEN (p.type = 'PURCHASE' OR p.TYPE = 'RENT_TO_OWN')
                    AND cro.commission_percentage != 0
               THEN cro.commission_percentage * p.profit / 100
               WHEN (p.type = 'PURCHASE' OR p.TYPE = 'RENT_TO_OWN')
                    AND cro.flat_commission != 0
               THEN cro.flat_commission * p.num_line_items
               WHEN p.type = 'RENT'
               THEN cro.rental_total_flat_commission_rate * p.num_line_items
               ELSE 0
           END as comission
    FROM profit p
    INNER JOIN commissions_rates_ordered cro ON p.agent_id = cro.user_id
    WHERE rn = 1
),

ranked_commissions_dates AS (
    SELECT user_id,
           commission_effective_date as start_date,
           commission_percentage,
           flat_commission,
           rental_total_flat_commission_rate,
           LEAD(created_at) OVER (
               PARTITION BY user_id
               ORDER BY created_at
           ) as end_date
    FROM commission_rates
),

ranked_commission_dates_final AS (
    SELECT user_id,
           start_date,
           COALESCE(end_date, '9999-12-31') as end_date,
           commission_percentage,
           flat_commission,
           rental_total_flat_commission_rate
    FROM ranked_commissions_dates
),

agent_commission AS (
    SELECT u.first_name || ' ' || u.last_name as agent_name,
           p.agent_id,
           p.display_order_id,
           CASE
               WHEN (p.type = 'PURCHASE' OR p.type = 'RENT_TO_OWN')
                    AND rcd2.commission_percentage != 0
               THEN p.profit * rcd2.commission_percentage/100
               WHEN (p.type = 'PURCHASE' OR p.type = 'RENT_TO_OWN')
                    AND rcd2.flat_commission != 0
               THEN p.num_line_items * rcd2.flat_commission
               WHEN p.type = 'RENT' AND rcd2.rental_total_flat_commission_rate != 0
               THEN p.num_line_items * rcd2.rental_total_flat_commission_rate
               ELSE 0
           END as agent_commission,
           RANK() OVER (
               PARTITION BY p.display_order_id
               ORDER BY p.agent_id, end_date DESC
           ) as rn
    FROM profit p
    INNER JOIN ranked_commission_dates_final rcd2 ON p.agent_id = rcd2.user_id
    INNER JOIN users u ON u.id = p.agent_id
    WHERE ((p.type = 'PURCHASE' OR p.type = 'RENT_TO_OWN')
           AND p.paid_at BETWEEN rcd2.start_date AND rcd2.end_date)
       OR (p.type = 'RENT' AND p.delivered_at BETWEEN rcd2.start_date AND rcd2.end_date)
),

agent_commission_dedup AS (
    SELECT *
    FROM agent_commission
    WHERE rn = 1
),

manager_commission_valid AS (
    SELECT pc.manager_id as manager_id,
           u.first_name || ' ' || u.last_name as manager_name,
           u_agent.first_name || ' ' || u_agent.last_name as agent_name,
           pc.display_order_id,
           CASE
               WHEN pc.manager_id IS NULL THEN pc.comission
               ELSE pc.comission - ac.agent_commission
           END as manager_commission,
           CASE
               WHEN pc.manager_id IS NULL THEN 0
               ELSE ac.agent_commission
           END as agent_commission,
           pc.comission as total_commission,
           tp.subtotal_amount,
           p.profit,
           ROW_NUMBER() OVER (
               PARTITION BY pc.display_order_id
               ORDER BY COALESCE(pc.manager_id, pc.user_id) DESC
           ) as rn,
           p.paid_at,
           p.delivered_at
    FROM profit_commission pc
    INNER JOIN agent_commission_dedup ac ON pc.display_order_id = ac.display_order_id
    INNER JOIN users u ON pc.manager_id = u.id
    INNER JOIN users u_agent ON ac.agent_id = u_agent.id
    INNER JOIN total_price tp ON pc.display_order_id = tp.display_order_id
    INNER JOIN profit p ON pc.display_order_id = p.display_order_id
),

manager_commission AS (
    SELECT COALESCE(pc.manager_id, pc.user_id) as manager_id,
           u.first_name || ' ' || u.last_name as manager_name,
           u_agent.first_name || ' ' || u_agent.last_name as agent_name,
           pc.display_order_id,
           CASE
               WHEN pc.manager_id IS NULL THEN pc.comission
               ELSE pc.comission - ac.agent_commission
           END as manager_commission,
           CASE
               WHEN pc.manager_id IS NULL THEN 0
               ELSE ac.agent_commission
           END as agent_commission,
           pc.comission as total_commission,
           tp.subtotal_amount,
           p.profit,
           ROW_NUMBER() OVER (
               PARTITION BY pc.display_order_id
               ORDER BY COALESCE(pc.manager_id, pc.user_id) DESC
           ) as rn,
           p.paid_at,
           p.delivered_at
    FROM profit_commission pc
    INNER JOIN agent_commission_dedup ac ON pc.display_order_id = ac.display_order_id
    INNER JOIN users u ON COALESCE(pc.manager_id, pc.user_id) = u.id
    INNER JOIN users u_agent ON ac.agent_id = u_agent.id
    INNER JOIN total_price tp ON pc.display_order_id = tp.display_order_id
    INNER JOIN profit p ON pc.display_order_id = p.display_order_id
),

manager_commission_dedup AS (
    SELECT *
    FROM manager_commission
    WHERE rn = 1
),

manager_commission_dedup_valid AS (
    SELECT *
    FROM manager_commission_valid
    WHERE rn = 1
),

manager_commission_agg AS (
    SELECT manager_name,
           manager_id,
           sum(subtotal_amount) as sum_total_amount,
           sum(total_commission) as sum_total_commission
    FROM manager_commission_dedup
    GROUP BY manager_name, manager_id
    ORDER BY sum_total_commission DESC
),

agent_commission_agg AS (
    SELECT agent_id,
           agent_name,
           sum(agent_commission) as sum_agent_commission
    FROM agent_commission_dedup
    GROUP BY agent_id, agent_name

    UNION ALL

    SELECT manager_id,
           manager_name,
           sum(manager_commission) as sum_agent_commission
    FROM manager_commission_dedup_valid m
    GROUP BY manager_id, manager_name
),

agent_commission_agg_ordered AS (
    SELECT agent_id,
           agent_name,
           sum(sum_agent_commission) as sum_agent_commission
    FROM agent_commission_agg
    GROUP BY agent_id, agent_name
    ORDER BY sum_agent_commission DESC
) ,
team as (
	SELECT * FROM (
        select a.manager_id as team_lead_id, a.assistant_id as team_member_id from assistant a
        union all
	select a.manager_id as team_lead_id, a.manager_id as team_member_id from assistant a) a
        group by team_lead_id, team_member_id
),
 teams_total_amount as(
	select t.team_lead_id,
        u.first_name || ' ' || u.last_name as name,
        sum(tp.subtotal_amount) as total_amount
        from team t
	inner join (
		select distinct team_lead_id from team_member
        ) tm on t.team_lead_id=tm.team_lead_id
	        INNER JOIN total_price_qualifying_orders tp
	ON tp.agent_id = t.team_member_id
                 INNER JOIN users u ON t.team_lead_id = u.id
        group by t.team_lead_id, u.first_name, u.last_name

), filtered_teams as (
select * from teams_total_amount where total_amount > 20000
), top_managers as (
SELECT
    ft.team_lead_id,
    ft.name AS name,
    CASE WHEN u2.first_name is null THEN 'N/A' ELSE u.first_name || ' ' || u.last_name END AS agent_name,
    CASE WHEN u2.first_name is null THEN u.first_name || ' ' || u.last_name  ELSE u2.first_name || ' ' || u2.last_name END AS manager_name ,
    tp.total_amount,
    p.display_order_id,
    p.profit * 0.05 AS total_commission,
    p.profit AS profit,
    p.paid_at,
    p.delivered_at
FROM filtered_teams ft
INNER JOIN team_member tm ON tm.team_lead_id = ft.team_lead_id
INNER JOIN profit p ON p.agent_id = tm.team_member_id
INNER JOIN users u ON u.id = p.agent_id
LEFT JOIN users u2 ON u2.id = p.manager_id
INNER JOIN total_price tp ON tp.display_order_id = p.display_order_id

UNION

SELECT
    ft.team_lead_id,
    ft.name AS name,
    CASE WHEN u2.first_name is null THEN 'N/A' ELSE u.first_name || ' ' || u.last_name END AS agent_name,
    CASE WHEN u2.first_name is null THEN u.first_name || ' ' || u.last_name  ELSE u2.first_name || ' ' || u2.last_name END AS manager_name ,
    tp.total_amount,
    p.display_order_id,
    p.profit * 0.05 AS total_commission,
    p.profit AS profit,
    p.paid_at,
    p.delivered_at
FROM filtered_teams ft
INNER JOIN team_member tm ON tm.team_lead_id = ft.team_lead_id
INNER JOIN profit p ON p.manager_id = tm.team_member_id
INNER JOIN users u ON u.id = p.agent_id
LEFT JOIN users u2 ON u2.id = p.manager_id
INNER JOIN total_price tp ON tp.display_order_id = p.display_order_id
)

"""


def get_team_commissions_report(filters: FilterObject, psycopg2_connection=None):
    if filters.can_read_all:
        query = (
            sql.SQL(
                """
    {common_sql_commissions}
    select team_lead_id as manager_id, name as manager_name, sum(total_amount) sum_total_amount, sum(total_commission) sum_total_commission from top_managers tm
    group by team_lead_id, name
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
    else:
        query = (
            sql.SQL(
                """
    {common_sql_commissions}
    select team_lead_id as manager_id, name as manager_name, sum(total_amount) sum_total_amount, sum(total_commission) sum_total_commission from top_managers tm
    where team_lead_id={user_id}
    group by team_lead_id, name
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


def get_commissions_team_individual_report(filters: FilterObject, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
    {common_sql_commissions}
        select * from  top_managers  where team_lead_id={user_id}
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
    return query
