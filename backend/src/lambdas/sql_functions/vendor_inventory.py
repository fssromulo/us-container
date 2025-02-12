# Pip imports
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def get_inventory_report(filters: FilterObject, psycopg2_connection=None):
    vendor_types = create_sql_composable(filters.vendors)
    vendor_types_all = True if filters.vendors[0] == 'All' else False

    if vendor_types_all:
        query = (
                sql.SQL(
                    """
                            SELECT
                                v.name,
                                ci.container_release_number,
                                ci.container_number,
                                ci.created_at,
                                ci.invoice_number,
                                ci.total_cost,
                                cp.container_size
                            FROM
                                container_inventory ci
                                INNER JOIN vendor v on ci.vendor_id=v.id
                                INNER JOIN container_product cp on cp.id::VARCHAR=ci.product_id::VARCHAR
                            WHERE
                                ci.created_at BETWEEN  {begin_date}
                                    AND {end_date}
                                AND ci.account_id={account_id}
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
                                v.name,
                                ci.container_release_number,
                                ci.container_number,
                                ci.created_at,
                                ci.invoice_number,
                                ci.total_cost,
                                cp.container_size
                            FROM
                                container_inventory ci
                                INNER JOIN vendor v on ci.vendor_id=v.id
                                INNER JOIN container_product cp on cp.id::VARCHAR=ci.product_id::VARCHAR
                            WHERE
                                ci.created_at BETWEEN  {begin_date}
                                    AND {end_date}
                                AND v.name in {vendor_types}
                                AND ci.account_id={account_id}
                            """
                )
                .format(
                    begin_date=sql.Literal(filters.begin_date),
                    end_date=sql.Literal(filters.end_date),
                    account_id=sql.Literal(filters.account_id),
                    vendor_types=vendor_types
                )
                .as_string(psycopg2_connection)
            )
    return query