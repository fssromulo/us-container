# Pip imports
from psycopg2 import sql

# Internal imports
from src.schemas.reports import FilterObject


def get_top_managers(filters: FilterObject, psycopg2_connection=None):
    query = (
        sql.SQL(
            """     WITH agents_month_units AS (
                        SELECT
                            u.first_name || ' ' || u.last_name AS name,
                            EXTRACT(YEAR FROM o.paid_at) AS year,
                            EXTRACT(MONTH FROM o.paid_at) AS month,
                            COUNT(*) AS total_count,
                            ast.manager_id AS manager_id
                        FROM
                            "order" o
                        INNER JOIN
                            line_item li ON o.id = li.order_id
                        INNER JOIN
                            users u ON o.user_id = u.id
                        LEFT JOIN
                            assistant ast ON ast.assistant_id = u.id
                        WHERE
                            o.status IN ('Completed', 'Paid', 'Delivered')
                        GROUP BY
                            name, year, month, u.id, ast.manager_id
                    ),
                    units_per_manager AS (
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
                            name, year, month, u.id
                    ),
                    agregated_units_per_manager AS(
                        SELECT
                            upm.id,
                            upm.name,
                            upm.year,
                            upm.month,
                            upm.total_count + SUM(amu.total_count) AS total_count
                        FROM
                            units_per_manager upm
                        INNER JOIN
                            agents_month_units amu ON upm.id = amu.manager_id
                                                    AND upm.year = amu.year
                                                    AND upm.month = amu.month
                        GROUP BY
                            upm.name, upm.year, upm.month, upm.total_count, upm.id
                    ),
                    max_units_per_manager_and_agents AS (
                        SELECT
                            upm.id,
                            upm.name,
                            upm.year,
                            upm.month,
                            SUM(upm.total_count) AS total_count,
                            ROW_NUMBER() OVER (PARTITION BY upm.id ORDER BY SUM(upm.total_count) DESC) AS row_num
                        FROM
                            agregated_units_per_manager upm
                        GROUP BY
                            upm.name, upm.year, upm.month, upm.total_count, upm.id),
                agents_revenue_plus_shipping AS (
                    SELECT
                        u.id,
                        u.first_name,
                        u.last_name,
                        EXTRACT(MONTH FROM o.paid_at) AS order_month,
                        EXTRACT(YEAR FROM o.paid_at) AS order_year,
                        SUM(li.revenue) AS aggregated_total_revenue,
                        SUM(li.shipping_revenue) AS aggregated_shipping_revenue,
                        ast.manager_id AS manager_id
                    FROM
                        users u
                    JOIN
                        "order" o ON u.id = o.user_id
                    JOIN
                        line_item li ON o.id = li.order_id
                    LEFT JOIN
                        assistant ast ON ast.assistant_id = u.id
                    WHERE
                        o.status IN ('Paid', 'Partially Paid', 'Delivered', 'Completed')
                        AND o.account_id = 1
                        AND u.is_active = TRUE
                    GROUP BY
                        u.id, u.first_name, u.last_name, order_month, order_year, ast.manager_id
                ), agents_fee AS (
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
                        assistant ast ON ast.assistant_id = u.id
                    LEFT JOIN
                        fee f ON o.id = f.order_id
                    WHERE
                        o.status IN ('Paid', 'Partially Paid', 'Delivered', 'Completed')
                        AND o.account_id = 1
                        AND u.is_active = TRUE
                    GROUP BY
                        u.id, u.first_name, u.last_name, order_month, order_year
                ), managers_with_agents AS (
                    SELECT
                        mrps.id,
                        mrps.first_name,
                        mrps.last_name,
                        SUM(arps.aggregated_total_revenue + arps.aggregated_shipping_revenue + af.aggregated_total_fees)
                            + mrps.aggregated_total_revenue + mrps.aggregated_shipping_revenue + mf.aggregated_total_fees as total,
                        mrps.order_year,
                        mrps.order_month
                    FROM
                        agents_revenue_plus_shipping arps
                    INNER JOIN
                        agents_fee af
                        ON arps.id=af.id
                            AND arps.order_month=af.order_month
                            AND arps.order_year=af.order_year
                    INNER JOIN
                        agents_revenue_plus_shipping mrps
                        ON mrps.id=arps.manager_id
                            AND mrps.order_month=arps.order_month
                            AND mrps.order_year=arps.order_year
                    INNER JOIN
                        agents_fee mf
                        ON mf.id=arps.manager_id
                            AND mf.order_month=arps.order_month
                            AND mf.order_year=arps.order_year
                    GROUP BY
                        mrps.id, mrps.first_name, mrps.last_name, mrps.order_year, mrps.order_month,
                        mrps.aggregated_total_revenue, mrps.aggregated_shipping_revenue , mf.aggregated_total_fees
                ), managers_with_rank AS (
                    SELECT
                        m.id,
                        m.first_name,
                        m.last_name,
                        m.order_month,
                        m.order_year,
                        SUM(m.total) AS total,
                        ROW_NUMBER() OVER (PARTITION BY m.id ORDER BY SUM(m.total) DESC) AS ranking
                    FROM
                        managers_with_agents m
                    GROUP BY
                        m.id, m.order_month, m.order_year, m.first_name, m.last_name
                ), agents_revenue_plus_shipping_current AS (
                    SELECT
                        u.id,
                        u.first_name,
                        u.last_name,
                        SUM(li.revenue) AS aggregated_total_revenue,
                        SUM(li.shipping_revenue) AS aggregated_shipping_revenue,
                        ast.manager_id AS manager_id
                    FROM
                        users u
                    JOIN
                        "order" o ON u.id = o.user_id
                    JOIN
                        line_item li ON o.id = li.order_id
                    LEFT JOIN
                        assistant ast ON ast.assistant_id = u.id
                    WHERE
                        o.status IN ('Paid', 'Partially Paid', 'Delivered', 'Completed')
                        AND o.account_id = 1
                        AND u.is_active = TRUE
                        AND o.paid_at BETWEEN  {begin_date} AND {end_date}
                    GROUP BY
                        u.id, u.first_name, u.last_name,  ast.manager_id
                ), agents_fee_current AS (
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
                        assistant ast ON ast.assistant_id = u.id
                    LEFT JOIN
                        fee f ON o.id = f.order_id
                    WHERE
                        o.status IN ('Paid', 'Partially Paid', 'Delivered', 'Completed')
                        AND o.account_id = 1
                        AND u.is_active = TRUE
                        AND o.paid_at BETWEEN  {begin_date} AND {end_date}
                    GROUP BY
                        u.id, u.first_name, u.last_name
                ), managers_with_agents_current AS (
                    SELECT
                        mrps.id,
                        mrps.first_name,
                        mrps.last_name,
                        SUM(arps.aggregated_total_revenue + arps.aggregated_shipping_revenue + af.aggregated_total_fees)
                            + mrps.aggregated_total_revenue + mrps.aggregated_shipping_revenue + mf.aggregated_total_fees as total
                    FROM
                        agents_revenue_plus_shipping_current arps
                    INNER JOIN
                        agents_fee_current af
                        ON arps.id=af.id
                    INNER JOIN
                        agents_revenue_plus_shipping_current mrps
                        ON mrps.id=arps.manager_id
                    INNER JOIN
                        agents_fee_current mf
                        ON mf.id=arps.manager_id
                    GROUP BY
                        mrps.id, mrps.first_name, mrps.last_name,
                        mrps.aggregated_total_revenue, mrps.aggregated_shipping_revenue , mf.aggregated_total_fees),

                    agents_month_units_current AS (
                        SELECT
                            u.first_name || ' ' || u.last_name AS name,
                            COUNT(*) AS total_count,
                            ast.manager_id AS manager_id
                        FROM
                            "order" o
                        INNER JOIN
                            line_item li ON o.id = li.order_id
                        INNER JOIN
                            users u ON o.user_id = u.id
                        LEFT JOIN
                            assistant ast ON ast.assistant_id = u.id
                        WHERE
                            o.status IN ('Completed', 'Paid', 'Delivered')
                            AND o.paid_at BETWEEN  {begin_date} AND {end_date}
                        GROUP BY
                            name, u.id, ast.manager_id
                    ),
                    units_per_manager_current AS (
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
                            name, u.id
                    ),
                    agregated_units_per_manager_current AS(
                        SELECT
                            upm.id,
                            upm.name,
                            upm.total_count + SUM(amu.total_count) AS total_count
                        FROM
                            units_per_manager_current upm
                        INNER JOIN
                            agents_month_units_current amu ON upm.id = amu.manager_id
                        GROUP BY
                            upm.name, upm.total_count, upm.id
                    )

                    SELECT
                        m.first_name || ' ' || m.last_name AS name,
                        m.order_month as highest_sales_month,
                        m.order_year as highest_sales_year,
                        m.total as highest_sales,
                        a.month as max_units_sold_month,
                        a.year as max_units_sold_year,
                        a.total_count as max_units_sold,
                        mwac.total AS current_sales,
                        aupmc.total_count as current_units
                    FROM
                        managers_with_rank m
                    INNER JOIN
                        max_units_per_manager_and_agents a ON a.id = m.id
                    INNER JOIN
                        managers_with_agents_current mwac on mwac.id = m.id
                    INNER JOIN
                        agregated_units_per_manager_current aupmc on aupmc.id = m.id
                    WHERE
                        ranking = 1 and row_num=1
                    ORDER BY
                        mwac.total DESC;

                        """
        )
        .format(
            begin_date=sql.Literal(filters.begin_date),
            end_date=sql.Literal(filters.end_date),
        )
        .as_string(psycopg2_connection)
    )
    return query
