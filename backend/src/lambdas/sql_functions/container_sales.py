# Pip imports
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def get_container_sales(filters: FilterObject = None, psycopg2_connection=None):
    conditions_list = create_sql_composable(filters.conditions)
    product_types_list = create_sql_composable(filters.productTypes, True)
    product_types_all = True if filters.productTypes[0] == 'All' else False

    qStr = [sql.SQL("")]
    if filters.productTypes and not product_types_all:
        qStr += [
            sql.SQL(
                """
            AND cpn.container_size || ' ' || cpn.condition ||
                        CASE
                            WHEN EXISTS (
                                SELECT *
                                FROM container_product_attribute cpa
                                INNER JOIN container_attribute ca ON ca.id = cpa.container_attribute_id
                                WHERE ca.name = ' Standard' AND container_product_id::VARCHAR = cpn.id::VARCHAR
                            ) THEN 'Standard'
                            ELSE ''
                        END ||
                        CASE
                            WHEN EXISTS (
                                SELECT *
                                FROM container_product_attribute cpa
                                INNER JOIN container_attribute ca ON ca.id = cpa.container_attribute_id
                                WHERE ca.name = ' High Cube' AND container_product_id::VARCHAR = cpn.id::VARCHAR
                            ) THEN 'High Cube'
                            ELSE ''
                        END ||
                        CASE
                            WHEN EXISTS (
                                SELECT *
                                FROM container_product_attribute cpa
                                INNER JOIN container_attribute ca ON ca.id = cpa.container_attribute_id
                                WHERE ca.name = ' Double Door' AND container_product_id::VARCHAR = cpn.id::VARCHAR
                            ) THEN 'Double Door'
                            ELSE ''
                        END IN  """
            ),
            product_types_list,
        ]

    if filters.conditions:
        qStr += [
            sql.SQL(
                """
            AND li.condition IN  """
            ),
            conditions_list,
        ]

    if product_types_all:
        query = (
            sql.SQL(
                """
                WITH total_queries AS (
                    SELECT COUNT(*) AS total_count
                    FROM "order" o
                    INNER JOIN line_item li on o.id = li.order_id
                    WHERE LOWER(o.status) IN ('paid', 'partially paid', 'completed', 'delivered')
                    AND o.paid_at BETWEEN  {begin_date}
                        AND {end_date}
                        AND o.account_id={account_id}
                ) , total_orders AS (
                    SELECT
                        li.product_state as state,
                        o.id
                    FROM
                        "order" o
                    INNER JOIN line_item li on o.id = li.order_id
                    WHERE
                            o.paid_at BETWEEN  {begin_date}
                            AND {end_date}
                            AND o.account_id={account_id}
                            {qStr}
                            AND LOWER(o.status) IN ('paid', 'partially paid', 'completed', 'delivered')
                    GROUP BY
                        li.product_state, o.id
                ), total_orders_count AS (
                    SELECT count(*) as count, state  FROM total_orders
                    GROUP BY state
                )
                SELECT
                    li.product_state as state,
                    count(*) * 100.0 / tq.total_count AS percent_total_units,
                    count(*) AS total_units,
                    toc.count as total_orders
                FROM
                    "order" o
                INNER JOIN line_item li on o.id = li.order_id
                CROSS JOIN total_queries tq
                INNER JOIN total_orders_count toc
                ON li.product_state = toc.state
                WHERE
                        o.paid_at BETWEEN  {begin_date}
                        AND {end_date}
                        AND o.account_id={account_id}
                        {qStr}
                        AND LOWER(o.status) IN ('paid', 'partially paid', 'completed', 'delivered')
                GROUP BY
                    li.product_state, tq.total_count, toc.count;
                """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
                qStr=sql.Composed(qStr),
            )
            .as_string(psycopg2_connection)
        )
    else:
        query = (
            sql.SQL(
                """
                WITH total_queries AS (
                    SELECT COUNT(*) AS total_count
                    FROM "order" o
                    INNER JOIN line_item li on o.id = li.order_id
                    WHERE LOWER(o.status) IN ('paid', 'partially paid', 'completed', 'delivered')
                    AND o.paid_at BETWEEN  {begin_date}
                        AND {end_date}
                        AND o.account_id={account_id}
                ), total_orders AS (
                    SELECT
                        li.product_state as state,
                        o.id
                    FROM
                        "order" o
                    INNER JOIN line_item li on o.id = li.order_id
                    INNER JOIN container_inventory i ON li.inventory_id = i.id
                    INNER JOIN container_product cpn ON i.product_id::VARCHAR = cpn.id::VARCHAR
                    WHERE
                            o.paid_at BETWEEN  {begin_date}
                            AND {end_date}
                            AND o.account_id={account_id}
                            {qStr}
                            AND LOWER(o.status) IN ('paid', 'partially paid', 'completed', 'delivered')
                    GROUP BY
                        li.product_state, o.id
                ), total_orders_count AS (
                    SELECT count(*) as count, state  FROM total_orders
                    GROUP BY state
                )
                SELECT
                    li.product_state as state,
                    count(*) * 100.0 / tq.total_count AS percent_total_units,
                    count(*) AS total_units,
                    toc.count as total_orders
                FROM
                    "order" o
                INNER JOIN line_item li on o.id = li.order_id
                INNER JOIN container_inventory i ON li.inventory_id = i.id
                INNER JOIN container_product cpn ON i.product_id::VARCHAR = cpn.id::VARCHAR
                CROSS JOIN total_queries tq
                INNER JOIN total_orders_count toc
                ON li.product_state = toc.state
                WHERE
                        o.paid_at BETWEEN  {begin_date}
                        AND {end_date}
                        AND o.account_id={account_id}
                        {qStr}
                        AND LOWER(o.status) IN ('paid', 'partially paid', 'completed', 'delivered')
                GROUP BY
                    li.product_state, tq.total_count, toc.count;
                """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
                qStr=sql.Composed(qStr),
            )
            .as_string(psycopg2_connection)
        )

    return query
