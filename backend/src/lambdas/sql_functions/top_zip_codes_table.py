# Pip imports
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def get_top_zip_codes_table(filters: FilterObject, psycopg2_connection=None):
    statuses_list = create_sql_composable(filters.statuses)

    if not filters.statuses:
        query = (
            sql.SQL(
                """
                        WITH orders_zip_codes AS (
                            SELECT
                                oa.zip AS zip_code,
                                o.id
                            FROM
                            "order" o
                            INNER JOIN order_address oa ON o.address_id = oa.id
                            WHERE
                            o.created_at BETWEEN  {begin_date}
                                AND {end_date}
                                AND o.account_id={account_id}
                            GROUP BY oa.zip, o.id
                        ), orders_zip_codes_count AS (
                            SELECT
                                zip_code,
                                count(*) AS count
                            FROM orders_zip_codes
                            GROUP BY zip_code
                        )
                        SELECT
                            oa.zip AS zip_code,
                            count(*) AS count,
                            ozic.count AS count_orders
                        FROM
                            "order" o
                        INNER JOIN order_address oa ON o.address_id = oa.id
                        INNER JOIN line_item li on o.id = li.order_id
                        INNER JOIN inventory i on li.inventory_id = i.id
                        INNER JOIN orders_zip_codes_count ozic ON oa.zip=ozic.zip_code
                        WHERE
                            o.created_at BETWEEN  {begin_date}
                                AND {end_date}
                                AND o.account_id={account_id}
                        GROUP BY
                            zip_code
                        ORDER BY count DESC
                        LIMIT 50
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
                        WITH orders_zip_codes AS (
                            SELECT
                                oa.zip AS zip_code,
                                o.id
                            FROM
                            "order" o
                            INNER JOIN order_address oa ON o.address_id = oa.id
                            WHERE
                            o.created_at BETWEEN  {begin_date}
                                AND {end_date}
                                AND o.account_id={account_id}
                            GROUP BY oa.zip, o.id
                        ), orders_zip_codes_count AS (
                            SELECT
                                zip_code,
                                count(*) AS count
                            FROM orders_zip_codes
                            GROUP BY zip_code
                        )
                        SELECT
                            oa.zip AS zip_code,
                            count(*) AS count,
                            ozic.count AS count_orders
                        FROM
                            "order" o
                        INNER JOIN order_address oa ON o.address_id = oa.id
                        INNER JOIN line_item li on o.id = li.order_id
                        INNER JOIN orders_zip_codes_count ozic ON oa.zip=ozic.zip_code
                        WHERE
                            o.created_at BETWEEN  {begin_date}
                                AND {end_date}
                                AND o.status in {statuses_list}
                            AND o.account_id={account_id}
                        GROUP BY
                            oa.zip, ozic.count
                        ORDER BY count DESC
                        LIMIT 50
                        """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
                statuses_list=statuses_list,
            )
            .as_string(psycopg2_connection)
        )

    return query
