# Pip imports
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def get_num_orders_per_month(filters: FilterObject, psycopg2_connection=None):
    product_types_list = create_sql_composable(filters.productTypes, True)
    statuses_list = create_sql_composable(filters.statuses)
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
    elif product_types_all:
        sqlProductTypes = sql.SQL("")

    sqlStates = sql.SQL("")
    if filters.states and not states_all:
        sqlStates = sql.SQL(
            """
            AND li.product_state IN {states_list}"""
        ).format(states_list=states_list)
    elif states_all:
        sqlStates = sql.SQL("")

    sqlStatuses = sql.SQL("")
    if filters.statuses:
        sqlStatuses = sql.SQL(
            """
            AND o.status in {statuses_list}"""
        ).format(statuses_list=statuses_list)

    if product_types_all:
        query = (
            sql.SQL(
                """
                        SELECT
                            EXTRACT(YEAR FROM o.created_at) AS year,
                            EXTRACT(MONTH FROM o.created_at) AS month,
                            count(*) AS count
                        FROM
                            "order" o
                            INNER JOIN line_item li on o.id = li.order_id
                        WHERE
                            o.created_at BETWEEN  {begin_date}
                                AND {end_date}
                            {sqlStatuses}
                            {sqlStates}
                            AND o.account_id={account_id}
                        GROUP BY
                            year, month
                        ORDER BY year, month ASC
                        """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
                sqlStates=sqlStates,
                sqlStatuses=sqlStatuses,
            )
            .as_string(psycopg2_connection)
        )
    else:

        query = (
            sql.SQL(
                """
                        SELECT
                            EXTRACT(YEAR FROM o.created_at) AS year,
                            EXTRACT(MONTH FROM o.created_at) AS month,
                            count(*) AS count
                        FROM
                            "order" o
                            INNER JOIN line_item li on o.id = li.order_id
                            INNER JOIN container_inventory i ON li.inventory_id = i.id
                            INNER JOIN container_product cpn ON i.product_id::VARCHAR = cpn.id::VARCHAR
                        WHERE
                            o.created_at BETWEEN  {begin_date}
                                AND {end_date}
                            {sqlProductTypes}
                            {sqlStatuses}
                            {sqlStates}
                            AND o.account_id={account_id}
                        GROUP BY
                            year, month
                        ORDER BY year, month ASC
                        """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
                sqlStates=sqlStates,
                sqlStatuses=sqlStatuses,
                sqlProductTypes=sqlProductTypes,
            )
            .as_string(psycopg2_connection)
        )
    return query
