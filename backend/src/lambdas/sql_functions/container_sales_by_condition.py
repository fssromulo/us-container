# Pip imports
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def get_container_sales_by_condition(filters: FilterObject = None, psycopg2_connection=None):
    product_types_list = create_sql_composable(filters.productTypes, True)
    product_types_all = True if filters.productTypes[0] == 'All' else False

    if product_types_all:
        query = (
            sql.SQL(
                """
                    SELECT
                        oa.state as state,
                        SUM(CASE WHEN li.condition = 'Used' THEN 1 ELSE 0 END) AS total_containers_used,
                        SUM(CASE WHEN li.condition = 'One-Trip' THEN 1 ELSE 0 END) AS total_containers_one_trip
                    FROM
                        "order" o
                    INNER JOIN order_address oa ON o.address_id = oa.id
                    INNER JOIN line_item li on o.id = li.order_id
                    WHERE
                        o.status <> 'Invoiced' AND o.status <> 'Expired' AND o.paid_at BETWEEN  {begin_date}
                            AND {end_date}
                             AND o.account_id = {account_id}
                    GROUP BY
                        oa.state
                    ORDER BY total_containers_used DESC
                    """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
            )
            .as_string(psycopg2_connection)
        )
    else:
        query = (
            sql.SQL(
                """
                    SELECT
                        oa.state as state,
                        SUM(CASE WHEN li.condition = 'Used' THEN 1 ELSE 0 END) AS total_containers_used,
                        SUM(CASE WHEN li.condition = 'One-Trip' THEN 1 ELSE 0 END) AS total_containers_one_trip
                    FROM
                        "order" o
                    INNER JOIN order_address oa ON o.address_id = oa.id
                    INNER JOIN line_item li on o.id = li.order_id
                    INNER JOIN container_inventory i ON li.inventory_id = i.id
                    INNER JOIN container_product cpn ON i.product_id::VARCHAR = cpn.id::VARCHAR
                    WHERE
                        o.status <> 'Invoiced' AND o.status <> 'Expired' AND o.paid_at BETWEEN  {begin_date}
                            AND {end_date}
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
                        END IN  {product_types_list}
                             AND o.account_id = {account_id}
                    GROUP BY
                        oa.state
                    ORDER BY total_containers_used DESC
                    """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
                product_types_list=product_types_list,
            )
            .as_string(psycopg2_connection)
        )
    return query
