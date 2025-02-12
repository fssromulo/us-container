# Pip imports
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def get_orders_by_payment_type(filters: FilterObject, psycopg2_connection=None):
    product_types_list = create_sql_composable(filters.productTypes, True)
    states_list = create_sql_composable(filters.states)
    states_all = True if filters.states[0] == 'All' else False
    product_types_all = True if filters.productTypes[0] == 'All' else False

    sqlProductTypes = sql.SQL("")
    if filters.productTypes and not product_types_all:
        sqlProductTypes = sql.SQL(
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
                        END IN  {product_types_list}"""
        ).format(product_types_list=product_types_list)

    sqlStates = sql.SQL("")
    if filters.states and not states_all:
        sqlStates = sql.SQL(
            """
            AND li.product_state IN {states_list}"""
        ).format(states_list=states_list)

    if product_types_all:
        query = (
            sql.SQL(
                """     WITH orders_payment_type AS (
                            SELECT
                                tt.payment_type AS payment_type
                            FROM
                                "order" o
                            INNER JOIN transaction_type tt
                            ON tt.order_id = o.id
                            WHERE
                                o.created_at BETWEEN  {begin_date}
                                    AND {end_date}
                                    {sqlStates}
                                    AND o.account_id={account_id}
                                AND tt.payment_type IS NOT NULL
                            GROUP BY
                                tt.payment_type, o.id
                            UNION ALL
                            SELECT
                                tt.payment_type AS payment_type
                            FROM
                                "order" o
                            INNER JOIN rent_period rp on o.id = rp.order_id
                            INNER JOIN transaction_type tt
                            ON tt.rent_period_id = rp.id
                            WHERE
                                o.created_at BETWEEN  {begin_date}
                                    AND {end_date}
                                    {sqlStates}
                                    AND o.account_id={account_id}
                                AND tt.payment_type IS NOT NULL
                            GROUP BY
                                tt.payment_type, o.id
                        ) SELECT payment_type, COUNT(*) as count
                        FROM orders_payment_type
                        GROUP BY payment_type
                        """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
                sqlStates=sqlStates,
                sqlProductTypes=sqlProductTypes,
            )
            .as_string(psycopg2_connection)
        )
    else:
        query = (
            sql.SQL(
                """
                    WITH orders_payment_type AS (
                            SELECT
                                tt.payment_type AS payment_type
                            FROM
                                "order" o
                            INNER JOIN transaction_type tt
                            ON tt.order_id = o.id

                            INNER JOIN line_item li on o.id = li.order_id
                            INNER JOIN container_inventory i ON li.inventory_id = i.id
                            INNER JOIN container_product cpn ON i.product_id::VARCHAR = cpn.id::VARCHAR
                            WHERE
                                o.created_at BETWEEN  {begin_date}
                                    AND {end_date}
                                    {sqlStates}
                                    {sqlProductTypes}
                                    AND o.account_id={account_id}
                                AND tt.payment_type IS NOT NULL
                            GROUP BY
                                tt.payment_type, o.id
                            UNION ALL
                            SELECT
                                tt.payment_type AS payment_type
                            FROM
                                "order" o
                            INNER JOIN rent_period rp on o.id = rp.order_id
                            INNER JOIN line_item li on o.id = li.order_id
                            INNER JOIN container_inventory i ON li.inventory_id = i.id
                            INNER JOIN container_product cpn ON i.product_id::VARCHAR = cpn.id::VARCHAR
                            INNER JOIN transaction_type tt
                            ON tt.rent_period_id = rp.id
                            WHERE
                                o.created_at BETWEEN  {begin_date}
                                    AND {end_date}
                                    {sqlStates}
                                    {sqlProductTypes}
                                    AND o.account_id={account_id}
                                AND tt.payment_type IS NOT NULL
                            GROUP BY
                                tt.payment_type, o.id
                        ) SELECT payment_type, COUNT(*) as count
                        FROM orders_payment_type
                        GROUP BY payment_type
                        """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
                sqlStates=sqlStates,
                sqlProductTypes=sqlProductTypes,
            )
            .as_string(psycopg2_connection)
        )
    return query
