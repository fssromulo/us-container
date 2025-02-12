# Pip imports
from psycopg2 import sql

# Internal imports
from src.schemas.reports import FilterObject


def get_top_agents(filters: FilterObject, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
        WITH agents_month_units AS (
            SELECT
                u.id,
                u.first_name || ' ' || u.last_name AS name,
                EXTRACT(YEAR FROM o.paid_at) AS year,
                EXTRACT(MONTH FROM o.paid_at) AS month,
                COUNT(*) AS total_count
            FROM
                "order" o
            INNER JOIN
                line_item li ON o.id = li.order_id
            INNER JOIN
                users u ON o.user_id = u.id
            WHERE
                o.status IN ('Completed', 'Paid', 'Delivered')
            GROUP BY
                u.id, u.first_name, u.last_name, year, month
        ),
        max_units_per_agent AS (
            SELECT
                amu.id,
                amu.name,
                amu.year,
                amu.month,
                amu.total_count AS total_count,
                ROW_NUMBER() OVER (PARTITION BY amu.id ORDER BY amu.total_count DESC) AS row_num
            FROM
                agents_month_units amu
            GROUP BY
                amu.id, amu.name, amu.total_count, amu.year, amu.month
        ),
        agents_revenue_plus_shipping AS (
            SELECT
                u.id,
                u.first_name,
                u.last_name,
                EXTRACT(MONTH FROM o.paid_at) AS order_month,
                EXTRACT(YEAR FROM o.paid_at) AS order_year,
                SUM(li.revenue) AS aggregated_total_revenue,
                SUM(li.shipping_revenue) AS aggregated_shipping_revenue
            FROM
                users u
            JOIN
                "order" o ON u.id = o.user_id
            JOIN
                line_item li ON o.id = li.order_id
            WHERE
                o.status IN ('Paid', 'Partially Paid', 'Delivered', 'Completed')
                AND o.account_id = 1
                AND u.is_active = TRUE
            GROUP BY
                u.id, u.first_name, u.last_name, order_month, order_year
        ),
        agents_fee AS (
            SELECT
                u.id,
                u.first_name,
                u.last_name,
                EXTRACT(MONTH FROM o.paid_at) AS order_month,
                EXTRACT(YEAR FROM o.paid_at) AS order_year,
                SUM(COALESCE(f.fee_amount, 0)) AS aggregated_total_fees
            FROM
                users u
            JOIN
                "order" o ON u.id = o.user_id
            JOIN
                line_item li ON o.id = li.order_id
            LEFT JOIN
                fee f ON o.id = f.order_id
            WHERE
                o.status IN ('Paid', 'Partially Paid', 'Delivered', 'Completed')
                AND o.account_id = 1
                AND u.is_active = TRUE
            GROUP BY
                u.id, u.first_name, u.last_name, order_month, order_year
        ),
        agent_aggregated AS (
            SELECT
                arps.id,
                arps.first_name,
                arps.last_name,
                arps.aggregated_total_revenue + arps.aggregated_shipping_revenue + af.aggregated_total_fees AS total,
                arps.order_year,
                arps.order_month
            FROM
                agents_revenue_plus_shipping arps
            INNER JOIN
                agents_fee af ON arps.id = af.id
                AND arps.order_month = af.order_month
                AND arps.order_year = af.order_year
        ),
        agents_with_rank AS (
            SELECT
                m.id,
                m.first_name,
                m.last_name,
                SUM(total) AS total,
                m.order_year,
                m.order_month,
                ROW_NUMBER() OVER (PARTITION BY m.id ORDER BY SUM(m.total) DESC) AS ranking
            FROM
                agent_aggregated m
            GROUP BY
                m.id, m.first_name, m.last_name, m.order_year, m.order_month
        ), agents_revenue_plus_shipping_current AS (
            SELECT
                u.id,
                u.first_name,
                u.last_name,
                SUM(li.revenue) AS aggregated_total_revenue,
                SUM(li.shipping_revenue) AS aggregated_shipping_revenue
            FROM
                users u
            JOIN
                "order" o ON u.id = o.user_id
            JOIN
                line_item li ON o.id = li.order_id
            WHERE
                o.status IN ('Paid', 'Partially Paid', 'Delivered', 'Completed')
                AND o.account_id = 1
                AND u.is_active = TRUE
                AND o.paid_at BETWEEN  {begin_date} AND {end_date}
            GROUP BY u.id, u.first_name, u.last_name
        ),
        agents_fee_current AS (
            SELECT
                u.id,
                u.first_name,
                u.last_name,
                SUM(COALESCE(f.fee_amount, 0)) AS aggregated_total_fees
            FROM
                users u
            JOIN
                "order" o ON u.id = o.user_id
            JOIN
                line_item li ON o.id = li.order_id
            LEFT JOIN
                fee f ON o.id = f.order_id
            WHERE
                o.status IN ('Paid', 'Partially Paid', 'Delivered', 'Completed')
                AND o.account_id = 1
                AND u.is_active = TRUE
                AND o.paid_at BETWEEN  {begin_date} AND {end_date}
            GROUP BY u.id, u.first_name, u.last_name
        ),
        agent_aggregated_current AS (
            SELECT
                arps.id,
                arps.first_name,
                arps.last_name,
                arps.aggregated_total_revenue + arps.aggregated_shipping_revenue + af.aggregated_total_fees AS total
            FROM
                agents_revenue_plus_shipping_current arps
            INNER JOIN
                agents_fee_current af ON arps.id = af.id
        ), agents_month_units_current AS (
            SELECT
                u.id,
                u.first_name || ' ' || u.last_name AS name,
                COUNT(*) AS total_count
            FROM
                "order" o
            INNER JOIN
                line_item li ON o.id = li.order_id
            INNER JOIN
                users u ON o.user_id = u.id
            WHERE
                o.status IN ('Completed', 'Paid', 'Delivered')
                AND o.paid_at BETWEEN  {begin_date} AND {end_date}
            GROUP BY
                u.id, u.first_name, u.last_name
        )
        SELECT
            m.first_name || ' ' || m.last_name AS name,
            m.order_month AS highest_sales_month,
            m.order_year AS highest_sales_year,
            m.total AS highest_sales,
            a.month AS max_units_sold_month,
            a.year AS max_units_sold_year,
            a.total_count AS max_units_sold,
            aac.total AS current_sales,
            amuc.total_count AS current_units
        FROM
            agents_with_rank m
        INNER JOIN
            max_units_per_agent a ON a.id = m.id
        INNER JOIN
            agent_aggregated_current aac ON aac.id=m.id
        INNER JOIN
            agents_month_units_current amuc ON amuc.id=m.id
        WHERE
            ranking = 1 AND row_num = 1
        ORDER BY
            a.total_count DESC;


        """
        )
        .format(
            begin_date=sql.Literal(filters.begin_date),
            end_date=sql.Literal(filters.end_date),
        )
        .as_string(psycopg2_connection)
    )
    return query
